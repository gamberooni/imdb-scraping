import psycopg2
import os
from dbconf import *
from sql import *

conn = psycopg2.connect(host=HOSTNAME, port=PORT, database=DBNAME, user=USERNAME, password=PASSWORD)
cursor = conn.cursor()

cursor.execute(drop_schema)  # drop the schema if exists
print(f"Dropped schema '{schemaName}'")
cursor.execute(create_schema)  # create the schema
print(f"Created schema '{schemaName}'")
cursor.execute(set_search_path)  # set search path to the schema
print(f"Set search path to schema '{schemaName}'")
conn.commit()

for create_table in create_tables:
    cursor.execute(create_table)
conn.commit()
print("Finished creating tables")
