class Context():
    def __init__(self):
        self.movies = []
        self.people = []

    def upgradeMovie(self,movie):
        try:
            self.movies.remove(movie)
        except ValueError:
            pass

        self.movies.insert(0,movie)

    def upgradePerson(self,person):
        try:
            self.peoples.remove(person)
        except ValueError:
            pass

        self.people.insert(0,person)

    def movie(self):
        if len(self.movies) > 0:
            return self.movies[0]
        else:
            return None


    def person(self):
        if len(self.people) > 0:
            return self.people[0]
        else:
            return None
