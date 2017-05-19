from chatterbot.trainers import Trainer, ListTrainer
from chatterbot.conversation import Response, Statement

from logic_adapters import faqAdapter

class FaqTrainer(ListTrainer):
    def get_or_create(self, statement_text):
        statement = self.storage.find(statement_text)

        if not statement:
            statement = Statement(statement_text)

        # Store the logic type in the 'extra_data'
        statement.add_extra_data('logic', faqAdapter.type())
        return statement