# Megatick

> **megatick**, _n._
> (slang, bird watching) A greatly desirable addition to the list of birds one has seen, usually because it is rare or seldom seen.
> Etymology: _mega-_ +‎ _tick_ (as in ticking off species on a checklist)

Megatick is a system for monitoring social media and websites for your topics of interest, and adding the content of those messages into a centralized graph database.

## Installation using `conda` and Python 3.X

1. Fork and clone [this repository](https://github.com/ucd-tronto/megatick)

2. Install [conda](http://conda.pydata.org/miniconda.html)

3. Create a new conda environment using the [`environment.yml`](environment.yml) config:

```bash
conda env create -f environment.yml
```
The environment can be updated using the following command:

```bash
conda env update -f environment.yml
```

4. Activate the environment:
```conda
source activate megatick
```

5. (Optional) Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/).

## Accounts and customization

Megatick is designed to be used modularly. We currently support Twitter, Reddit, and RSS monitoring, each usable independently or together.
6. To monitor social media, you will need to apply for developer accounts and store the relevant credentials in [config.ini](config.ini). *Be sure not to commit your credentials.*
  * _Twitter_: [apply for a developer account](https://developer.twitter.com/en/apply-for-access) and create a Twitter app. Each monitor (accounts and keywords) can use the same set of credentials. Twitter's current permissions disallow multiple deployment credentials for the same application.
  * _Reddit_: Sign up for the [Reddit API](https://www.reddit.com/wiki/api) (creating a new Reddit account if necessary), create an app, and enter the resulting credentials in [config.ini](config.ini) under `[reddit]`.

Record the accounts, keywords, subreddits, and sites you want to follow. Each will be defined in a text file with one term per line. 
  * Enter Twitter handles to follow into a file whose location is specified in [config.ini](config.ini) under `twitter.usersLoc`. NB: twitter users are defined by their ID (a string of numbers) rather than their handle (e.g., `@wint`). This is because handles can change for a given account. If you need to look them up, you can use your API credentials or a conversion site like [TweeterID](https://tweeterid.com/). For example, your `twitter_users.txt` file might look like:
```
3887467873
174958347
16298441
```
  * The same goes for keywords to follow, which you can enter into a file whose location is specified under `twitter.keywordsLoc`. The keywords apply to the partially tokenized text of tweets plus some metadata. See the [Twitter Developer docs](https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators) for more detail.
  * Likewise, you can exclude selected users and keywords using files whose locations are specified under `twitter.userBlacklistLoc` and `twitter.keywordBlacklistLoc` respectively. Any tweets by these users or containing these keywords will be excluded from your streamed results.
  * Specify the location of the file of subreddits you want to monitor at `reddit.subredditsLoc`. Don't use the `r/` prefix. For example, your `subreddits.txt` file might look like:
  ```
  science
  funny
  Showerthoughts
  ```
  * Specify the location of the file of RSS feeds you want to monitor at `rss.feedsLoc`. Each line of the file should contain a complete single RSS feed URL, e.g.
  ```
  http://feeds.reuters.com/Reuters/worldNews
  https://hnrss.org/frontpage
  ```

## Running Megatick

### With Neo4j

In [config.ini](config.ini), set `neo4j.userNeo4j` to `True` and enter your credentials in `neo4j.user` and `neo4j.pass`.

In the terminal, ensure that your `Neo4j` instance is running (e.g. `sudo neo4j start`, check status with `sudo neo4j status`). Enable the environment installed earlier using `conda activate megatick`, then run:

* `python monitor_twitter.py` for the Twitter monitor,
* `python monitor_reddit.py` for the Reddit monitor, and/or
* `python monitor_rss.py` for the RSS monitor

We recommend the use of a window manager such as [tmux](https://github.com/tmux/tmux) or [gnu screen](https://www.gnu.org/software/screen/) to keep these running.

### Without Neo4j

At present, only the Twitter monitor can operate without Neo4j. To use this option, set `neo4j.useNeo4j = False`. Ensure that you have specified an output location for the tweets at `twitter.tweetsLoc`. Then enable the environment installed earlier using `conda activate megatick` and run `python monitor_twitter.py`. A CSV will be placed in that location with a filename specifying the start time. Not all information from the tweets will be placed there. If you restart the script, a new CSV will be started rather than appending the new tweets to the old file. Beware the header when you merge these files.
