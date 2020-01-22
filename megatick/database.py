from megatick.utils import get_full_text
from megatick.nodes import *
from megatick.relations import *

def tweet_to_neo4j(graph, status, full_text=None):
    """
    Given a JSON rep of a status, add it to the Neo4j database (or update)
    """
    if full_text is None:
        full_text = get_full_text(status)

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
    tweet.add_to(graph)
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
    user.add_to(graph)

    authored = AUTHORED(user, tweet)
    graph.merge(authored)

    return (user, tweet, authored)

def get_tweet_node(graph, status):
    """
    Search for a Tweet node in the graph matching this status, and return it
    if it exists (otherwise None).
    """
    return graph.nodes.match("Tweet", tweet_id=status.id).first()

def link_tweets(graph, from_status, to_status):
    """
    Links two existing Tweet nodes, which must already exist in graph.
    Returns True if successfully linked, otherwise False.
    """
    from_node = get_tweet_node(graph, from_status)
    to_node = get_tweet_node(graph, to_status)
    if from_node is not None and to_node is not None:
        links_to = LINKS_TO(from_node, to_node)
        graph.merge(links_to)
        return True
    else:
        return False

def reddit_to_neo4j(graph, submission, url_queue=None):
    """
    Given a JSON rep of a reddit submission, add it to the Neo4j database
    (or update)
    """
    reddit_submission = RedditSubmission(submission.created_utc,
                                         submission.id,
                                         submission.permalink,
                                         submission.score,
                                         submission.selftext,
                                         submission.subreddit.display_name,
                                         submission.title,
                                         submission.upvote_ratio)
    reddit_submission.add_to(graph)
    # print("added reddit submission")
    user = Redditor(submission.author.comment_karma,
                    submission.author.created_utc,
                    submission.author.has_verified_email,
                    submission.author.id,
                    submission.author.is_mod,
                    submission.author.link_karma,
                    submission.author.name)
    user.add_to(graph)
    authored = AUTHORED(user, reddit_submission)
    graph.merge(authored)
    return (user, reddit_submission, authored)

# def link_reddit_to_webpage(graph, submission, url):
#     """
#     Link reddit submission to a webpage, which must already exist in graph.
#     Returns True if successfully linked, otherwise False.
#     """
#     from_node = graph.nodes.match("RedditSubmission",
#                                   submission_id=submission.id).first()
#     to_node = graph.nodes.match("WebPage", url=url).first()
#     if from_node is not None and to_node is not None:
#         links_to = LINKS_TO(from_node, to_node)
#         graph.merge(links_to)
#         return True
#     else:
#         return False

