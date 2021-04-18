# imdb-scraping

## to-do
1. refine schema as necessary
2. do transformation on these json files and dump them into the postgres db - need to explore the data and decide what kind of transformations to perform
3. create a simple dashboard (Grafana) to show top 5 sorted by some criteria
4. include link to bring dashboard user to the imdb website of that anime

## IMPORTANT
1. Intensive web scraping can cause heavy load on the IMDb servers. You can get blocked from accessing IMDb website if you intend to speed up the scraping jobs by creating more processes. The script currently uses 2 * number of CPUs (my total CPUs = 12) and it seems alright...
2. These scripts work for the current IMDb Title page layout at this time of writing (18 April 2021). The IMDb team is working on updates to the Title page and it is highly likely that these scripts may not work after the update...

## Starting Docker containers
1. Create docker network
```
$ docker network create -d bridge imdb-scraping
```
2. Create and start `minio`, `postgres`, `rabbitmq`, `redis` and `grafana` containers
```
$ docker-compose up -d
```

## Execution sequence
1. Start celery workers
> celery -A tasks:app workers -l info -P gevent -c 24
2. create_bucket.py
3. scrape.py
4. create_schema.py
5. populate_db.py

## Grafana Dashboard
Visit `Grafana` dashboard at `localhost:3000` and login using:
```
username: admin
password: password
```
