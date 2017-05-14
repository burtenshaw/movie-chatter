#!/usr/bin/python

#context class which will be used for actors or directors
class Person(object):

	def __init__(self, id, role, movies_actor, movie_directed):
		self.id = id
		self.role = role
		self.movies_actor = movies_actor
		self.movie_directed = movie_directed

	@property
	def id(self):
		return self.__id
	@id.setter
	def id(self, value):
		self.__id = value

	@property
	def role(self):
		return self.__role
	@role.setter
	def role(self, value):
		self.__role = value

	@property
	def movies_actor(self):
		return self.__movies_actor
	@movies_actor.setter
	def movies_actor(self, value):
		self.__movies_actor = value

	@property
	def movie_directed(self):
		return self.__movie_directed
	@movie_directed.setter
	def movie_directed(self, value):
		self.__movie_directed = value
