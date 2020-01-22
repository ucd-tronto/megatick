"""
Get markdown version of website body content in a threaded fashion
"""

import configparser
import re
from bs4 import BeautifulSoup as bs
from markdownify import markdownify as md
from py2neo import NodeMatcher
from queue import Queue
from threading import Thread
from urllib.parse import urlparse
import requests

from megatick.nodes import WebPage
from megatick.relations import LINKS_TO
from megatick.utils import create_graph, url_is_valid

def retrieve_url(url):
    """Retrieve the markdown version of a site given a URL"""
    content = None
    # TODO: remove cruft at the end of URLs, e.g. site.com/bob.html?u=103&t=7
    if url_is_valid(url):
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

class Scraper:
    """
    Manage URL downloading in a threaded fashion
    """

    def __init__(self, conf=None, graph=None):
        # load default conf if none is provided
        if conf is None:
            # load default configuration
            conf = configparser.ConfigParser()
            conf.read("config.ini")

        # create new copy of (default) graph if none is provided
        if graph is None:
            self.graph = create_graph(conf)
        else:
            self.graph = graph
        self.matcher = NodeMatcher(self.graph)

        # domains to ignore
        self.blacklist = None
        if conf.has_option("DEFAULT", "domainBlacklistLoc"):
            with open(conf.get("DEFAULT", "domainBlacklistLoc"), "r") as bl_file:
                self.blacklist = [line.strip() for line in bl_file]

        # queue for sites to download
        self.queue = Queue(maxsize=0)
        threads = []
        num_threads = conf.getint("DEFAULT", "numUrlThreads")
        for _ in range(num_threads):
            thread = Thread(target=self.add_urls)
            thread.start()
            threads.append(thread)

    def get_or_add(self, url):
        """
        If a WebPage has been previously downloaded, return the node so it can
        be linked to the citer. Otherwise, try to create a new node.
        """
        match = self.matcher.match("WebPage", url=url).first()
        if match is None:
            content = retrieve_url(url)
            if content is not None:
                web_site = WebPage(url,
                                   content)
                web_site.add_to(self.graph)
                web_site
            else:
                None
        else:
            match


    def remove_blacklisted(self, urls):
        """Filter out urls that match blacklisted domains"""
        if self.blacklist is None:
            return urls
        else:
            return [url for url in urls
                    if urlparse(url).netloc not in self.blacklist]

    def add_urls(self):
        """
        Add citees to graph and links citer to citees via LinksTo relations.
        Assumes citer is already in the graph.
        """
        while True:
            # pull a task from the download queue
            citer, urls = self.queue.get()

            # filter out forbidden domains
            whitelisted = self.remove_blacklisted(urls)

            # download new sites and get nodes of previously downloaded sites
            # TODO: consider using date to update old sites
            web_pages = [self.get_or_add(url) for url in whitelisted]

            # connect citer (node) to WebPage nodes
            for web_page in web_pages:
                links_to = LINKS_TO(citer, web_page)
                self.graph.merge(links_to)
                # print('merged links_to')

            self.queue.task_done()

    def link(self, citer, citees):
        """
        Add a citer and its citees to the queue to be downloaded and
        linked
        """
        self.queue.put((citer, citees))
