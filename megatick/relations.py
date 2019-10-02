"""
Relations of the Megatick Neo4j graph
"""

from py2neo import Relationship

Authored = Relationship.type("AUTHORED")
LinksTo = Relationship.type("LINKS_TO")

# class Authored(Relationship):
#     """directed: Authored(TwitterUser, Tweet)"""
#     def __init__(self, author, content):
#         """New AUTHORED relation"""
#         self.rel = super().__init__(author, "AUTHORED", content)

#     def add_to(self, graph):
#         """Add this relation to an existing graph unless it already exists."""
#         rel = None
#         try:
#             rel = graph.merge(self.rel)
#         except Exception as error:
#             print(error)
#         return rel

# class LinksTo(Relationship):
#     """directed: LinksTo(Tweet, Tweet)"""
#     def __init__(self, linker, linkee):
#         """New LINKS_TO relation"""
#         self.rel = super().__init__(linker, "LINKS_TO", linkee)

#     def add_to(self, graph):
#         """Add this relation to an existing graph unless it already exists."""
#         rel = None
#         try:
#             rel = graph.merge(self.rel)
#         except Exception as error:
#             print(error)
#         return rel
