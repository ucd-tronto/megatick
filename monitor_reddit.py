#!/usr/bin/python3

from megatick.monitors import RedditMonitor

def main():
    """Monitor a pre-determined list of forums (subreddits) on Reddit."""
    reddit_monitor = RedditMonitor()
    reddit_monitor.start()

if __name__ == "__main__":
    main()
