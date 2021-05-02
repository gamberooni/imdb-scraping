from conf import POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
from sql import *
from prefect import task, Flow
from prefect.tasks.postgres import PostgresExecute
import prefect


@task
def drop_schema():
    logger = prefect.context.get("logger")
    pg = PostgresExecute(POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_HOSTNAME, POSTGRES_PORT, commit=True)
    pg.run(query=drop_schema_sql, password=POSTGRES_PASSWORD)
    logger.info(f"Dropped schema '{SCHEMA_NAME}'")

@task
def create_schema():
    logger = prefect.context.get("logger")
    pg = PostgresExecute(POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_HOSTNAME, POSTGRES_PORT, commit=True)
    pg.run(query=create_schema_sql, password=POSTGRES_PASSWORD)
    logger.info(f"Created schema '{SCHEMA_NAME}'")

@task
def create_tables():
    logger = prefect.context.get("logger")
    pg = PostgresExecute(POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_HOSTNAME, POSTGRES_PORT, commit=True)
    for create_table in create_tables_sql:
        pg.run(query=create_table, password=POSTGRES_PASSWORD)
    logger.info(f"Created tables in schema '{SCHEMA_NAME}'")


def main():
    flow = Flow("create_schema")
    flow.set_dependencies(create_schema, upstream_tasks=[drop_schema], downstream_tasks=[create_tables])
    flow.register("imdb-scraping")  # register flow to project name "imdb-scraping"
    # flow.run()

if __name__ == "__main__":
    main()
    