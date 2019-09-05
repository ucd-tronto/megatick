"""
Custom listeners for monitoring cybersecurity tweets.
"""

import config
import csv
import os
import time

import tweepy

from . import utils

# load configuration
config = configparser.ConfigParser()
config.read('config.ini')
output_location = config['tweetsLoc']

class UserStreamListener(tweepy.StreamListener):
    """A tweepy StreamListener for following users."""

    def __init__(self, api=None):
        """Establishes output location and creates header"""
        # set the api
        self.api = api
        # create a file with the current datetime
        fn = 'tweets_' + time.strftime('%Y-%m-%dT%H-%M-%S')+'.csv'
        self.filename = os.join(output_location, fn)
        # Create a new file with that filename
        csvFile = open(self.filename, 'w')
        
        # create a csv writer
        csvWriter = csv.writer(csvFile)

        # write a single row with the headers of the columns
        csvWriter.writerow(['text',
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
    
    def on_status(self, status):
        """
        When a status is posted, records it.
        
        Args:
            status: a tweet with metadata
        """
        full_text = ""

        # Open the csv file created previously
        csvFile = open(self.filename, 'a')
        
        # Create a csv writer
        csvWriter = csv.writer(csvFile)
        
        # Try to 
        try:
            # Write the tweet's information to the csv file
            csvWriter.writerow([full_text,
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
        except Exception as e:
            # Print the error
            print(e)
            # and continue
            pass
        
        # Close the csv file
        csvFile.close()
        
        # Return nothing
        return

    def on_error(self, status_code):
        """Print error codes as they occur"""
        print('Encountered error with status code:', status_code)
        
        # End the stream if the error code is 401 (bad credentials)
        if status_code == 401:
            return False

    def on_delete(self, status_id, user_id):
        """Note deleted tweets but do nothing else."""
        print("Delete notice")
        
        return

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
        
        # Return nothing
        return
