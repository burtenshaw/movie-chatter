#!/usr/bin/python

#class Movie which will handle an IMBD movie and its properties
class Movie(object):
	def __init__(self, id, title, director, plot, rating, writer, actors, genres, cast, year):
		self.id = id
		self.title = title
		self.director = director
		self.plot = plot
		self.writer = writer
		self.rating = rating
		self.actors = actors
		self.genres = genres
		self.cast = cast
		self.year = year

	@property
	def id(self):
		return self.__id
	@id.setter
	def id(self, value):
		self.__id = value

	@property
	def title(self):
		return self.__title
	@title.setter
	def title(self, value):
		self.__title = value

	@property
	def director(self):
		return self.__director
	@director.setter
	def director(self, value):
		self.__director = value

	@property
	def plot(self):
		return self.__plot
	@plot.setter
	def plot(self, value):
		self.__plot = value

	@property
	def rating(self):
		return self.__rating
	@rating.setter
	def rating(self, value):
		self.__rating = value

	@property
	def writer(self):
		return self.__writer
	@writer.setter
	def writer(self, value):
		self.__writer = value

	@property
	def actors(self):
		return self.__actors
	@actors.setter
	def actors(self, value):
		self.__actors = value

	@property
	def genres(self):
		return self.__genres
	@genres.setter
	def genres(self, value):
		self.__genres = value

	@property
	def cast(self):
		return self.__cast
	@cast.setter
	def cast(self, value):
		self.__cast = value

	@property
	def year(self):
		return self.__year
	@year.setter
	def year(self, value):
		self.__year = value