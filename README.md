# imdb-scraping

## to-do
1. ~~to output to 5 movie details into a .json file~~
2. ~~create a minio bucket - name based on date~~
3. ~~content of bucket = all these json files~~
5. ~~create a postgres db~~
6. ~~decide a schema~~ - need to refine
7. do transformation on these json files and dump them into the postgres db - need to explore the data and decide what kind of transformations to perform
8. create a simple dashboard to show top 5 sorted by some criteria
9. include link to bring dashboard user to the imdb website of that anime
10. ~~use docker-compose to bring up these different containers~~
12. ~~use rabbitmq and celery, and multiprocessing module to parallelize jobs~~

## Starting Docker containers
1. Create docker network
```
$ docker network create -d bridge imdb-scraping
```
2. Create `minio` and `postgres` containers
```
$ docker-compose up -d
```

## Execution sequence
1. Start celery workers
> celery -A tasks:app workers -l info -P gevent
2. create_bucket.py
3. scrape.py
4. create_schema.py
5. populate_db.py