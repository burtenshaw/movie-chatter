from chatterbot import ChatBot


class MovieChatBot(ChatBot):
    """
    A more featureful ChatBot class.

    Currently it has two additional attributes:
        - input_history: A list containing all user inputs (strings). 
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

    def get_response(self, input_item, session_id=None):
        output = ChatBot.get_response(self, input_item, session_id)
        self.input_history.append(input_item)
        self.output_history.append(output)
        return output


