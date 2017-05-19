from __future__ import print_function, division
import nltk
import numpy as np
import spacy
import string

from scipy.spatial import distance as dist

def sentence2vec(sentence, nlp, stopwords):
    '''
        Naively represent a sentence by the average of its word vectors
    '''
    # Convert to lowercase, remove punctuation and stopwords
    sentence = u' '.join(filter(lambda word: word not in stopwords, sentence.lower().translate(None,string.punctuation).split()))
    # Tokenise what's left
    tokens = nlp(sentence)
    num_tokens = len(tokens)
    # Initialise by the null-vector
    vec = np.zeros([num_tokens,300])
    # For every token in the sentence
    for token in nlp(sentence):
        # Add it to the intermediary vector
        vec += token.vector
    return vec.mean(axis=0)

def similarity(u,v,f=dist.cosine):
    '''
        Compute the similarity between two vectors u and v
        as '1-f(u,v)' for some distance measure f
    '''
    return 1 - f(u,v)


if __name__=='__main__':
    # Load spacy
    print('Loading SpaCy...')
    nlp = spacy.load('en')
    
    # Load stopwords
    print('Loading stopwords from NLTK...')
    stopwords = set(nltk.corpus.stopwords.words('english'))

    # Initialise dummy sentences as examples
    sentence1 = 'The Godfather was the best movie of all time.'
    print('Sentence 1:\n\t' + sentence1)
    sentence2 = 'The Godfather is one of the greatest films ever'
    print('Sentence 2:\n\t' + sentence2)
    sentence3 = 'I really did not like Gone Girl'
    print('Sentence 3:\n\t' + sentence3)
    
    # Compare sentences to each other
    print('Computing sentence vectors...')
    print('Similarity for sentences 1 and 2:\n\t' + str(similarity(sentence2vec(sentence1,nlp,stopwords),
                                                                   sentence2vec(sentence2,nlp,stopwords),
                                                                   f=dist.correlation)))
    print('Similarity for sentences 2 and 3:\n\t' + str(similarity(sentence2vec(sentence2,nlp,stopwords),
                                                                   sentence2vec(sentence3,nlp,stopwords),
                                                                   f=dist.correlation)))
    print('Similarity for sentences 1 and 3:\n\t' + str(similarity(sentence2vec(sentence1,nlp,stopwords),
                                                                   sentence2vec(sentence3,nlp,stopwords),
                                                                   f=dist.correlation)))
