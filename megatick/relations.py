"""
Relations of the Megatick Neo4j graph
"""

from py2neo import Relationship

AUTHORED = Relationship.type("AUTHORED")
LINKS_TO = Relationship.type("LINKS_TO")
