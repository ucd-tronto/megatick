#!/usr/bin/python3

import configparser

import tweepy

from megatick.listeners import KeywordStreamListener

def main():
    """Monitor a pre-determined list of keywords on Twitter."""
    # get list of keywords
    config = configparser.ConfigParser()
    config.read('config.ini')
    keywords = []
    with open(config['DEFAULT']['keywordsLoc'], 'r') as kw_file:
        keywords = [line.strip() for line in kw_file]

    # load credentials
    credentials = configparser.ConfigParser()
    credentials.read('keyword-credentials.ini')

    # authorize our API
    consumer_key = credentials['DEFAULT']['consumerKey']
    consumer_secret = credentials['DEFAULT']['consumerSecret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_token = credentials['DEFAULT']['authToken']
    auth_secret = credentials['DEFAULT']['authSecret']
    auth.set_access_token(auth_token, auth_secret)

    # initialize API
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    # access keyword stream for selected keyword(s)
    kw_stream_listener = KeywordStreamListener()
    kw_stream = tweepy.Stream(auth=api.auth, listener=kw_stream_listener)

    kw_stream.filter(track=keywords)

if __name__ == '__main__':
    main()
