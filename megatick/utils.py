"""
Support functions for megatick modules.
"""

import configparser
import praw
import tweepy

from py2neo import Graph

def get_full_text(status):
    """Return the full text of a tweet, regardless of its length"""
    # Check if the tweet is extended (> 140 characters)
    try:
        full_text = status.extended_tweet['full_text']
    except AttributeError:
        full_text = status.text
    return full_text

def get_urls(status):
    """Return the expanded (non-media) URLs in a tweet"""
    # Check if the tweet has entities with expanded urls
    try:
        urls = [format(url['expanded_url']) for url in status.entities['urls']]
    except AttributeError:
        urls = []
    return urls

def is_notable(status, blacklist=None):
    """Returns true if the status is to be recorded"""
    # TODO: this should optionally allow an external (e.g., machine-learning)
    #  model to make this decision.
    non_rt = status.text[0:2] != 'RT'
    if blacklist is None:
        print("no blacklist!")
        whitelisted = True
    else:
        whitelisted = status.user.id_str not in blacklist
    # if not whitelisted:
    #     print("blacklisted user " + status.user.name)
    return non_rt and whitelisted

def is_invalid(url):
    """
    Returns true for non-html files and non-http protocols (ftp, smtp)
    """
    # TODO: refactor to use regex or cases
    return(url.endswith('.7z') or
           url.endswith('.bz2') or
           url.endswith('.c') or
           url.endswith('.diff') or
           url.endswith('.doc') or
           url.endswith('.docx') or
           url.endswith('.gz') or
           url.endswith('.patch') or
           url.endswith('.pdf') or
           url.endswith('.ppt') or
           url.endswith('.pptx') or
           url.endswith('.rar') or
           url.endswith('.rb') or
           url.endswith('.tar') or
           url.endswith('.txt') or
           url.endswith('.zip') or
           url.endswith('.sql') or
           url.endswith('.sh') or
           url.endswith('.csh') or
           not url.startswith('http'))

def create_twitter_auth(credentials_file):
    """Create Twitter API authorization from credentials"""
    # load credentials
    credentials = configparser.ConfigParser()
    credentials.read(credentials_file)
    consumer_key = credentials['DEFAULT']['consumerKey']
    consumer_secret = credentials['DEFAULT']['consumerSecret']
    # create OAuth authorization
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_token = credentials['DEFAULT']['authToken']
    auth_secret = credentials['DEFAULT']['authSecret']
    # grant auth access
    auth.set_access_token(auth_token, auth_secret)
    return auth

def create_reddit_auth(credentials_file):
    """Create Twitter API authorization from credentials"""
    # load credentials
    credentials = configparser.ConfigParser()
    credentials.read(credentials_file)
    client_id = credentials['DEFAULT']['clientId']
    client_secret = credentials['DEFAULT']['clientSecret']
    password = credentials['DEFAULT']['password']
    username = credentials['DEFAULT']['username']
    user_agent = credentials['DEFAULT']['userAgent']
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         password=password,
                         user_agent=user_agent,
                         username=username)
    return reddit

def create_graph():
    """Retrieve Neo4j graph credentials and create Graph object"""
    graph_cred = configparser.ConfigParser()
    graph_cred.read('neo4j.ini')
    graph_user = graph_cred['DEFAULT']['user']
    graph_pass = graph_cred['DEFAULT']['pass']
    graph = Graph(user=graph_user, password=graph_pass)
    if graph is not None:
        print("Loaded Neo4j graph")
    return graph
