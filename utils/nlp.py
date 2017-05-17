from __future__ import division
import nltk
import string
from collections import defaultdict
from nltk import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet as wn
import numpy as np
from pattern.web import Twitter, hashtags
import requests
from bs4 import BeautifulSoup
import sys
import logging

try:
    import grequests
except ImportError:
    pass

# Levenstein
from nltk.metrics import *
# Stopwords
from nltk.corpus import stopwords
# To use the stop words list:
stops = set(stopwords.words("english"))

Stemmer = nltk.PorterStemmer()
Lemmatizer = nltk.WordNetLemmatizer()

import corpus


def sentence_tokenizer(string):
    # Break up a text into sentences
    import nltk.data
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentence_list = sent_detector.tokenize(string.strip())
    return sentence_list

# Handling words as simple strings:

def sieve(string_list):
    # Remove extras from a list
    string_list.sort(key=lambda s: len(s), reverse=True)
    out = []
    for s in string_list:
        if not any([s in o for o in out]):
            out.append(s)
    return out

def crossBagger(X,Y):
    # Turn a two lists into one, with no extras.
    words = []
    for i in X:
        if i in Y:
            words.append(i)
    words = sieve(words)
    return words

# Handling words via their part of speach.

def posScraper(string, X):
    # Scrape all the words from a string, ascociated to one POS.
    text = nltk.pos_tag(word_tokenize(string))
    pos = []
    for i in text:
        if i[1].startswith(X):
            pos.append(i[0])
    return pos

def phraseScraper(string, POS, window):
    pos_list = posScraper(string, POS)
    list = string.split()
    pos_phrases = []
    for i,item in enumerate(list):
        if item in pos_list:
            phrase = list[i-window], list[i], list[i+window]
            pos_phrases.append(phrase)
    return pos_phrases

def nounPhrases(string):
    '''
    Breaks up a sentence into chunks of nouns.
    For example, ['The Blue School'], rather than ['the', 'blue', 'school']
    '''
    grammar = r"""
        NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
        {<NNP>+}                # chunk sequences of proper nouns
        {<NN>+}                 # chunk consecutive nouns
        """

    cp = nltk.RegexpParser(grammar)
    tagged_sent = nltk.pos_tag(string.split())
    parsed_sent = cp.parse(tagged_sent)
    for subtree in parsed_sent.subtrees():
      if subtree.label() == 'NP':
        yield ' '.join(word for word, tag in subtree.leaves())

def nounPropper(string):
    '''
    Tokenises the propper nouns.
    '''
    grammar = r"""
        NNP: {<DT|PP\$>?<JJ>*<NNP>}
        {<NNP>+}
        """
    cp = nltk.RegexpParser(grammar)
    tagged_sent = nltk.pos_tag(string.split())
    parsed_sent = cp.parse(tagged_sent)
    for subtree in parsed_sent.subtrees():
      if subtree.label() == 'NNP':
        yield ' '.join(word for word, tag in subtree.leaves())


def propperNounList(string):
    # takes in a plain string and gives back a list of the propper nouns.
    sent_tokenized = word_tokenize(string)
    pn_list = []
    for npstr in nounPropper(string):
         pn_list.append(npstr)
    return pn_list


def nounList(string):
    tokens = nltk.word_tokenize(string)
    tagged = nltk.pos_tag(tokens)
    nouns = [word for word,pos in tagged \
    	if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
    return nouns

# Handling via their characters:

def questionList(list):
    # Turn a text into a list of question pairs
    questions_answers = []
    for i in list:
        if "?" in i:
            pair = []
            pair.append(i)
            pair.append(i + 1)
            questions_answers.append(tuple(pair))
    return questions_answers

def levenstein(query, dataset):
    '''
    Compare the levenstein distance between the words in a sentence, and a dataset of keywords.
    To use:
    query = "I want to go and play football"
    dataset = corpus.load("data/keywords_dictionary.json")
    returns a tuple of score and ID
    '''
    for l in dataset:
        score = (0,"")
        for w1 in l[2]:
            for w2 in query:
                x = edit_distance(w1, w2)
                if x > score[0]:
                    score = (x, l[1])
    return


def levensteinWord(query, dataset):
    '''
    Compare the levenstein distance between the words in a sentence, and a dataset of keywords.
    To use:
    query = "I want to go and play football"
    dataset = "play"
    returns the max score
    '''
    similarity = 0.0
    for w1 in dataset:
        for w2 in query:
            x = edit_distance(w1, w2)
            bigger = max(len(w1),len(w2))
            pct = (bigger - x)/bigger
            if pct > similarity:
                similarity = pct
    return similarity

def smith_waterman(seq1, seq2, match=3, mismatch=-1, insertion=-1, deletion=-1, normalize=1):
    '''Temporarily borrowed from stolen from http://climberg.de/page/smith-waterman-distance-for-feature-extraction-in-nlp/'''
    # switch sequences, so that seq1 is the longer sequence to search for seq2
    if len(seq2) > len(seq1): seq1, seq2 = seq2, seq1
    # create the distance matrix
    mat = np.zeros((len(seq2) + 1, len(seq1) + 1))
    # iterate over the matrix column wise
    for i in range(1, mat.shape[0]):
        # iterate over the matrix row wise
        for j in range(1, mat.shape[1]):
            # set the current matrix element with the maximum of 4 different cases
            mat[i, j] = max(
                # negative values are not allowed
                0,
                # if previous character matches increase the score by match, else decrease it by mismatch
                mat[i - 1, j - 1] + (match if seq1[j - 1] == seq2[i - 1] else mismatch),
                # one character is missing in seq2, so decrease the score by deletion
                mat[i - 1, j] + deletion,
                # one additional character is in seq2, so decrease the scare by insertion
                mat[i, j - 1] + insertion
            )
    # the maximum of mat is now the score, which is returned raw or normalized (with a range of 0-1)
    return np.max(mat) / (len(seq2) * match) if normalize else np.max(mat)

def getBestMatch(statement,movies):
    '''
    Get the movie title with the highest Smith-Waterman similarity compared to the statement
    '''
    scores = [(smith_waterman(statement,movie),movie) for movie in movies]
    return max(scores)[1]


def jaccard_sim(x,y):
    """
    Compute Jaccard similarity between two bags of words
    """
    return len(set(x) & set(y)) / float(len(set(x) | set(y)))

def movie_comparison(statement, other_statement, data='data/keywords_dictionary.json'):
    '''
    Compare two statements based on the movie titles:
        Pull movie titles from the statement
        Get IMDB keywords for those movies
        Compare these with Jaccard similarity
    '''
    # TODO: Extract IMDB keywords from database (database needed)
    # For testing purposes: read in keywords from top 250 movies in JSON format
    #                       Title is at first index, ID at second, list of keywords at third
    keywords = defaultdict(list,{movie[0]: movie[2] for movie in corpus.load(data)})

    # Find best match of movie title in statement
    title_1 = getBestMatch(statement,keywords.keys())
    title_2 = getBestMatch(other_statement,keywords.keys())
    print title_1, 'extracted from', statement
    print title_2, 'extracted from', other_statement

    # Extract keywords for both titles
    keywords_1 = keywords[title_1]
    keywords_2 = keywords[title_2]

    return jaccard_sim(keywords_1,keywords_2)

# Twitter crawler for Training.

# if grequests not available, fall back to synchronous requests
if 'grequests' in sys.modules:
    def tweetCrawl(search_term, cnt):
        '''
        Search Twitter for a term and return (cnt) number of tweets as a list of tuples of tweet and first response.
        '''
        def handleResponse(tweet, pairs, response):
            replies = [i.get_text() for i in BeautifulSoup(response.content, 'html.parser').select('.tweet-text')]
            
            if len(replies) >= 2:
                pairs.append((tweet, replies[1]))

        def handleException(request, exception):
            raise exception

        twitter = Twitter(language='en')
        tweets = twitter.search(search_term, cached=False, count=cnt)

        pairs = []

        asyncRequests = (grequests.get(tweet['url'],
            callback=lambda response, **kwargs: handleResponse(tweet, pairs, response)) for tweet in tweets)

        grequests.map(asyncRequests, exception_handler=handleException)

        return pairs
else:
    def tweetCrawl(search_term, cnt):
        '''
        Search Twitter for a term and return (cnt) number of tweets as a list of tuples of tweet and first response.
        '''
        logging.warning("Calling tweetCrawl without grequests installed, which handles requests asynchronously.")
        twitter = Twitter(language='en')
        tweets = twitter.search(search_term, cached=False, count=cnt)
        pairs = []
        for t in tweets:
            try:
                replies = [i.get_text() for i in BeautifulSoup(requests.get(t['url']).content, 'html.parser').select(".tweet-text")]
                pairs.append((t['text'],replies[1]))
            except IndexError:
                pass
        return pairs

## To use tweetCrawl
# search_term = "What movie should i watch?"
# cnt =999
# tweets = tweetCrawl(search_term, cnt)


def positives():
    positives = ['yes','ok','sure','positive','affirmative']
    #Find synonyms
    synonyms = set(positives)
    for word in positives:
        for synonym in wn.synsets(word):
            for lemma in synonym.lemma_names():
                synonyms.add(lemma)

    #remove duplicates
    positives = list(synonyms)
    return positives

def isQuestion(message):
    """
    Check if 'message' is a question.
    """
    # Very basic for now, should become more intelligent.
    if '?' in message:
        return True
    return False


def cleanString(mystring):
    return mystring.lower().translate(None, string.punctuation)

def stem(string):
    """
    Lemmatize and stem string.
    """
    return Stemmer.stem(Lemmatizer.lemmatize(string))

if __name__=='__main__':
    # Just for testing
    # print movie_comparison('I thought The Godfather was amazing!', 'I loved The Godfather a lot!')
    print positives()
