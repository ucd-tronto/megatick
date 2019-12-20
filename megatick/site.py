'''
get markdown version of website body content
'''

import re
import requests
from bs4 import BeautifulSoup as bs
from markdownify import markdownify as md
from py2neo import NodeMatcher
from urllib.parse import urlparse

from megatick.nodes import WebPage
from megatick.relations import LINKS_TO
from megatick.utils import is_invalid

def site_exists(graph, url):
    '''Return True if content for this URL is already present'''
    matcher = NodeMatcher(graph)
    match = matcher.match("WebPage", url=url).first()
    if match is None:
        return False
    else:
        return True

def retrieve_url(url):
    '''Retrieve the markdown version of a site given a URL'''
    content = None
    # TODO: remove cruft at the end of URLs, e.g. site.com/bob.html?u=103&t=7
    if not is_invalid(url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("%d status code for %s" % (response.status_code, url))
            elif re.match("^https?://twitter.com/", response.url):
                print("tried to download a tweet")
            elif response.status_code == 200:
                soup = bs(response.content, features='html.parser')
                body = soup.find('body')
                if body is not None:
                    print('found content for', url)
                    content = md(str(body))
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Error:", err)

    return content

def add_urls(graph, citer, citees, blacklist=None):
    '''
    Add citees to graph and links citer to citees via LinksTo relations.
    Assumes citer is already in the graph.
    '''
    # ignore previously downloaded sites
    # TODO: consider recording and checking date, updating for old sites
    not_yet_cited = list(filter(lambda x: not site_exists(graph, x), citees))

    # check against a list of blacklisted domains
    if blacklist is None:
        whitelisted = not_yet_cited
    else:
        whitelisted = [url for url in not_yet_cited 
                       if urlparse(url).netloc not in blacklist]

    # for url in not_yet_cited:
    #     if url not in whitelisted:
    #         print("excluded " + url)

    # retrieve the contents of the sites
    contents = [(url, retrieve_url(url)) for url in whitelisted]

    # add these sites to the graph
    for url, content in contents:
        web_site = WebPage(url,
                           content)
        web_site.add_to(graph)
        links_to = LINKS_TO(citer, web_site)
        graph.merge(links_to)
        print('merged links_to')
