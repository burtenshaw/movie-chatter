import imdb
from imdb._exceptions import IMDbDataAccessError, IMDbError

import random

import nlp
import corpus

# Create the object that will be used to access the IMDb's database.
ia = imdb.IMDb()

# Top 250 films
top250 = ia.get_top250_movies()

## Fast index
top_250_list = []

for i in top250:
    top_250_list.append(i.movieID)
# Movie Chat tools
context = []
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
        response = False
    else:
        ia.update(movie)
        title = str(movie)
        director = str(movie['director'][0])
        response = ((title, director), True, movie)
    return response

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
    nearest = ia.get_movie_recommendations(imdb_movie.movieID)['data']['recommendations']['database'][0:5]
    return nearest[rand]

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
    return plot

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