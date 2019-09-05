#!/usr/bin/python3

import configparser

import tweepy

from megatick.listeners import UserStreamListener

def main():
    """Monitor a pre-determined list of Twitter accounts."""
    # get list of users
    config = configparser.ConfigParser()
    config.read('config.ini')
    users = []
    with open(config['DEFAULT']['usersLoc'], 'r') as user_file:
        users = [line.strip() for line in user_file]

    # load credentials
    credentials = configparser.ConfigParser()
    credentials.read('credentials.ini')

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

    # access user stream for selected user(s)
    user_stream_listener = UserStreamListener()
    user_stream = tweepy.Stream(auth=api.auth, listener=user_stream_listener)

    user_stream.filter(follow=users)

if __name__ == '__main__':
    main()
