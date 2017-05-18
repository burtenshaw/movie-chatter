import requests
import re
import json
import imdb
from class_movie import Movie

# from imdb import IMDbBase
from imdb._exceptions import IMDbDataAccessError, IMDbError

ia = imdb.IMDb()

def getMovie(id):
    # Get the first movie on IMDB that responds to a given search.
    try:
        movie = ia.get_movie(id)
        return movie
    except IndexError:
        return False


top250_url = "http://akas.imdb.com/chart/top"

r = requests.get(top250_url)
html = r.text.split("\n")
result = []
for line in html:
    line = line.rstrip("\n")
    m = re.search(r'data-titleid="tt(\d+?)">', line)
    if m:
        _id = m.group(1)
        movie = getMovie(_id)
        writer = []
        cast = []
        for w in movie['writer']:
            writer.append(w['name']) 
        for c in movie['cast']:
            cast.append(c['name']) 
        film = Movie(_id, movie['title'], movie['director'][0]['name'], movie['plot'], movie['rating'], writer, movie['genre'], cast, movie['year'])
        result.append(film.__dict__)

with open('data250.json', 'w') as outfile:
    json.dump(result, outfile)


