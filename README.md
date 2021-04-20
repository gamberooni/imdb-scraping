# imdb-scraping

## To-do
1. refine schema as necessary
2. do transformation on these json files and dump them into the postgres db - need to explore the data and decide what kind of transformations to perform

## Introduction
This repo performs web scraping on the IMDb website using `BeautifulSoup`, particularly on Anime titles (who doesn't like Animes, duh!). Data of each of the Anime titles are uploaded to `MinIO` as JSON files, where each JSON file contains data of 5 titles. The `populate_db_parallel.py` script will read these JSON files and populate the `PostgreSQL` database with the [following schema](#database-schema). Finally, `Grafana` pulls the data from `PostgreSQL` for us to visualize the data.

## IMPORTANT
1. Intensive web scraping can cause heavy load on the IMDb servers. You can get blocked from accessing IMDb website if you intend to speed up the scraping jobs by creating more processes. The script currently uses 2 * number of CPUs (my total CPUs = 12) and it seems alright...
- It would be a better idea to directly download the dataset provided by the IMDb team [here](https://datasets.imdbws.com/) and the documentation for this dataset is found [here](https://www.imdb.com/interfaces/)
2. These scripts work for the current IMDb Title page layout at this time of writing (18 April 2021). The IMDb team is working on updates to the Title page and it is highly likely that these scripts may not work after the update...

## High-Level Block Diagram
![imdb-scraping](./images/imdb-scraping.png)

## Database Schema 
![db-schema](./images/db_schema.png)

## Starting Docker containers
1. Create docker network
```
$ docker network create -d bridge imdb-scraping
```
2. Create and start `minio`, `postgres`, `rabbitmq`, `redis` and `grafana` containers
```
$ docker-compose up -d
```

## Execution sequence (after starting Docker containers)
1. Start celery workers
> celery -A tasks:app workers -l info -P gevent -c 24
2. create_bucket.py
3. scrape_parallel.py
4. create_schema.py
5. populate_db_parallel.py

## Grafana Dashboard
Visit `Grafana` dashboard at `localhost:3000` and login using:
```
username: admin
password: password
```
