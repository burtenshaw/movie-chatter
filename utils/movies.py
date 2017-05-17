import imdb
from imdb._exceptions import IMDbDataAccessError, IMDbError

import random
from class_movie import Movie
import nlp
import corpus

from context import Context

# Create the object that will be used to access the IMDb's database.
ia = imdb.IMDb()

# Top 250 films
top250 = ia.get_top250_movies()

## Fast index
top_250_list = []

for i in top250:
    top_250_list.append(i.movieID)
# Movie Chat tools
context = Context()
# TODO : A list of phrases with movies in
movies_dialogue_history = []


def tophit(string):
    # Get the first movie on IMDB that responds to a given search.
    try:
        s_result = ia.search_movie(string)
        return s_result[0]
    except IndexError:
        return False

def getMovie(input_phrase):
    # Get a tuple from a sentence; ((title, director), bool, imdb_movie)
    movie = tophit(input_phrase)
    if movie == False:
        #if no movie was found, try seperate nouns
        for noun in nlp.nounList(input_phrase):
            movie = tophit(noun)
            if movie != False:
                break
        if movie == False:
            return False

    ia.update(movie)
    title = str(movie)
    director = ""
    try :
        director = str(movie['director'][0])
    except KeyError:
        # Handle unknown director
        director = "Unknown"
    film = Movie(movie.movieID, title, movie['director'], movie['plot'], movie['rating'], movie['writer'], movie['genre'], movie['cast'], movie['year'])
    response = (film,True, movie)
    return response

def genreMovies(input_phrase):
    movies = []
    for movie in top250:
        ia.update(movie)
        if input_phrase in movie['genre']:
            film = Movie(movie.movieID, movie['title'], movie['director'], movie['plot'], movie['rating'], movie['writer'], movie['genre'], movie['cast'], movie['year'])
            movies.append(film)
            if len(movies) > 5:
                break

    return movies

def checkPerson(string):
    # Check if a person is on IMDB
    nouns = nlp.propperNounList(string)
    ia = imdb.IMDb()

    last_noun = nouns[-1]
    s_result = ia.search_person(last_noun)

    if len(s_result) < 1:
        response = False

    else:
        top_hit = str(s_result[0])
        if top_hit is last_noun:
            response = top_hit
        else:
            response = "Do you mean " + top_hit + "?"
    return response

def checkMovie(input_phrase):
    # Check for a movie within a sentence.
    nouns = " ".join(nlp.propperNounList(input_phrase))
    movie = tophit(nouns)
    if movie == False:
        return (None, False)
    elif movie.movieID in top_250_list:
        return (str(movie), True)
    else:
        return (None, False)

def similarMovie(imdb_movie):
    # Take one of the top 5 movies from "people also liked"
    ia.update(imdb_movie, 'recommendations')
    rand = random.randint(0, 4)
    try:
        nearest = ia.get_movie_recommendations(imdb_movie.movieID)['data']['recommendations']['database'][0:5]
        return str(nearest[rand])
    except UnicodeDecodeError:
        rand = random.randint(0, 4)
        return str(nearest[rand])
    except:
        return None

def trivia(imdb_movie):
    # Take a random piece of trivia about a movie.
    ia.update(imdb_movie, 'trivia')
    trivia = ia.get_movie_trivia(imdb_movie.movieID)['data']['trivia']
    rand = random.randint(0, len(trivia))
    return trivia[rand]

def plot(imdb_movie):
    # Take the first sentence from the plot.
    ia.update(imdb_movie, 'plot')
    plot = ia.get_movie_plot(imdb_movie.movieID)['data']['plot'][0]
    try:
        plot = str(plot)
    except:
        plot = 'Me neither, sorry.'
    return plot

def rating(imdb_movie):
    #get the rating of a movie
    # movie = tophit(imdb_movie)
    ia.update(imdb_movie)
    return imdb_movie['rating']

def cast(imdb_movie):
    # Get the cast of a movie
    ia.update(imdb_movie)
    try:
        return imdb_movie['cast']
    except IndexError:
        return []

def writer(imdb_movie):
    # Get the cast of a movie
    ia.update(imdb_movie)
    try:
        return imdb_movie['writer']
    except IndexError:
        return []

# For building further Dataset:

def faqSplitter(movie):
    # FAQs : Split the Faqs into questions and answers return as list:
    try:
        ia.update(movie, 'faqs')
        faq = movie['faqs']
        x = []
        for i in faq:
            x.append(i.split('::'))
        return x
    except (KeyError, IMDbDataAccessError):
        pass

def keywordData():
    # Keywords : Build a dictionary of films and keywords.
    top250 = ia.get_top250_movies()
    print "Building index of titles"

    top_250_list = []
    for i in top250:
        top_250_list.append(i)

    top_250_titles = []
    for i in top250:
        top_250_titles.append(str(i))

    print "Building index of keywords"

    top_250_keywords = []
    for i in top_250_list:
        ia.update(i, 'keywords')
        top_250_keywords.append(i['keywords'])

    dataset = dict(zip(top_250_titles, top_250_keywords))

    return dataset

def imdbMovie(movie_tuple):
    """
    Extract IMDb.Movie from ((title, director), True, imdb_movie)
    """
    assert(isinstance(movie_tuple, tuple))
    assert(len(movie_tuple) == 3)

    return movie_tuple[2]
