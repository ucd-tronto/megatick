"""
Support functions for megatick modules.
"""

# def get_full_text(status):
#     """Returns the full text of a tweet, regardless of its length"""
#     # Check if the tweet is extended (> 140 characters)
#     try:
#         full_text = status.extended_tweet["full_text"]
#     except AttributeError:
#         full_text = status.text
#     return full_text

def get_full_text(status):
    """Return the full text of a tweet, regardless of its length"""
    # Check if the status is a retweet
    if hasattr(status, "retweeted_status"):
        # Check if the tweet is extended (> 140 characters)
        try:
            full_text = status.retweeted_status.extended_tweet["full_text"]
        except AttributeError:
            full_text = status.retweeted_status.text
    else:
        # Check if the tweet is extended (> 140 characters)
        try:
            full_text = status.extended_tweet["full_text"]
        except AttributeError:
            full_text = status.text
    return full_text

def is_notable(status):
    """Returns true if the status is to be recorded"""
    return status.lang == "en"
