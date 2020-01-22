#!/usr/bin/python3

from megatick.monitors import TwitterMonitor

def main():
    """Monitor a pre-determined list of keywords on Twitter."""
    twitter_monitor = TwitterMonitor()
    twitter_monitor.start()

if __name__ == "__main__":
    main()
