"""
Train from tweets using TwitterTrainer. Default mode is training, use --test to test.
When training specify --keywords <keywords>, a comma-separated list of keywords.
"""

from chatterbot import ChatBot
import utils.nlp as nlp
import argparse
import sys
import logging

parser = argparse.ArgumentParser()

# By default use JSON storage adapter; mongodb optional.

# Usage: python chatter.py --mongodb host:port
# Example: python chatter.py --mongodb localhost:27017
parser.add_argument("--mongodb")
parser.add_argument("--keywords")
parser.add_argument("--num-tweets", type=int, default=20)
parser.add_argument("--test", action="store_true")

args = parser.parse_args()

test = args.test
keywords = args.keywords.split(',') if args.keywords else None
num_tweets = args.num_tweets

if args.mongodb is not None:
    database_uri = "mongodb://" + args.mongodb
    storage_adapter = "chatterbot.storage.MongoDatabaseAdapter"
    database = "chatterbot-database"
else:
    database_uri = None
    storage_adapter = "chatterbot.storage.JsonFileStorageAdapter"
    database = "data/top_250_faq.json"

chatbot = ChatBot("Terminal",
    storage_adapter=storage_adapter,
    database_uri=database_uri,
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "statement_comparison_function": nlp.statement_comparison_for_best_match,
            "response_selection_method": "chatterbot.response_selection.get_random_response"
        }
    ],
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter",
    database=database,
    trainer="trainers.TwitterTrainer.TwitterTrainer"
)

if test:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    print("Type something to begin...")
    print("---")

    while True:
        try:
            bot_input = chatbot.get_response(None)
            print("---")

        except (KeyboardInterrupt, EOFError, SystemExit):
            break
else:
    # train
    
    if keywords is None:
        raise Exception("Specify --keywords when training.")
    chatbot.train(keywords, num_tweets)
