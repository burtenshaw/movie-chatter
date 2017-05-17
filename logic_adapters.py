from __future__ import unicode_literals

import collections
import string

from chatterbot.logic import LogicAdapter

from utils import movies, nlp

conversation_history = []


def extractMovieContext(context, statement):
    movie = context.movie()
    statement_txt = nlp.cleanString(statement.text)

    # If another title is mentioned in the statement, load that movie
    for title in context.getAllTitles():
        # Stop at first occurence of a title in the statement.
        # They are ordered by recentness. Most recent occurence gets precedence.
        if nlp.cleanString(title) in statement_txt:
            movie = movies.context.movieByTitle(title)
            break
    return movie

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
        if movies.context.movie() is None:
            return False
        words = ['actor','performer','star']
        statement_text = nlp.cleanString(statement.text)
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False
        # similarity = nlp.levensteinWord(statement_text.lower().split(), words)
        # threshold = 0.8
        # if similarity >= threshold:
        #     return True
        # else:
        #     return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context_movie = movies.context.movie()

        response = self.enumerate(context_movie)

        return response

    def enumerate(self, imdb_movie):
        actornames = [actor['name'] for actor in movies.cast(imdb_movie)]
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
        # Can't handle empty context
        if movies.context.movie() is None:
            return False
        # Can handle any question.
        return nlp.isQuestion(statement.text)


    def similar(self, m1, m2):
        """
        Comparison between two message based on Jaccard similarity
        :return: float
        """
        return nlp.jaccard_sim(nlp.cleanString(m1), nlp.cleanString(m2))

    def process(self, statement):
        context = extractMovieContext(movies.context, statement)
        response = default_response()
        question = statement.text

        # If no FAQs were found, skip
        raw_faqs = movies.faqSplitter(context)
        if raw_faqs:
            # Convert unicode strings to python strings
            faq_list = []
            for faq in raw_faqs:
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
        if movies.context.movie() is None:
            return False
        words = ['about','explain','information']
        statement_text = nlp.cleanString(statement.text)
        # similarity = nlp.levensteinWord(statement_text.lower().split(), words)
        # threshold = 0.5
        # if similarity >= threshold and movies.context.movie() != None:
        #     return 1
        # else:
        #     return 0
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = extractMovieContext(movies.context,statement)
        movies.context.upgradeMovie(context)
        val = raw_input("Do you know %s?\n" %(str(context)))

        if any(x in val.lower() for x in nlp.positives() + ['i do']):
            print "Something you might not know is ..."
            response.text = movies.trivia(context)
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
        statement_text = nlp.cleanString(statement.text)
        # similarity = nlp.levensteinWord(statement_text.lower().split(), words)
        # threshold = 0.8
        # if similarity >= threshold:
        #     return 1
        # else:
        #     return 0
        # if any(x in statement.text.split() for x in words):
        #     return 1
        # else:
        #     return 0
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        fav_movie = raw_input("What's your favorite film? Maybe we can find something similar.\n")
        # Get the movie
        try:
            movie = movies.getMovie(fav_movie)
        except IndexError:
            fav_movie = raw_input("I don't know that one. Any others? \n")
            movie = movies.getMovie(fav_movie)

        movies.context.upgradeMovie(movie[2])
        val = raw_input("Do you mean %s directed by %s?\n" %(movie[0].title,movie[0].director[0]))

        if any(x in val.lower() for x in nlp.positives() + ['i do']):

            similar = movies.similarMovie(movie[2])
            if similar ==  None:
                response.text = 'Sorry, we couldn\'t find any similar movies.'
                response.confidence = 1
            else:
                response.text = "How about %s?" %(str(similar))
                response.confidence = 1
                movies.context.upgradeMovie(
                    movies.imdbMovie(movies.getMovie(str(similar)))
                )

        else:
            response.text = ''
            response.confidence = 0

        return response

class ratingAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(ratingAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        if movies.context.movie() is None:
            return False
        words = ['rating','popular','good','like']
        statement_text = nlp.cleanString(statement.text)
        # similarity = nlp.levensteinWord(statement.text.lower().split(), words)
        # threshold = 0.8
        # if similarity >= threshold and movies.context.movie() != None:
        #     return 1
        # else:
        #     return 0
        # if any(x in statement_text.split() for x in words):
        #     return True
        # else:
        #     return False
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context.movie()
        rating = movies.rating(context)
        response.text = "The movie is rated " + str(rating) + "/10."
        add = ''
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
        words = ['writer', 'wrote','written']
        if movies.context.movie() is None:
            return False
        statement_text = nlp.cleanString(statement.text)
        # similarity = nlp.jaccard_sim(statement_text.lower().split(), words)
        # threshold = 0.5
        # if similarity >= threshold and movies.context.movie() != None:
        #     return 1
        # else:
        #     return 0
        # if any(x in statement.text.split() for x in words):
        #     return 1
        # else:
        #     return 0
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context.movie()
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
        if movies.context.movie() is None:
            return False
        statement_text = nlp.cleanString(statement.text)
        # similarity = nlp.jaccard_sim(statement_text.lower().split(), words)
        # threshold = 0.5
        # if similarity >= threshold:
        #     return 1
        # else:
        #     return 0
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = movies.context.movie()
        films = movies.genreMovies(context)
        answer =  "Some movies in this genre are: \n"
        for mov in films:
            answer += "Title " +mov.title + ",  Rated: " + str(mov.rating) + '\n'
        response.text = answer
        response.confidence = 1

        return response


if __name__ == '__main__':
    words = ['movie','film','watch']
    statement_text = 'movie'
    print [nlp.stem(word) for word in statement_text.split()]
    if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
    # if any([nlp.stem(word) for word in words]) in [nlp.stem(word) for word in statement_text.split()]:
        print "Success!"
    else:
        print "Failed"
    # import imdb
    # ia = imdb.IMDb()
    # Movie = ia.search_movie("the godfather")[0]
    # print Movie.__class__
    # print Movie['title']
