from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

import argparse

import logic_adapters

from utils import movies
# Uncomment the following line to enable verbose logging
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

chatbot = ChatBot("Terminal",
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
        },
        {
            'import_path': 'logic_adapters.actorAdapter',
        },
        {
            'import_path': 'logic_adapters.writerAdapter',
        },
    ],
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter",
    database=database,
    trainer='chatterbot.trainers.ListTrainer'
)


# Train the chat bot with a few responses
# chatbot.train([])

print("Type something to begin...")
print("---")

# The following loop will execute each time the user enters input
while True:
    try:
        # We pass None to this method because the parameter
        # is not used by the TerminalAdapter
        try:
            bot_input = chatbot.get_response(None)
        except UnicodeDecodeError:
            pass
        print("---")

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
