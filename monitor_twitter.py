#!/usr/bin/python3

import configparser
import json

import tweepy

from megatick.listeners import MegatickStreamListener
from megatick.utils import create_twitter_auth, create_graph

def main():
    """Monitor a pre-determined list of keywords on Twitter."""
    # load configuration
    config = configparser.ConfigParser()
    config.read("config.ini")

    # languages to accept (from config)
    if config.has_option("DEFAULT", "languages"):
        languages = json.loads(config['DEFAULT']['languages'])
    else:
        languages = None

    # what keywords to follow
    # TODO: keywords should be updated by an explorer module
    keywords = []
    with open(config['DEFAULT']['twitterKeywordsLoc'], "r") as kw_file:
        keywords = [line.strip() for line in kw_file]

    # what users to follow
    # TODO: users should be updated by an explorer module
    users = []
    with open(config['DEFAULT']['twitterUsersLoc'], "r") as user_file:
        users = [line.strip() for line in user_file]

    # create Neo4j Graph object if necessary
    if config['DEFAULT']['neo4j'] == "True":
        print("Attempting to load graph")
        graph = create_graph()
    else:
        graph = None

    # authorize our API
    # TODO: get file location from config
    auth = create_twitter_auth('twitter-credentials.ini')

    # initialize API
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    # access keyword stream for selected keyword(s)
    stream_listener = MegatickStreamListener(api=api, graph=graph)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

    # get up to 1% of Twitter stream this way (~60 tweets/s)
    stream.filter(track=keywords, follow=users, languages=languages)

if __name__ == "__main__":
    main()
