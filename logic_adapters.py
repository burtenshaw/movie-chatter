from __future__ import unicode_literals
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from chatterbot.conversation import Response

import collections

from utils import corpus, movies, nlp

conversation_history = []

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