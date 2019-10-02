#!/usr/bin/python3

import configparser

import tweepy
from py2neo import Graph

from megatick.listeners import MegatickStreamListener

def create_graph():
    '''Retrieve graph credentials'''
    graph_cred = configparser.ConfigParser()
    graph_cred.read('neo4j.ini')
    graph_user = graph_cred['DEFAULT']['user']
    graph_pass = graph_cred['DEFAULT']['pass']
    graph = Graph(user=graph_user, password=graph_pass)
    if graph is not None:
        print("Loaded Neo4j graph")
    return graph

def create_auth():
    '''Create Twitter API authorization from credentials'''
    # load credentials
    credentials = configparser.ConfigParser()
    credentials.read('dev-credentials.ini')
    consumer_key = credentials['DEFAULT']['consumerKey']
    consumer_secret = credentials['DEFAULT']['consumerSecret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_token = credentials['DEFAULT']['authToken']
    auth_secret = credentials['DEFAULT']['authSecret']
    auth.set_access_token(auth_token, auth_secret)
    return auth

def main():
    """Monitor a pre-determined list of keywords on Twitter."""
    # get list of keywords
    config = configparser.ConfigParser()
    config.read('config.ini')
    keywords = []
    with open(config['DEFAULT']['keywordsLoc'], 'r') as kw_file:
        keywords = [line.strip() for line in kw_file]

    # create Neo4j Graph object if necessary
    if config['DEFAULT']['neo4j'] == "True":
        print("Attempting to load graph")
        graph = create_graph()
    else:
        graph = None

    # authorize our API
    auth = create_auth()

    # initialize API
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    # access keyword stream for selected keyword(s)
    kw_stream_listener = MegatickStreamListener(graph=graph, prefix="keyword")
    kw_stream = tweepy.Stream(auth=api.auth, listener=kw_stream_listener)

    kw_stream.filter(track=keywords)

if __name__ == '__main__':
    main()
