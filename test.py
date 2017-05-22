from utils import nlp
from pyjarowinkler import distance

word1 = "music"
word2 = 'comedy'

print distance.get_jaro_distance(word1, word2)
print nlp.levensteinWord(word1, word2)