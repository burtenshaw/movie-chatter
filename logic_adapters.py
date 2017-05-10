from __future__ import unicode_literals
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from chatterbot.conversation import Response

import collections

from utils import corpus, movies, nlp
import string

conversation_history = []


class faqAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(faqAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        # Accept phrase 'I have a question' or 'may I ask a question?'
        words = ['question']
        if any(x in statement.text.split() for x in words):
            return True
        else:
            return False

    def similar(self, m1, m2):
        """
        Naive comparison between two message
        :return: 1 when m1 is considered similar to m2 or -1 when m1 is not considered similar to m2.
        """
        if any(x in nlp.word_tokenize(m1) for x in nlp.word_tokenize(m2)):
            return 1
        return -1

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context[0]
        question = raw_input("What would you like to know?\n")

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

        if response.confidence <= 0:
            response.text = "I don't know, ask me again later."

        return response



class aboutAdapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(aboutAdapter, self).__init__(**kwargs)

    def can_process(self, statement):

        words = ['about','explain','information']
        if any(x in statement.text.split() for x in words):
            #if len(movies.context) > 0:
            return 1
        else:
            return 0

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

        return response

class movieAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(movieAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['movie','film','watch']

        if any(x in statement.text.split() for x in words):
            return 1
        else:
            return 0

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        fav_movie = raw_input("What's your favorite film? Maybe we can find something similar.\n")
        # Get the movie
        try:
            movie = movies.getMovie(fav_movie)
        except IndexError:
            fav_movie = raw_input("I don't know that one. Any others? \n")
            movie = movies.getMovie(fav_movie)

        val = raw_input("Do you mean %s directed by %s?\n" %(movie[0][0],movie[0][1]))

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

        #remove punctuation
        statement.text = statement.text.translate(None,string.punctuation)
        #Don't use this if no context is set
        if len(movies.context) == 0:
            return 0

        if any(x in statement.text.split() for x in words):
            return 1
        else:
            return 0

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

if __name__ == '__main__':
    import imdb
    ia = imdb.IMDb()
    movies.context = ia.search_movie('The Godfather')

    faq = faqAdapter()
    print faq.process("").text

    # about = aboutAdapter()
    # print about.process("")
