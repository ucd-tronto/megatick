#!/usr/bin/python3

import configparser
import tweepy
from megatick import listeners

def main():
    # load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    # output location for tweets
    tweets_loc = config['tweetsLoc']

    # authorize our API
    consumer_key = config['consumerKey']
    consumer_secret = config['consumerSecret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_token = config['authToken']
    auth_secret = config['authSecret']
    auth.set_access_token(auth_token, auth_secret)

    # initialize API
    api = tweepy.API(auth)

    # access user stream for selected user(s)
    userStreamListener = UserStreamListener()
    userStream = tweepy.Stream(auth = api.auth, listener=userStreamListener)

    userStream.filter(follow=config['users'])

if __name__ == '__main__':
    main()
