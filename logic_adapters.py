from __future__ import unicode_literals

import collections
import string

from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement

from utils import movies, nlp, confidenceRange as cr

conversation_history = []



def findStatementInStorage(logicAdapter, statement):
    """
    Is the statement stored in the logicAdapters storage?
    
    Checks the stored statement to be of the same type as logicAdapter.
    """
    for stored_statement in logicAdapter.chatbot.storage.filter():
        try:
            if stored_statement.extra_data['logic'] == logicAdapter.type():
                if stored_statement.text == statement.text:
                    return True

        except KeyError:
            # Ignore all statements without the extra_data "logic"
            pass


def extractMovieContext(context, statement):
    # If last 2 mentions were of same movie, set it as the primary movie.
    count = 2
    if len(context.mentionedMovies) >= 2:
        start = context.mentionedMovies[0]
        same = True
        for i in range(count):
            if context.mentionedMovies[i] != start:
                same = False
        if same:
            context.upgradeMovie(start)

    movie = context.movie()
    statement_txt = nlp.cleanString(statement.text)

    # If another title is mentioned in the statement, load that movie
    for title in context.getAllTitles():
        # Stop at first occurence of a title in the statement.
        # They are ordered by recentness. Most recent occurence gets precedence.
        if nlp.cleanString(title) in statement_txt:
            movie = movies.context.movieByTitle(title)
            break

    # The movie was mentioned.
    context.mentionMovie(movie)

    return movie

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
        # if movies.context.movie() is None:
        #     return False
        words = ['actor','performer','star', 'appear', 'act', 'perform']
        statement_text = nlp.cleanString(statement.text)
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        threshold = 0.6
        humanNames = nlp.get_human_names(statement.text)
        (person,nameSimilar,similarity) = movies.getPersonMaxSimilarity(humanNames)
        if similarity >= threshold:
            val = raw_input("Do you mean %s \n" %(person))
            if any(x in val.lower() for x in nlp.positives()):
                if 'cast'  in movies.people_role[person]:
                    moviesW = movies.people_role[person]['cast']
                    response.text = person + " has acted in: " + format(moviesW)
                else:
                    response.text = person + " is not registered as an actor in our Database, keep trying, we won't give up!!"
            else:
                response.text = ""
            response.confidence = cr.lowConfidence(1)
        else:
            response.text = ""
            response.confidence = cr.lowConfidence(1)
        if response.text == "":
            if movies.context.movie() is not None:
                context_movie = extractMovieContext(movies.context, statement)
                response = self.enumerate(context_movie)

        return response

    def enumerate(self, imdb_movie):
        actornames = [actor['name'] for actor in movies.cast(imdb_movie)]
        response = collections.namedtuple('response', 'text confidence')

        # Return the 5 first actor names (less if needed).
        response.text = "The most important actors are " \
                        + format(actornames[:min(len(actornames), 5)])
        response.confidence = cr.lowConfidence(1)

        return response



class faqAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(faqAdapter, self).__init__(**kwargs)
        self.threshold= kwargs['threshold']
        # Multiplication factor for confidence. Lower the FAQ to prioritize other logicAdapters.
        self.default_response = kwargs['default_response']

    @staticmethod
    def type():
        """
        Used by to generate the Statements 'logic type' when training custom phrases.
        """
        return 'faq'

    def can_process(self, statement):
        """
        Checks if faqAdapter can process the statement.

        return True if the statement is found to be similar to a FAQ.
        """
        # Can't handle empty context
        if movies.context.movie() is None:
            return False

        # If statement is in storage, we can handle it!
        if findStatementInStorage(self, statement):
            return True

        # Can handle any question.
        return nlp.isQuestion(statement.text)


    def similar(self, m1, m2):
        """
        Comparison between two message based on Jaccard similarity
        :return: float
        """
        return nlp.jaccard_sim(nlp.cleanString(m1), nlp.cleanString(m2))

    def process(self, statement):
        # Update the context
        context = extractMovieContext(movies.context, statement)

        # Get all statements that are in response to the statement
        response_list = self.chatbot.storage.filter(
            in_response_to__contains=statement.text
        )

        # If statement was found in storage
        if response_list:
            response = self.select_response(statement, response_list)
            response.confidence = cr.highConfidence(1)

        # If statement not in storage, handle it manually
        else:
            response = collections.namedtuple('response', 'text confidence')
            response.confidence = cr.lowConfidence(0)
            response.text = self.default_response

            # If no FAQs were found, skip
            raw_faqs = movies.faqSplitter(context)
            if raw_faqs:
                max_conf = -1
                for (q, a) in raw_faqs:
                    try:
                        similarity = self.similar(statement.text, q.encode('utf-8'))
                        if similarity > max_conf:
                            max_conf = similarity
                            response.text = a
                    except UnicodeEncodeError as e:
                        # This happens when reading links.
                        # TODO: fix or remove after development.
                        print "failed to parse answer"
                        continue
                response.confidence = cr.lowConfidence(max_conf)

            if response.confidence < self.threshold:
                response.text = self.default_response
                response.confidence = cr.noConfidence(0)

        return response


class aboutAdapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(aboutAdapter, self).__init__(**kwargs)
        self.movie = None

    def can_process(self, statement):
        if movies.context.movie() is None:
            return False

        if self.conversation_stage() == 1:
            return True

        words = ['about', 'explain', 'information']
        statement_text = nlp.cleanString(statement.text)

        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = Statement("")
        stage = self.conversation_stage(response)

        if stage == 0:
            self.movie = extractMovieContext(movies.context, statement)
            movies.context.upgradeMovie(self.movie)
            response.text = "Do you know %s?" %(str(self.movie))
            response.confidence = cr.lowConfidence(1)
        elif stage == 1:
            val = statement.text.lower()
            if any(x in val for x in nlp.positives() + ['i do']):
                response.text  = "Something you might not know is ...\n"
                response.text += movies.trivia(self.movie)
                response.confidence = cr.mediumConfidence(1)
            else:
                response.text = movies.plot(self.movie)
                response.confidence = cr.lowConfidence(0.7)

        return response

    def conversation_stage(self, response=Statement("")):
        hist = self.chatbot.output_history
        if hist == [] or type(hist[-1]) != Statement:
            stage = 0
        else:
            stage = hist[-1].extra_data.get("about_stage", -1) + 1
        response.add_extra_data("about_stage", stage)
        return stage


class movieAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(movieAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['movie', 'film','watch']
        statement_text = nlp.cleanString(statement.text)
        #If user wants to know about a genre, don't give this adapter
        genre = GenreAdapter()
        if genre.can_process(statement):
            return False
        writer = writerAdapter()
        if writer.can_process(statement):
            return False
        actor = actorAdapter()
        if actor.can_process(statement):
            return False

        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        movie = None
        response = collections.namedtuple('response', 'text confidence')
        fav_movie = raw_input("What's your favorite film? Maybe we can find something similar.\n")
        # Get the movie
        while True:
            try:
                movie = movies.getMovie(fav_movie.rstrip(string.punctuation))   # Remove trailing punctuation for better search results
                break
            except IndexError:
                fav_movie = raw_input("I don't know that one. Any others? \n")
                # movie = movies.getMovie(fav_movie)

        movies.context.upgradeMovie(movies.imdbMovie(movie))
        val = raw_input("Do you mean %s directed by %s?\n" %(movie[0].title,movie[0].director))

        if any(x in val.lower() for x in nlp.positives() + ['i do']):

            similar = movies.similarMovie(movie[2])
            if similar ==  None:
                response.text = 'Sorry, we couldn\'t find any similar movies.'
                response.confidence = cr.noConfidence(1)
            else:
                response.text = "How about %s?" %(str(similar))
                response.confidence = cr.lowConfidence(1)
                movies.context.upgradeMovie(
                    movies.imdbMovie(movies.getMovie(str(similar)))
                )

        else:
            response.text = 'Then I don\'t know which one you mean.'
            response.confidence = cr.noConfidence(0.7)

        return response

class ratingAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(ratingAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        if movies.context.movie() is None:
            return False
        words = ['rating','popular','good','like']
        statement_text = nlp.cleanString(statement.text)

        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        context = extractMovieContext(movies.context, statement)
        rating = movies.rating(context)
        response.text = "The movie is rated " + str(rating) + "/10."
        add = ''
        if rating > 6:
            add = "\nIn general, people seem to like it."
            if rating > 8:
                add = "\nSo it should be really good!"

        response.text += add
        response.confidence = cr.lowConfidence(1)

        return response

class writerAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(writerAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        words = ['writer', 'wrote','written','create','compose','author','scribble','rewrite']
        statement_text = nlp.cleanString(statement.text)
        if any(nlp.stem(x) in [nlp.stem(w) for w in words] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):        
        response = collections.namedtuple('response', 'text confidence')
        threshold = 0.6
        humanNames = nlp.get_human_names(statement.text)
        (person,nameSimilar,similarity) = movies.getPersonMaxSimilarity(humanNames)
        if similarity >= threshold:
            val = raw_input("Do you mean %s \n" %(person))
            if any(x in val.lower() for x in nlp.positives()):
                if 'writer'  in movies.people_role[person]:
                    moviesW = movies.people_role[person]['writer']
                    response.text = person + " has written: " + format(moviesW)
                else:
                    response.text = person + " is not registered as a writer in our Database, keep trying, we won't give up!!"
            else:
                response.text = ""
            response.confidence = cr.lowConfidence(1)
        else:
            response.text = ""
            response.confidence = cr.lowConfidence(1)
        if response.text == "":
            if movies.context.movie() is not None:
                context = extractMovieContext(movies.context, statement)
                writers = [writer['name'] for writer in movies.writer(context)]
                response.text = "The writers of the movie are: \n" + format(writers)
                response.confidence = cr.lowConfidence(1)
        return response

class GenreAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(GenreAdapter, self).__init__(**kwargs)
        self.genres = ['action','comedy', 'documentary', 'family', 'adventure', 'biography', 'crime','drama','romance','fantasy', 'horror', 'war','musical',
        'sport', 'thriller', 'western','music','history','thriller']

        #Phrase 'wanna see some action tonight.'
    def can_process(self, statement):
        statement_text = nlp.cleanString(statement.text)
        if any(nlp.stem(x) in [nlp.stem(w) for w in self.genres] for x in statement_text.split()):
            return True
        else:
            return False

    def process(self, statement):
        response = collections.namedtuple('response', 'text confidence')
        response.text = 'sorry! we couldnt find any movie in this genre'
        response.confidence = cr.noConfidence(1)
        genre = [genre for genre in self.genres if genre in nlp.cleanString(statement.text)]
        resp = raw_input("Shall I propose some %s movies for you?\n"%genre[0])

        if any(x in resp.lower() for x in nlp.positives() + ['i do']):
            films = movies.genreMovies(genre[0])
            if len(films) != 0:
                answer =  "Some movies in this genre are: \n"
                for film,movie in films:
                    answer += '%s , directed by %s \n'% (film.title, film.director)
                    movies.context.upgradeMovie(movie)

                answer = answer[:-4]
                response.text = answer
                response.confidence = cr.lowConfidence(1)
                # fav_movie = raw_input("select what movie do you like to see !!! \n")
                # # Get the movie
                # try:
                #     movie = movies.getMovie(fav_movie)
                # except IndexError:
                #     fav_movie = raw_input("I don't know that one. Any others? \n")
                #     movie = movies.getMovie(fav_movie)
                # movies.context.upgradeMovie(movie[2])
                # val = raw_input("Do you mean %s directed by %s?\n" %(movie[0].title,movie[0].director))
                # if any(x in resp.lower() for x in nlp.positives() + ['i do']):
                #     response.text = 'ejoy the movie !!!'
                #     response.confidence = 1
                # else:
                #     similar = movies.similarMovie(movie[2])
                #     if similar ==  None:
                #         response.text = 'Sorry, we couldn\'t find any similar movies.'
                #         response.confidence = 1
                #     else:
                #         response.text = "How about %s?" %(str(similar))
                #         response.confidence = 1
                #         movies.context.upgradeMovie(
                #             movies.imdbMovie(movies.getMovie(str(similar)))
                #         )

        else:
            response.text = 'Anything else I can help you with?'

        return response


if __name__ == '__main__':
    from utils import context
    from chatterbot.conversation.statement import Statement

    movies.context = context.Context()
    movies.context.upgradeMovie(movies.imdbMovie(movies.getMovie("the godfather")))
    faq = faqAdapter()
    print faq.process(Statement("what is the godfather about?")).text
