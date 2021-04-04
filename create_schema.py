import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from dbconf import *
from utils import *
from minio import Minio
import json
import io


client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password",
    secure=False,
)

conn = psycopg2.connect(host=HOSTNAME, port=PORT, database=DBNAME, user=USERNAME, password=PASSWORD)
cursor = conn.cursor()

schemaName = "imdb"
drop_schema_if_exists(schemaName, conn, cursor)
create_schema(schemaName, conn, cursor)  # create the schema
# upload_files(current_dir, DB_URI)


create_director_table = f"CREATE TABLE IF NOT EXISTS {schemaName}.directors (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(50) NOT NULL,);"

create_stars_table = f"CREATE TABLE IF NOT EXISTS {schemaName}.stars (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(50) NOT NULL,);"

create_writers_table = f"CREATE TABLE IF NOT EXISTS {schemaName}.writers (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(50) NOT NULL,);"

create_genres_table = f"CREATE TABLE IF NOT EXISTS {schemaName}.genres (
                            id SERIAL PRIMARY KEY,
                            genre1 VARCHAR(50) NOT NULL,);"

create_titles_table = f"CREATE TABLE IF NOT EXISTS {schemaName}.titles (
                            id SERIAL PRIMARY KEY,
                            director_id INT,
                            stars_id INT,
                            writers_id INT,
                            genres_id SMALLINT,
                            duration SMALLINT,
                            is_series BOOLEAN,
                            movie_rated VARCHAR(10),
                            name VARCHAR(50) NOT NULL,
                            rating_count INT,
                            rating_value FLOAT(2),
                            release_date VARCHAR(15),
                            summary_text VARCHAR,);"

BUCKET_NAME = "imdb"
found = client.bucket_exists(BUCKET_NAME)
if found:
    print(f"Bucket '{BUCKET_NAME}' exists. Proceeding job.")
else:
    raise Exception(f"Bucket '{BUCKET_NAME}' does not exist. Aborting...")

FILE_PREFIX = "2021-04-04/"
objects = client.list_objects(bucket_name=BUCKET_NAME, prefix=FILE_PREFIX)

def get_obj_filepaths(objects):
    '''
    Parameters
    ----------
    objects: MinIO Object
        An iterator of Objects stored in MinIO Bucket
    '''
    filepaths = []
    for obj in objects:
    # {'_bucket_name': 'data', '_object_name': 'imdb/2021-04-03/anime_1.json', 
    #   '_last_modified': datetime.datetime(2021, 3, 18, 1, 42, 59, 439000, tzinfo=datetime.timezone.utc), 
    #   '_etag': '85951813368733551d7c8ada22923374', '_size': 118618497, '_metadata': {}, '_version_id': None, 
    #   '_is_latest': None, '_storage_class': 'STANDARD', '_owner_id': '', '_owner_name': '', '_content_type': None}
        if obj.object_name.split('.')[-1] == "json":
            filepaths.append(f"{obj.bucket_name}/{obj.object_name}")  
    return filepaths 

# filepaths = get_obj_filepaths(objects)
# print(filepaths)
for obj in objects:
    o = client.get_object(BUCKET_NAME, obj.object_name)
    data = json.load(io.BytesIO(o.data))
    data_dict = json.loads(data)
    for d in data_dict:
        print(d.keys())
        print("\n")
    # print(json.dumps(data, indent=4, sort_keys=True))
