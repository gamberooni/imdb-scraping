# IMDb Scraping

## Introduction
This repo performs web scraping on the IMDb website using `BeautifulSoup4`, particularly on Anime titles (who doesn't like Animes, duh!). Data of each of the Anime titles are uploaded to `MinIO` as JSON files, where each JSON file contains data of 5 titles. The `populate_db_parallel.py` script will read these JSON files and populate the `PostgreSQL` database with the [following schema](#database-schema). Finally, `Grafana` pulls the data from `PostgreSQL` for us to visualize the data. There are four general steps in this workflow: create bucket, create schema, scrape and upload to MinIO, and finally populate Postgres database using data stored in MinIO. This workflow is orchestrated using `Prefect`.

## IMPORTANT
1. Intensive web scraping can cause heavy load on the IMDb servers. You can get blocked from accessing IMDb website if you intend to speed up the scraping jobs by creating more processes. The script currently uses 2 * number of CPUs (my total CPUs = 12) and it seems alright...
    - It would be a better idea to directly download the dataset provided by the IMDb team [here](https://datasets.imdbws.com/) and the documentation for this dataset is found [here](https://www.imdb.com/interfaces/)
2. These scripts work for the current IMDb Title page layout at this time of writing (18 April 2021). The IMDb team is working on updates to the Title page and it is highly likely that these scripts may not work after the update...

## Grafana Dashboard
An example `Grafana` dashboard that I decided to come up with. 

![dashboard](./images/dashboard.png)

Visit the dashboard at `localhost:3001` and login using:
```
username: admin
password: password
```

## React App
I thought that the `Top 10 Best Anime All Time` table was too ugly so I decided to develop a Grafana `Panel` plugin to replace it. From there I figured out I needed to learn `React` (also means I have to pickup `JavaScript`) to create the plugin. 

I learned Javascript then React for about a week, and the following frontend interface is the end result of my effort :). I also had to use `Node` and `Express` to correctly reflect the top 10 anime titles stored in Postgres. The entire backend is just a single `GET` request/response so no big deal about it. 

I still think the frontend interface looks ugly, but looks good enough after spending only one week on learning the whole JS stack required to develop this. I attempted to turn it into a Grafana Panel plugin, but it requires me to understand `TypeScript` as well, which I think it requires deeper understanding of the whole JavaScript and TypeScript paradigm. So I will just leave it as it is for now...

![anime-react](./images/anime-react.png)

### Starting the React App
- To start the frontend React server, do `npm start` in `PROJECT_ROOT/anime-react`
- To start the backend Nodejs server, do `node index.js` in `PROJECT_ROOT/anime-react`
> **__NOTE:__** Make sure you already have the web scraping data stored in Postgres before doing these two steps. If not there will be error since the backend can't actually pull the data from Postgres. Start from [here](#starting-docker-containers) to scrape the data from IMDb website. 

## High-Level Block Diagram
This section describes what components each script interacts with in the workflow.

![imdb-scraping](./images/imdb-scraping.png)

## Database Schema
I decided to adopt a snowflake schema instead of star schema because of the many-to-many relationships between the tables (e.g. one title can have many writers, stars and genres) and I think I still couldn't get over the fact of the highly denormalized fact table if star schema is adopted instead. I researched a little bit and I found that composite tables are also being used in data warehouse, so I think this snowflake schema with only one composite table to each dimension table is a tradeoff I am willing to make. Feedbacks are welcome though :)

![db-schema](./images/db-schema.png)

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
1. Create Python virtual environment and activate it
> python3 -m venv venv
> 
> . venv/bin/activate
2. Install dependencies
> pip install -r requirements.txt
3. Start celery workers (if gevent workers doesn't work, you can try using eventlet workers)
> celery -A tasks worker -l info -P gevent -c 24

    - Note that this command sets the value of concurrency to be 24

4. create_bucket.py
5. scrape_parallel.py
6. create_schema.py
7. populate_db_parallel.py


## Prefect as Workflow Orchestrator
[Prefect](https://www.prefect.io/) is used to orchestrate the workflow. You can visit the Prefect UI at localhost:8080. 

I had a little experience of using Airflow. Initially I thought of using `Airflow`, but Airflow's data transfer between operators relies on Xcoms, which is a bit awkward in my opinion. I decided to experiment with Prefect, and I think the data transfer is more intuitive and natural, but its documentation should show some common data workflow examples so that it is easier to get started. It is a great tool nonetheless. 

### Steps
1. Activate Python venv
2. Use Prefect backend server
> prefect backend server
3. Start backend server
> prefect server start
4. Start a local agent
> prefect agent local start
5. Create prefect project
> prefect create project "imdb-scraping"
6. Register each of the Prefect `flow` into the Prefect backend server:
```
python prefect_create_bucket.py
python prefect_create_schema.py
python prefect_scrape_parallel.py
python prefect_populate_db_parallel.py
python prefect_parent_flow.py
```

The `prefect_parent_flow.py` is used to run a `Flow-of-Flows` and runs on a schedule that you can set and it is turned on by default. 
![prefect-flow](./images/prefect-flow.png)

**__NOTE:__** There are still some bits and pieces of work to do in refactoring the code. For example, factor out the use of Celery and Redis in the scraping and uploading job, and breaking down the populate db job into smaller separate functions for `Dask` to parallelize the execution more efficiently. 
