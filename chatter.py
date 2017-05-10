from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

import logic_adapters

from utils import movies
# Uncomment the following line to enable verbose logging
# logging.basicConfig(level=logging.INFO)

# Create a new instance of a ChatBot

chatbot = ChatBot("Terminal",
    storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
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
    database="data/database.db",
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
        bot_input = chatbot.get_response(None)
        print("---")

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
