# imdb-scraping

# to-do
1. to output to 5 movie details into a .json file
2. create a minio bucket - name based on date
3. content of bucket = all these json files
4. do this once every week
5. use airflow to orchestrate
6. create a postgres db
7. decide a schema 
8. do transformation on these json files and dump them into the postgres db
9. create a simple dashboard to show top 5 sorted by some criteria
10. include link to bring dashboard user to the imdb website of that anime
11. use docker-compose to bring up these different containers
12. airflow(scraping job + transformation here) - minio - postgres - superset/redash?