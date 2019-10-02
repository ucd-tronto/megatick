"""
Nodes of the Megatick Neo4j graph
"""

from py2neo import Node

class Tweet(Node):
    """Tweet Node with required parameters"""
    def __init__(self,
                 tweet_id,
                 text,
                 created_at,
                 geo,
                 lang,
                 coordinates,
                 favorite_count,
                 retweeted,
                 source,
                 favorited,
                 retweet_count):
        super().__init__("Tweet",
                         tweet_id=tweet_id,
                         text=text,
                         created_at=created_at,
                         geo=geo,
                         lang=lang,
                         coordinates=coordinates,
                         favorite_count=favorite_count,
                         retweeted=retweeted,
                         source=source,
                         favorited=favorited,
                         retweet_count=retweet_count)

    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "Tweet", "tweet_id")

class TwitterUser(Node):
    """TwitterUser with required parameters"""
    def __init__(self,
                 user_id,
                 handle,
                 user_name,
                 created_at,
                 url,
                 favourites_count,
                 statuses_count,
                 description,
                 location,
                 verified,
                 following,
                 listed_count,
                 followers_count,
                 default_profile_image,
                 utc_offset,
                 friends_count,
                 default_profile,
                 lang,
                 geo_enabled,
                 time_zone):
        super().__init__("TwitterUser",
                         user_id=user_id,
                         handle=handle,
                         user_name=user_name,
                         created_at=created_at,
                         url=url,
                         favourites_count=favourites_count,
                         statuses_count=statuses_count,
                         description=description,
                         location=location,
                         verified=verified,
                         following=following,
                         listed_count=listed_count,
                         followers_count=followers_count,
                         default_profile_image=default_profile_image,
                         utc_offset=utc_offset,
                         friends_count=friends_count,
                         default_profile=default_profile,
                         lang=lang,
                         geo_enabled=geo_enabled,
                         time_zone=time_zone)

    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "TwitterUser", "user_id")
