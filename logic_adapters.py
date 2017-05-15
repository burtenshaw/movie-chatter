from __future__ import unicode_literals
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from chatterbot.conversation import Response
import chatterbot.comparisons as comparisons
import collections
from utils import nlp

from utils import corpus, movies, nlp
import string

conversation_history = []

def default_response():
    """
    Create a default response
    """
    response = collections.namedtuple('response', 'text confidence')
    # Set default answer
    response.text = "I don't know, ask me again later."
    response.conf = 0
    return response

def format(data_list):
    """
    Convert list ([A, B, C]) in string of the form "A, B and C"
    :return: string
    """
    assert(len(data_list) > 0)

    string = ""
    if len(data_list) == 1:
        return data_list[0]
    elif len(data_list) == 2:
        return data_list[0] + " and " + data_list[1]
    else:
        for el in data_list[:-2]:
            string += el + ", "
        string += data_list[-2] + " and " + data_list[-1]
    return string

class actorAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(actorAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['actor','performer','star']
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]

        response = self.enumerate(context)

        return response

    def enumerate(self, context):
        actornames = [actor['name'] for actor in movies.cast(context)]
        response = collections.namedtuple('response', 'text confidence')

        # Return the 5 first actor names (less if needed).
        response.text = "The most important actors are " \
                        + format(actornames[:min(len(actornames), 5)])
        response.confidence = 1

        return response



class faqAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(faqAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        """
        Checks if faqAdapter can process the statement.
        
        return True if the statement is found to be similar to a FAQ.
        """
        # NAIVE
        # Accept phrase 'I have a question' or 'may I ask a question?'
        # words = ['question']
        # return any(x in statement.text.split() for x in words)

        # SMARTER
        threshold = 0.5
        context = movies.context[0]

        # If no FAQs were found, skip
        raw_faqs = movies.faqSplitter(context)
        if raw_faqs:
            # Convert unicode strings to python strings
            faq_list = []
            for faq in movies.faqSplitter(context):
                faq_list.append([faq[0].encode('utf-8'), faq[1].encode('utf-8')])

            for faq in faq_list:
                sim = self.similar(faq[0], statement.text)
                if sim > threshold:
                    return True
        return False


    def similar(self, m1, m2):
        """
        Comparison between two message based on Levenshtein distance
        :return: float
        """
        # Compute Jaccard similarity between two lists of words
        jaccard_sim = lambda x,y: len(set(x) & set(y)) / float(len(set(x) | set(y)))

        # Remove punctuation + set to lowercase
        m1 = m1.lower().translate(None, string.punctuation)
        m2 = m2.lower().translate(None, string.punctuation)

        return jaccard_sim(m1, m2)
        # return comparison.levenshtein_distance(Statement(m1), Statement(m2))

    def process(self, statement):
        response = default_response()
        context = movies.context[0]
        # question = raw_input("What would you like to know?\n")
        question = statement.text

        # If no FAQs were found, skip
        raw_faqs = movies.faqSplitter(context)
        if raw_faqs:
            # Convert unicode strings to python strings
            faq_list = []
            for faq in movies.faqSplitter(context):
                faq_list.append([faq[0].encode('utf-8'), faq[1].encode('utf-8')])

            max_conf = -1
            for (q, a) in faq_list:
                if self.similar(question, q) > max_conf:
                    max_conf = self.similar(question, q)
                    response.confidence = max_conf
                    response.text = a
        return response


class aboutAdapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(aboutAdapter, self).__init__(**kwargs)

    def can_process(self, statement):

        words = ['about','explain','information']
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0
        # if any(x in statement.text.split() for x in words):
        #     #if len(movies.context) > 0:
        #     return 1
        # else:
        #     return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]
        val = raw_input("Do you know %s?\n" %(str(context)))

        if any(x in val for x in nlp.positives):
            print "Something you might not know is ..."
            response.text = movies.trivia(movies.context[0])
            response.confidence = 1
        else:
            response.text = movies.plot(context)
            response.confidence = 0.7
        maxSimilarity = 0
        return response

class movieAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(movieAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['movie','film','watch']        
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0
        # if any(x in statement.text.split() for x in words):
        #     return 1
        # else:
        #     return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        fav_movie = raw_input("What's your favorite film? Maybe we can find something similar.\n")
        # Get the movie
        try:
            movie = movies.getMovie(fav_movie)
        except IndexError:
            fav_movie = raw_input("I don't know that one. Any others? \n")
            movie = movies.getMovie(fav_movie)

        val = raw_input("Do you mean %s directed by %s?\n" %(movie[0].title,movie[0].director[0]))

        if any(x in val for x in nlp.positives):
            similar = movies.similarMovie(movie[2])
            response.text = "How about %s?" %(str(similar))
            response.confidence = 1
            movies.context.append(similar)

        else:
            response.confidence = 0

        return response

class ratingAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(ratingAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['rating','popular','good','like']
        #Don't use this if no context is set
        if len(movies.context) == 0:
            return 0
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0
        # if any(x in statement.text.split() for x in words):
        #     return 1
        # else:
        #     return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]
        rating = movies.rating(context)
        response.text = "The movie is rated " + str(rating) + "/10."
        if rating > 6:
            add = "\nIn general, people seem to like it."
            if rating > 8:
                add = "\nSo it should be really good!"

        response.text += add
        response.confidence = 1

        return response

class writerAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(writerAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['writer']
        #remove punctuation
        statement.text = statement.text.translate(None,string.punctuation)
        #Don't use this if no context is set
        if len(movies.context) == 0:
            return 0
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0
        # if any(x in statement.text.split() for x in words):
        #     return 1
        # else:
        #     return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]
        writers = [writer['name'] for writer in movies.writer(context)]
        response.text = "The writers of the movie are: \n" + format(writers)
        response.confidence = 1

        return response

class GenreAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(GenreAdapter, self).__init__(**kwargs)
        #Phrase 'wanna see some action tonight.'
    def can_process(self, statement):
        words = ['action','comedy', 'documentary', 'family', 'adventure', 'biography', 'crime','drama','romance','fantasy', 'horror', 'war','musical',
        'sport', 'thriller', 'western','music','history','thriller']
        statement.text = statement.text.translate(None,string.punctuation)
        if len(movies.context) == 0:
            return 0
        statement.text = statement.text.translate(None,string.punctuation)
        similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        threshold = 0.5
        if similarity >= threshold:
            return 1
        else:
            return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]
        films = movies.genreMovies(context)
        answer =  "Some movies in this genre are: \n"
        for mov in films:
            answer += "Title " +mov.title + ",  Rated: " + str(mov.rating) + '\n'
        response.text = answer
        response.confidence = 1

        return response


if __name__ == '__main__':
    import imdb
    ia = imdb.IMDb()
    movies.context = ia.search_movie('The Godfather')
    # movies.context = ia.search_movie('Asdfmovie')
    # movies.context = ia.search_movie('Total Blackout')

    # a = actorAdapter()
    # print a.process("").text

    # f = faqAdapter()
    # print f.process("").text

    f = faqAdapter()
    print f.similar(str("A note regarding spoilers"),
                    str("Will you tell spoilers?"))
    print f.similar(str("A note regarding spoilers"),
                    str("Is this about cars?"))
    # assert(f.can_process(Statement('May I ask you something?')))
    # assert(not f.can_process(Statement("What is this movie's rating?")))
    # assert(not f.can_process(Statement("Who stars in this movie?")))

