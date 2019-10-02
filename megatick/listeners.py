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
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead

import tweepy

from megatick.utils import get_full_text, is_notable
from megatick.nodes import Tweet, TwitterUser
from megatick.relations import Authored

class MegatickStreamListener(tweepy.StreamListener):
    """
    A tweepy StreamListener with custom error handling.
    """
    def __init__(self, graph=None, prefix=None):
        """Initialize MegatickStreamListener"""
        super().__init__()
        print("Initializing listener")
        self.graph = graph
        self.output_location = None
        self.filename = None

        # if no graph, then print header to csv
        if self.graph is None:
            # load configuration
            config = configparser.ConfigParser()
            config.read('config.ini')
            self.output_location = config['DEFAULT']['tweetsLoc']

            # establish a filename with the current datetime
            self.filename = time.strftime('%Y-%m-%dT%H-%M-%S') + '.csv'
            if prefix is not None:
                self.filename = prefix + '_' + self.filename

            # Create a new file with that filename
            csv_file = open(os.path.join(self.output_location, self.filename), 'w')

            # create a csv writer
            self.csv_writer = csv.writer(csv_file)

            # write a single row with the headers of the columns
            self.csv_writer.writerow(['text',
                                      'created_at',
                                      'geo',
                                      'lang',
                                      'place',
                                      'coordinates',
                                      'user.favourites_count',
                                      'user.statuses_count',
                                      'user.description',
                                      'user.location',
                                      'user.id',
                                      'user.created_at',
                                      'user.verified',
                                      'user.following',
                                      'user.url',
                                      'user.listed_count',
                                      'user.followers_count',
                                      'user.default_profile_image',
                                      'user.utc_offset',
                                      'user.friends_count',
                                      'user.default_profile',
                                      'user.name',
                                      'user.lang',
                                      'user.screen_name',
                                      'user.geo_enabled',
                                      'user.time_zone',
                                      'id',
                                      'favorite_count',
                                      'retweeted',
                                      'source',
                                      'favorited',
                                      'retweet_count'])

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
        When a status is posted, records it.

        Args:
            status: a tweet with metadata
        """
        print("found tweet")

        if not is_notable(status):
            return

        full_text = get_full_text(status)

        # If no Neo4j graph,
        if self.graph is None:
            try:
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
            # If some error occurs
            except Exception as error:
                # print the error
                print(error)

        else:
            print("putting it in neo4j")
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
                          status.retweet_count)
            tweet.add_to(self.graph)

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

            authored = Authored(user, tweet)
            # authored.add_to(self.graph)
            self.graph.merge(authored)

    def on_error(self, status_code):
        """Print error codes as they occur"""
        print('Encountered error with status code:', status_code)

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
        print(sys.stderr, 'Timeout...')

        # Wait 10 seconds
        time.sleep(10)

        # Continue mining tweets
        return True
