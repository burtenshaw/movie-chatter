import json

# Format the string for referencing as json
def format(list, ref_string):
    x = { ref_string: []}
    x[ref_string] = list
    return x

# save as a json file
def save(output_file, corpus):
    f = open(output_file, 'w')
    json.dump(corpus, f)

# load a json file
def load(file):
	with open(file, 'r') as f:
		data = json.load(f)
	return data

