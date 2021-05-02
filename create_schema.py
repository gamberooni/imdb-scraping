import psycopg2
from conf import POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
from sql import *
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

conn = psycopg2.connect(
    host=POSTGRES_HOSTNAME, 
    port=POSTGRES_PORT, 
    database=POSTGRES_DATABASE, 
    user=POSTGRES_USER, 
    password=POSTGRES_PASSWORD
    )
cursor = conn.cursor()

cursor.execute(drop_schema_sql)  # drop the schema if exists
logging.info(f"Dropped schema '{schemaName}'")

cursor.execute(create_schema_sql)  # create the schema
logging.info(f"Created schema '{schemaName}'")

cursor.execute(set_search_path_sql)  # set search path to the schema
logging.info(f"Set search path to schema '{schemaName}'")
conn.commit()

for create_table in create_tables_sql:
    cursor.execute(create_table)
conn.commit()
logging.info("Finished creating tables")
