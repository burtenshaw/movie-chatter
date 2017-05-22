from pyjarowinkler import distance
from PyDictionary import PyDictionary
import nlp

genres = ['action','comedy', 'documentary', 'family', 'adventure', 'biography', 'crime','drama','romance','fantasy', 'horror', 'war','musical',
        'sport', 'thriller', 'western','music','history','thriller']

word = 'comedies'


for i in genres:
	print i
	print distance.get_jaro_distance(word, i)
	print nlp.jaccard_sim(word, i)

'''for i in genres:
	print i
	print distance.get_jaro_distance(word, i)
'''