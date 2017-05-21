"""
Contains a more featureful ChatBot class that keeps conversation history.
See the MovieChatBot class for details.

Conversation history can be useful when you need more complex interactions,
with more than a single input and response. Following example defines an 
adapter that gives different replies depending on the history:

    # Defining an adapter somewhere
    from chatterbot.logic import LogicAdapter
    from chatterbot.conversation import Statement
    from chatterbot.comparisons import levenshtein_distance

    class AstleyAdapter(LogicAdapter):

        def __init__(self, **kwargs):
            super(AstleyAdapter, self).__init__(**kwargs)

        def process(self, statement):
            hist = self.chatbot.output_history
            conf = levenshtein_distance(Statement("never gonna"), statement)
            if hist == [] or hist[-1].text != "give you up!":
                res = Statement(text="give you up!")
            else:
                res = Statement(text="let you down!")
            res.confidence = conf
            return res

    # Building the chatbot
    from utils.chatbot import MovieChatBot

    chatbot = MovieChatBot(
        "AstleyBot", 
        input_adapter = "chatterbot.input.TerminalAdapter",
        output_adapter = "chatterbot.output.TerminalAdapter",
        logic_adapters = ["chatterbot.logic.BestMatch",
                          "logic_adapters.AstleyAdapter"]
        # ...
    )

More complex historical information could be kept by using the Statement's 
add_extra_data() method.
"""

from chatterbot import ChatBot


class MovieChatBot(ChatBot):
    """
    A more featureful ChatBot class.

    Currently it has two additional attributes:
        - input_history: A list containing all user inputs (Statements). 
          Ordered from old to new.
        - output_history: A list containing all chatbot outputs (Statements).
          Ordered from old to new.

    Note that an input is added to the history only after the corresponding 
    output has been decided. The two histories are always equal in length.
    """

    def __init__(self, *args, **kwargs):
        ChatBot.__init__(self, *args, **kwargs)
        self.input_history = []
        self.output_history = []

    def generate_response(self, input_statement, session_id):
        input_statement, response = \
                ChatBot.generate_response(self, input_statement, session_id)
        self.input_history.append(input_statement)
        self.output_history.append(response)
        return input_statement, response


