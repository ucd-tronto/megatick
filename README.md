# megatick

> **megatick**, _n._
> (slang, bird watching) A greatly desirable addition to the list of birds one has seen, usually because it is rare or seldom seen.
> Etymology: _mega-_ +‎ _tick_ (as in ticking off species on a checklist)


## Installation: Using `conda` and Python 3.X

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

5. (Optional) Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/). Set `neo4j = True` in `config.ini` and enter your credentials into `neo4j.ini` to connect to your Neo4j instance.

6. To monitor Twitter accounts and keywords, you will need to [apply for a developer account](https://developer.twitter.com/en/apply-for-access) and create a Twitter app. Each monitor (accounts and keywords) can use the same set of credentials, kept in `twitter-credentials.ini`.
