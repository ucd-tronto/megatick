"""
Relations of the Megatick Neo4j graph
"""

from py2neo import Relationship

# Redditor    -(AUTHORED)-> RedditSubmission
# Redditor    -(AUTHORED)-> RedditComment
# TwitterUser -(AUTHORED)-> Tweet
AUTHORED = Relationship.type("AUTHORED")

# RedditComment    -(LINKS_TO)-> WebPage
# RedditSubmission -(LINKS_TO)-> WebPage
# Tweet            -(LINKS_TO)-> WebPage
# WebPage          -(LINKS_TO)-> WebPage
LINKS_TO = Relationship.type("LINKS_TO")
