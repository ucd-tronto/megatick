"""
Nodes of the Megatick Neo4j graph
"""

from py2neo import Node

class RedditComment(Node):
    """Reddit comment with required parameters. Contains text"""
    def __init__(self,
                 body,
                 created_at,
                 comment_id,
                 is_submitter,
                 permalink,
                 score,
                 subreddit):
        super().__init__("RedditComment",
                         body=body,
                         created_at=created_at,
                         comment_id=comment_id,
                         is_submitter=is_submitter,
                         permalink=permalink,
                         score=score,
                         subreddit=subreddit)
    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "RedditComment", "comment_id")

class RedditSubmission(Node):
    """Reddit post with required parameters. May contain link and/or text"""
    def __init__(self,
                 created_at,
                 submission_id,
                 permalink,
                 score,
                 text,
                 subreddit,
                 title,
                 upvote_ratio):
        super().__init__("RedditSubmission",
                         created_at=created_at,
                         submission_id=submission_id,
                         permalink=permalink,
                         score=score,
                         text=text,
                         subreddit=subreddit,
                         title=title,
                         upvote_ratio=upvote_ratio)
    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "RedditSubmission", "submission_id")

class Redditor(Node):
    """Redditor (Reddit user) node"""
    def __init__(self,
                 comment_karma,
                 created_at,
                 has_verified_email,
                 user_id,
                 is_mod,
                 link_karma,
                 name):
        super().__init__("Redditor",
                         comment_karma=comment_karma,
                         created_at=created_at,
                         has_verified_email=has_verified_email,
                         user_id=user_id,
                         is_mod=is_mod,
                         link_karma=link_karma,
                         name=name)
    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "Redditor", "user_id")

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

class WebPage(Node):
    """WebPage with required parameters"""
    def __init__(self,
                 url,
                 content):
        super().__init__("WebPage",
                         url=url,
                         content=content)

    def add_to(self, graph):
        """
        Add this node to an existing graph, or update it if it already exists.
        """
        return graph.merge(self, "WebPage", "url")
