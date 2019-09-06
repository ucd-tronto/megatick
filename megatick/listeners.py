"""
Custom listeners for monitoring cybersecurity tweets.
"""

import configparser
import csv
import os
import sys
import time

import tweepy

from megatick.utils import get_full_text, is_notable

class MegatickStreamListener(tweepy.StreamListener):
    """
    A tweepy StreamListener with custom error handling. This class should be
    extended, not instantiated.
    """
    def __init__(self, api=None):
        """Boilerplate init"""
        super().__init__()
        # set the api
        self.api = api

        # load configuration
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.output_location = config['DEFAULT']['tweetsLoc']

        # establish a filename with the current datetime
        filename = 'tweets_' + time.strftime('%Y-%m-%dT%H-%M-%S')+'.csv'
        self.filename = os.path.join(self.output_location, filename)

    def on_status(self, status):
        """
        When a status is posted, records it.

        Args:
            status: a tweet with metadata
        """
        if not is_notable(status):
            return

        full_text = get_full_text(status)

        # Open the csv file created previously
        csv_file = open(self.filename, 'a')

        # Create a csv writer
        csv_writer = csv.writer(csv_file)

        try:
            # Write the tweet's information to the csv file
            csv_writer.writerow([full_text,
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

        # Close the csv file
        csv_file.close()

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

class UserStreamListener(MegatickStreamListener):
    """A tweepy StreamListener for following users."""

    def __init__(self, api=None):
        """Establishes output location and creates header"""
        super().__init__(api)

        # create a file with the current datetime
        filename = 'user_tweets_' + time.strftime('%Y-%m-%dT%H-%M-%S')+'.csv'
        self.filename = os.path.join(self.output_location, filename)
        # Create a new file with that filename
        csv_file = open(self.filename, 'w')

        # create a csv writer
        csv_writer = csv.writer(csv_file)

        # write a single row with the headers of the columns
        csv_writer.writerow(['text',
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

class KeywordStreamListener(MegatickStreamListener):
    """A tweepy StreamListener for following keywords."""

    def __init__(self, api=None):
        """Establishes output location and creates header"""
        super().__init__(api)

        # create a file with the current datetime
        current_time = time.strftime('%Y-%m-%dT%H-%M-%S')
        filename = 'keyword_tweets_%s.csv' % (current_time)
        self.filename = os.path.join(self.output_location, filename)
        # Create a new file with that filename
        csv_file = open(self.filename, 'w')

        # create a csv writer
        csv_writer = csv.writer(csv_file)

        # write a single row with the headers of the columns
        csv_writer.writerow(['text',
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
