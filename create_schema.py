import psycopg2
import os
from dbconf import *
from sql import *

conn = psycopg2.connect(host=HOSTNAME, port=PORT, database=DBNAME, user=USERNAME, password=PASSWORD)
cursor = conn.cursor()

cursor.execute(drop_schema)  # drop the schema if exists
cursor.execute(create_schema)  # create the schema
cursor.execute(set_search_path)  # set search path to the schema
conn.commit()

for create_table in create_tables:
    cursor.execute(create_table)
conn.commit()
print("Finished creating tables")
