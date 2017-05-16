import imdb
import string

class Context():
    def __init__(self):
        self.movies = []
        self.people = []

    def upgradeMovie(self,movie):
        assert(isinstance(movie, imdb.Movie.Movie))
        try:
            self.movies.remove(movie)
        except ValueError:
            pass

        self.movies.insert(0,movie)

    def movie(self):
        if len(self.movies) > 0:
            return self.movies[0]
        else:
            return None

    def movieByTitle(self, title):
        for movie in self.movies:
            if title.lower().translate(None, string.punctuation) == str(movie).lower().translate(None, string.punctuation):
                return movie
        return None

    def getAllTitles(self):
        return [str(m) for m in self.movies]

    def upgradePerson(self, person):
        assert (isinstance(person, imdb.Person.Person))
        try:
            self.people.remove(person)
        except ValueError:
            pass

        self.people.insert(0, person)

    def person(self):
        if len(self.people) > 0:
            return self.people[0]
        else:
            return None


if __name__ == '__main__':
    import movies

    context = Context()

    # Should succeed
    imdb_actor = movies.cast(movies.tophit("the godfather"))[0]
    context.upgradePerson(imdb_actor)

    # Should succeed
    imdb_movie = movies.tophit("the godfather")
    context.upgradeMovie(imdb_movie)

    # Should succeed
    non_imdb_movie = movies.getMovie("the godfather")[2]
    context.upgradeMovie(non_imdb_movie)

    # Should succeed
    non_imdb_movie = movies.imdbMovie(movies.getMovie("the godfather"))
    context.upgradeMovie(non_imdb_movie)

    # Should fail
    non_imdb_movie = movies.getMovie("the godfather")
    try:
        context.upgradeMovie(non_imdb_movie)
        raise RuntimeError("should have failed!")
    except AssertionError:
        # Should fail
        pass
