from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from trainers.FaqTrainer import FaqTrainer

import argparse

import logic_adapters
import utils.nlp as nlp

from utils import movies, confidenceRange as cr
from utils.chatbot import MovieChatBot
# Uncomment the following lines to enable verbose logging
# import logging
# logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()

# By default use JSON storage adapter; mongodb optional.

# Usage: python chatter.py --mongodb host:port
# Example: python chatter.py --mongodb localhost:27017
parser.add_argument("--mongodb")

args = parser.parse_args()

if args.mongodb is not None:
    database_uri = "mongodb://" + args.mongodb
    storage_adapter = "chatterbot.storage.MongoDatabaseAdapter"
    database = "chatterbot-database"
else:
    database_uri = None
    storage_adapter = "chatterbot.storage.JsonFileStorageAdapter"
    database = "data/top_250_faq.json"

# Create a new instance of a ChatBot

chatbot = MovieChatBot("Terminal",
    storage_adapter=storage_adapter,
    database_uri=database_uri,
    logic_adapters=[
        {
             'import_path': 'logic_adapters.movieAdapter',
        },
        {
             'import_path': 'logic_adapters.aboutAdapter',
        },
        {
             'import_path': 'logic_adapters.ratingAdapter',
        },
        {
            'import_path': 'logic_adapters.faqAdapter',
            'threshold': 0.4,
            'default_response': 'I don\'t have an answer for that, sorry'
        },
        {
            'import_path': 'logic_adapters.actorAdapter',
        },
        {
            'import_path': 'logic_adapters.writerAdapter',
        },
        {
            'import_path': 'logic_adapters.GenreAdapter',
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            "statement_comparison_function":
                lambda x, y: cr.lowConfidence(nlp.statement_comparison_for_best_match(x, y)),
            "response_selection_method": "chatterbot.response_selection.get_random_response"
        },
    ],
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter",
    database=database,
)

chatbot.set_trainer(ChatterBotCorpusTrainer)
# Train based on the english corpus.
# Focus is on general conversation, movies and subjects
# closely related to movies (history, literature, ...)
chatbot.train("chatterbot.corpus.english.conversations")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.movies")

# Example training data far FaqAdapter
chatbot.set_trainer(FaqTrainer)
chatbot.train([
    'Is this an FAQ?',
    'Hell, yes!'
])

# Train the chat bot with a few responses
# chatbot.train([])

print("Type something to begin...")
print("---")

# The following loop will execute each time the user enters input
while True:
    try:
        # We pass None to this method because the parameter
        # is not used by the TerminalAdapter
        # try:
        bot_input = chatbot.get_response(None)
        # except UnicodeDecodeError as e:
        #     # TODO: remove after development!!!
        #     print "Got error:"
        #     print e
        #
        #     pass
        print("---")

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
