#!/usr/bin/python3

from megatick.monitors import RssMonitor

def main():
    """Monitor a pre-determined list of RSS feeds."""
    rss_monitor = RssMonitor()
    rss_monitor.start()

if __name__ == "__main__":
    main()
