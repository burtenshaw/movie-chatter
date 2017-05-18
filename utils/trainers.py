from chatterbot.trainers import Trainer
from chatterbot.conversation import Response
from utils.nlp import tweetCrawl
import re
import logging

def processTweet(tweet):
    # remove mentions
    tweet = re.sub('@.+ | @[^ ]+$', '', tweet)

    # remove URLs (in a basic way)
    tweet = re.sub('http[s]?://[^ ]+', '', tweet)

    # remove extraneous spaces, newlines
    tweet = " ".join(tweet.split())

    return tweet


class TwitterTrainer(Trainer):
    def __init__(self, storage, **kwargs):
        super(TwitterTrainer, self).__init__(storage, **kwargs)

    def train(self, keywords, num_tweets):
        """
        Train the bot on Twitter search results for a number of keywords.
        For each keyword, num_tweets tweets will be fetched.
        (Although tweetCrawl might return less than num_tweets tweets--if
        any of the search results contain a tweet with no replies.)
        """

        logger = logging.getLogger("trainers.TwitterTrainer")

        for keyword in keywords:
            for tweet, reply in tweetCrawl(keyword, num_tweets):
                tweet_processed = processTweet(tweet)
                reply_processed = processTweet(reply)

                logger.info("Training tweet {}\n reply: {}".format(
                    tweet_processed.encode('utf-8'), reply_processed.encode('utf-8')))

                statement = self.get_or_create(reply_processed)

                statement.add_response(Response(tweet_processed))

                self.storage.update(statement)