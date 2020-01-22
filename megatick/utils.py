"""
Support functions for megatick modules.
"""

import re

import praw
import tweepy

from py2neo import Graph

def partition(pred, iterable):
    """
    Given a condition pred, produce two lists of the elements in iterable
    that meet and fail that condition, respectively.
    All credit to https://stackoverflow.com/a/4578605/2749397
    """
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses

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

def tweet_is_notable(status,
                     full_text=None,
                     user_blacklist=None,
                     kw_blacklist=None):
    """Returns true if the status is to be recorded"""
    # TODO: this should optionally allow an external (e.g., machine-learning)
    #  model to make this decision.
    if full_text is None:
        full_text = get_full_text(status)

    # we're not interested in RTs with no added info
    non_rt = status.text[0:2] != 'RT'

    # check if the user is to be excluded by rule
    if user_blacklist is None:
        # print("no user blacklist!")
        user_ok = True
    else:
        user_ok = status.user.id_str not in user_blacklist
    # if not user_ok:
    #     print("blacklisted user " + status.user.name)

    # check if the tweet contains text to be excluded
    if kw_blacklist is None:
        # print("no keyword blacklist!")
        text_ok = True
    else:
        text_ok = re.search(kw_blacklist, full_text) is None
    # if not text_ok:
    #     print("blacklisted text " + full_text)
    return non_rt and user_ok and text_ok

def reddit_is_notable(submission,
                      user_blacklist=None,
                      kw_blacklist=None):
    """Returns true if the submission is to be recorded"""
    # TODO: this should optionally allow an external (e.g., machine-learning)
    #  model to make this decision.
    # check if the user is to be excluded by rule
    if user_blacklist is None:
        # print("no user blacklist!")
        user_ok = True
    else:
        user_ok = submission.author.name not in user_blacklist
    # if not user_ok:
    #     print("blacklisted user " + submission.author.name)

    # check if the submission contains text to be excluded
    if kw_blacklist is None:
        # print("no keyword blacklist!")
        text_ok = True
    else:
        text_ok = re.search(kw_blacklist, submission.selftext) is None
    # if not text_ok:
    #     print("blacklisted text " + submission.selftext)
    return user_ok and text_ok

def url_is_valid(url):
    """
    Returns true for non-html files and non-http protocols (ftp, smtp)
    """
    # TODO: refactor to use regex or cases
    invalid = (url.endswith('.7z') or
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
    return not invalid

def create_twitter_auth(conf):
    """Create Twitter API authorization from credentials"""
    # create OAuth authorization
    auth = tweepy.OAuthHandler(conf.get('twitter', 'consumerKey'),
                               conf.get('twitter', 'consumerSecret'))
    # grant auth access
    auth.set_access_token(conf.get('twitter', 'authToken'),
                          conf.get('twitter', 'authSecret'))
    return auth

def create_reddit_auth(conf):
    """Create Reddit API authorization from credentials"""
    reddit = praw.Reddit(client_id=conf.get('reddit', 'clientId'),
                         client_secret=conf.get('reddit', 'clientSecret'),
                         password=conf.get('reddit', 'password'),
                         user_agent=conf.get('reddit', 'userAgent'),
                         username=conf.get('reddit', 'username'))
    return reddit

def create_graph(conf):
    """Retrieve Neo4j graph credentials and create Graph object"""
    graph = Graph(user=conf.get('neo4j', 'user'),
                  password=conf.get('neo4j', 'pass'))
    if graph is not None:
        print("Loaded Neo4j graph")
    return graph
