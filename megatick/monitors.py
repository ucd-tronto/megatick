"""
Define overarching monitor class that applies to different social media sites.
"""

from abc import ABC, abstractmethod
import configparser
import json
from queue import Queue
from threading import Thread

import tweepy

from megatick.database import reddit_to_neo4j
from megatick.utils import create_graph, create_twitter_auth, create_reddit_auth, reddit_is_notable
from megatick.listeners import MegatickStreamListener
from megatick.scraper import Scraper

class Monitor(ABC):
    """A Monitor reads some sites/api and records the results"""
    def __init__(self):
        """Generic initalization"""
        pass

    @abstractmethod
    def start(self):
        """Start reading and recording"""
        pass

class TwitterMonitor(Monitor):
    """Monitor a pre-determined set of users and keywords on Twitter."""
    def __init__(self, conf=None):
        """Initialization"""
        # load default conf if none is provided
        if conf is None:
            # load default configuration
            self.conf = configparser.ConfigParser()
            self.conf.read("config.ini")
        else:
            self.conf = conf

        # languages to accept (from conf)
        if self.conf.has_option("twitter", "languages"):
            self.languages = json.loads(self.conf.get("twitter", "languages"))
        else:
            self.languages = None

        # what keywords to follow
        # TODO: keywords should be updated by an explorer module
        self.keywords = []
        with open(self.conf.get("twitter", "keywordsLoc"), "r") as kw_file:
            self.keywords = [line.strip() for line in kw_file]

        # what users to follow
        # TODO: users should be updated by an explorer module
        self.users = []
        with open(self.conf.get("twitter", "usersLoc"), "r") as user_file:
            self.users = [line.strip() for line in user_file]

        # create Neo4j Graph object if necessary
        if self.conf.getboolean("neo4j", "useNeo4j"):
            print("Attempting to load graph")
            self.graph = create_graph(self.conf)
        else:
            self.graph = None

        # initialize scraper for external links
        self.scraper = Scraper(self.conf, self.graph)

        # authorize our API
        auth = create_twitter_auth(self.conf)

        # initialize API
        self.api = tweepy.API(auth,
                              wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)

    def start(self):
        """Start up TwitterMonitor (through MegatickStreamListener)"""
        # access keyword stream for selected keyword(s)
        stream_listener = MegatickStreamListener(api=self.api, 
                                                 graph=self.graph)
        stream = tweepy.Stream(auth=self.api.auth,
                               listener=stream_listener)

        # get up to 1% of Twitter stream this way (~60 tweets/s)
        stream.filter(track=self.keywords,
                      follow=self.users,
                      languages=self.languages)

class RedditMonitor(Monitor):
    """Monitor a pre-determined set of subreddits"""
    def __init__(self, conf=None):
        """Initialization"""
        # load default conf if none is provided
        if conf is None:
            # load default configuration
            self.conf = configparser.ConfigParser()
            self.conf.read("config.ini")
        else:
            self.conf = conf

        # what subreddits to follow
        # TODO: subreddits should be updated by an explorer module
        self.subreddits = ""
        with open(self.conf.get("reddit", "subredditsLoc"), "r") as sr_file:
            lines = [line.strip() for line in sr_file]
            self.subreddits = "+".join(lines)

        # create Neo4j Graph object if necessary
        if self.conf.getboolean("neo4j", "useNeo4j"):
            print("Attempting to load graph")
            self.graph = create_graph(self.conf)
        else:
            self.graph = None

        # read list of blacklisted user IDs to filter out. 
        self.user_blacklist = None
        if self.conf.has_option("reddit", "userBlacklistLoc"):
            userBlacklistLoc = self.conf.get("reddit", "userBlacklistLoc")
            with open(userBlacklistLoc, "r") as bl_file:
                self.user_blacklist = [line.strip() for line in bl_file]

        # read list of blacklisted terms and join them using | (or) for regex
        # searches
        self.kw_blacklist = None
        if self.conf.has_option("reddit", "keywordBlacklistLoc"):
            kwBlacklistLoc = self.conf.get("reddit", "keywordBlacklistLoc")
            with open(kwBlacklistLoc, "r") as bl_file:
                pieces = [line.strip() for line in bl_file]
                self.kw_blacklist = "|".join(pieces)

        self.scraper = Scraper(self.conf, self.graph)

        # authorize our API
        self.reddit = create_reddit_auth(self.conf)

        # set up queue to keep up with submission rate
        self.submission_queue = Queue(maxsize=0)
        thread = Thread(target=self.record_submission)
        thread.start()

    def start(self):
        """Start monitoring"""
        print("Monitoring: " + self.subreddits)
        self.reddit_thread = Thread(target=self.record_submission)

        sr = self.reddit.subreddit(self.subreddits)
        for submission in sr.stream.submissions():
            self.submission_queue.put(submission)

    def record_submission(self):
        """
        Pulls a submission from the queue and records it.
        """
        while True:
            submission = self.submission_queue.get()

            print("found " + submission.permalink)
            notable = reddit_is_notable(submission,
                                        user_blacklist=self.user_blacklist,
                                        kw_blacklist=self.kw_blacklist)
            # check for notability
            # TODO: make this modular to allow ML/ruley models of notability
            if not notable:
                continue

            # If no Neo4j graph, write to csv
            # if self.graph is None:
                # TODO: write reddit submission to csv
                # try:
                #     # print("trying to write " + str(submission.id) + " to csv")
                #     self.write_reddit_to_csv(submission)
                # except Exception as error:
                #     print(error)
            # Neo4j graph is available, so write to it
            if self.graph is not None:
            # else:
                print("recording " + submission.permalink)
                # add tweet to Neo4j graph
                _, submission_node, _ = reddit_to_neo4j(self.graph, submission)
                # recursive call to follow outgoing links
                if submission.url != submission.permalink:
                    self.scraper.link(submission_node, [submission.url])

            # in case we need side effects for finishing a task, mark complete
            self.submission_queue.task_done()
