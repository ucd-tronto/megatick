"""
Custom listeners for monitoring cybersecurity tweets.
"""

import configparser
import csv
import json
import os
import sys
import time

from http.client import IncompleteRead as http_incompleteRead
from queue import Queue
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead
from threading import Thread

import tweepy

from megatick.utils import get_full_text, get_urls, is_notable, create_twitter_auth
from megatick.nodes import Tweet, TwitterUser
from megatick.relations import AUTHORED
from megatick.site import add_urls

class MegatickStreamListener(tweepy.StreamListener):
    """
    A tweepy StreamListener with custom error handling.
    """
    def __init__(self, api=None, graph=None, prefix=None):
        """Initialize MegatickStreamListener"""
        super().__init__(api=api)
        print("Initializing listener")

        # load configuration
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Neo4j database graph or None
        self.graph = graph

        # status_queue (single-threaded) for handling tweets as they come in
        # without binding up
        self.status_queue = Queue(maxsize=0)
        status_thread = Thread(target=self.record_status)
        status_thread.start()

        self.user_blacklist = None
        if config.has_option("DEFAULT", "twitterUserBlacklistLoc"):
            with open(config["DEFAULT"]["twitterUserBlacklistLoc"], "r") as bl_file:
                self.user_blacklist = [line.strip() for line in bl_file]

        # if no graph, then print header to csv
        if self.graph is None:
            output_location = config["DEFAULT"]["tweetsLoc"]
            print("printing csv to " + output_location)

            # establish a filename with the current datetime
            filename = time.strftime("%Y-%m-%dT%H-%M-%S") + ".csv"
            if prefix is not None:
                filename = prefix + "_" + filename

            # Create a new file with that filename
            self.csv_file = open(os.path.join(output_location, filename), "w")

            # create a csv writer
            self.csv_writer = csv.writer(self.csv_file)

            # write a single row with the headers of the columns
            self.csv_writer.writerow(["text",
                                      "created_at",
                                      "geo",
                                      "lang",
                                      "place",
                                      "coordinates",
                                      "user.favourites_count",
                                      "user.statuses_count",
                                      "user.description",
                                      "user.location",
                                      "user.id",
                                      "user.created_at",
                                      "user.verified",
                                      "user.following",
                                      "user.url",
                                      "user.listed_count",
                                      "user.followers_count",
                                      "user.default_profile_image",
                                      "user.utc_offset",
                                      "user.friends_count",
                                      "user.default_profile",
                                      "user.name",
                                      "user.lang",
                                      "user.screen_name",
                                      "user.geo_enabled",
                                      "user.time_zone",
                                      "id",
                                      "favorite_count",
                                      "retweeted",
                                      "source",
                                      "favorited",
                                      "retweet_count"])

            # flush to force writing
            self.csv_file.flush()

        # when using Neo4j graph, also retrieve sites and twitter threads
        else:
            self.thread_queue = Queue(maxsize=0)
            thread_thread = Thread(target=self.get_thread)
            thread_thread.start()

            self.url_queue = Queue(maxsize=0)
            url_threads = []
            num_url_threads = int(config["DEFAULT"]["numUrlThreads"])
            for i in range(num_url_threads):
                thread = Thread(target=self.add_tweet_citations)
                thread.start()
                url_threads.append(thread)
            self.domain_blacklist = None
            if config.has_option("DEFAULT", "domainBlacklistLoc"):
                with open(config["DEFAULT"]["domainBlacklistLoc"], "r") as bl_file:
                    self.domain_blaclist = [line.strip() for line in bl_file]

    # see https://github.com/tweepy/tweepy/issues/908#issuecomment-373840687
    def on_data(self, raw_data):
        """
        This function overloads the on_data function in the tweepy package.
        It is called when raw data is received from tweepy connection.
        """
        print("received data")
        try:
            super().on_data(raw_data)
        except http_incompleteRead as error:
            print("http.client Incomplete Read error: %s" % str(error))
            print("Restarting stream search in 5 seconds...")
            time.sleep(5)
            return True
        except urllib3_incompleteRead as error:
            print("urllib3 Incomplete Read error: %s" % str(error))
            print("Restarting stream search in 5 seconds...")
            time.sleep(5)
            return True
        except BaseException as error:
            print("Error on_data: %s, Pausing..." % str(error))
            time.sleep(5)
            return True

    def on_status(self, status):
        """
        When a status is posted, sends it to a queue for recording.
        Using a queue prevents back-ups from high volume.

        Args:
            status: a tweet with metadata
        """
        print("found tweet")
        self.status_queue.put(status)
        # print(str(len(self.status_queue.queue)) + " items in status_queue")

    def on_error(self, status_code):
        """Print error codes as they occur"""
        print("Encountered error with status code:", status_code)

        # End the stream if the error code is 401 (bad credentials)
        if status_code == 401:
            return False
        return True

    def on_delete(self, status_id, user_id):
        """Note deleted tweets but do nothing else."""
        print("Delete notice")
        return True

    def on_limit(self, track):
        """Sleep and retry upon rate limit."""

        # Print rate limiting error
        print("Rate limited, waiting 15 minutes")

        # Wait 15 minutes
        time.sleep(15 * 60)

        # Continue mining tweets
        return True

    def on_timeout(self):
        """Sleep and retry when timed out."""

        # Print timeout message
        print(sys.stderr, "Timeout...")

        # Wait 10 seconds
        time.sleep(10)

        # Continue mining tweets
        return True

    def get_thread(self):
        """
        Given a Tweet object and its parent (either the tweet it's a
        quote-tweet of, or the tweet it's a reply to), find the parent (and
        its parents, recursively) and link the tweet to its parent.
        """
        # Time between requests to avoid overrunning rate limit
        # TODO: should be config
        show_rate_limit = 1.01

        while True:
            # get next tweet and parent ID from queue
            later_status, earlier_id = self.thread_queue.get()

            try:
                # sleep first to respect rate limit
                time.sleep(show_rate_limit)
                # ask for status using GET statuses/show/:id
                # TODO: batch these to get up to 100 using statuses/lookup
                earlier_status = self.api.get_status(earlier_id)
            except TweepError:
                # no available status at that ID (deleted or nonexistent)
                self.thread_queue.task_done()
                continue

            # sanity check for content
            if hasattr(earlier_status, "user"):
                # recursive call records this status and asks for more parents
                self.write_status_to_neo4j(earlier_status)
                # add link to graph to recreate Twitter threading
                links_to = LINKS_TO(later_status, earlier_status)
                self.graph.merge(links_to)

            self.thread_queue.task_done()

    def record_status(self):
        """
        Pulls a status from the queue and records it.
        """
        while True:
            status = self.status_queue.get()
            # print("writing " + str(status.id))

            # check for notability, currently hardcoded as English and not RT
            # TODO: make this modular to allow ML models of notability
            if not is_notable(status, blacklist=self.user_blacklist):
                # print("not notable, language=" + status.lang + " " + status.text[0:100])
                continue

            # If no Neo4j graph, write to csv
            if self.graph is None:
                try:
                    # print("trying to write " + str(status.id) + " to csv")
                    self.write_status_to_csv(status)
                except Exception as error:
                    print(error)

            # Neo4j graph is available, so write to it
            else:
                self.write_status_to_neo4j(status)

            # in case we need side effects for finishing a task, mark complete
            self.status_queue.task_done()

    def add_tweet_citations(self):
        """Pull a tweet's URLs from the queue to download"""
        while True:
            tweet, urls = self.url_queue.get()
            add_urls(self.graph, tweet, urls, self.domain_blacklist)
            self.url_queue.task_done()

    def write_status_to_csv(self, status):
        """Write a status in flat format (not following links)"""
        full_text = get_full_text(status)

        # Write the tweet's information to the csv file
        self.csv_writer.writerow([full_text,
                                  status.created_at,
                                  status.geo,
                                  status.lang,
                                  status.place,
                                  status.coordinates,
                                  status.user.favourites_count,
                                  status.user.statuses_count,
                                  status.user.description,
                                  status.user.location,
                                  status.user.id,
                                  status.user.created_at,
                                  status.user.verified,
                                  status.user.following,
                                  status.user.url,
                                  status.user.listed_count,
                                  status.user.followers_count,
                                  status.user.default_profile_image,
                                  status.user.utc_offset,
                                  status.user.friends_count,
                                  status.user.default_profile,
                                  status.user.name,
                                  status.user.lang,
                                  status.user.screen_name,
                                  status.user.geo_enabled,
                                  status.user.time_zone,
                                  status.id_str,
                                  status.favorite_count,
                                  status.retweeted,
                                  status.source,
                                  status.favorited,
                                  status.retweet_count])

        # flush to force writing
        self.csv_file.flush()

    def write_status_to_neo4j(self, status):
        """
        Given a JSON rep of a status, add it to the Neo4j database (or update)
        """
        full_text = get_full_text(status)
        urls = get_urls(status)

        tweet = Tweet(status.id,
                      full_text,
                      status.created_at,
                      status.geo,
                      status.lang,
                      status.coordinates,
                      status.favorite_count,
                      status.retweeted,
                      status.source,
                      status.favorited,
                      status.retweet_count,
                      urls)
        tweet.add_to(self.graph)
        # print("added tweet")
        user = TwitterUser(status.user.id,
                           status.user.screen_name,
                           status.user.name,
                           status.user.created_at,
                           status.user.url,
                           status.user.favourites_count,
                           status.user.statuses_count,
                           status.user.description,
                           status.user.location,
                           status.user.verified,
                           status.user.following,
                           status.user.listed_count,
                           status.user.followers_count,
                           status.user.default_profile_image,
                           status.user.utc_offset,
                           status.user.friends_count,
                           status.user.default_profile,
                           status.user.lang,
                           status.user.geo_enabled,
                           status.user.time_zone)
        user.add_to(self.graph)
        # print("added author")
        authored = AUTHORED(user, tweet)
        self.graph.merge(authored)

        if len(urls) > 0:
            # add url to scrape queue
            # NB: must be a pipe because we only have so much network
            #  bandwidth, but must be non-blocking so that this stream can
            #  continue
            print("adding " + str(len(urls)) + " urls")
            self.url_queue.put((tweet, urls))
            # print(str(len(self.url_queue.queue)) + " items in url_queue")

        if status.is_quote_status:
            # add upstream quote-tweet thread to download pipe
            # NB: must be a pipe because of rate limiting, but must be non-
            #  blocking so that this stream can continue
            prev_id = status.quoted_status_id
            self.thread_queue.put((tweet, prev_id))
            # print(str(len(self.thread_queue.queue)) + " items in thread_queue")

        if status.in_reply_to_status_id is not None:
            # add upstream tweet reply thread to download pipe
            # NB: must be a pipe because of rate limiting, but must be non-
            #  blocking so that this stream can continue
            prev_id = status.in_reply_to_status_id
            self.thread_queue.put((tweet, prev_id))
            # print(str(len(self.thread_queue.queue)) + " items in thread_queue")
