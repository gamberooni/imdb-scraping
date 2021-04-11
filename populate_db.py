from minio import Minio
import json
import io
import re
import psycopg2
from dbconf import *
from sql import *
import datetime
import time


conn = psycopg2.connect(host=HOSTNAME, port=PORT, database=DBNAME, user=USERNAME, password=PASSWORD)
cursor = conn.cursor()

cursor.execute(set_search_path)  # set search path to the schema
conn.commit()

client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password",
    secure=False,
)

BUCKET_NAME = "imdb"
if client.bucket_exists(BUCKET_NAME):  # if bucket exists
    print(f"Bucket '{BUCKET_NAME}' exists. Proceeding job.")
else:
    raise Exception(f"Bucket '{BUCKET_NAME}' does not exist. Aborting...")

FILE_PREFIX = "2021-04-11/"
# FILE_PREFIX = str(datetime.datetime.now().date())
objects = client.list_objects(bucket_name=BUCKET_NAME, prefix=FILE_PREFIX)

# def get_obj_filepaths(objects):
#     '''
#     Parameters
#     ----------
#     objects: MinIO Object
#         An iterator of Objects stored in MinIO Bucket
#     '''
#     filepaths = []
#     for obj in objects:
#     # {'_bucket_name': 'data', '_object_name': 'imdb/2021-04-03/anime_1.json', 
#     #   '_last_modified': datetime.datetime(2021, 3, 18, 1, 42, 59, 439000, tzinfo=datetime.timezone.utc), 
#     #   '_etag': '85951813368733551d7c8ada22923374', '_size': 118618497, '_metadata': {}, '_version_id': None, 
#     #   '_is_latest': None, '_storage_class': 'STANDARD', '_owner_id': '', '_owner_name': '', '_content_type': None}
#         if obj.object_name.split('.')[-1] == "json":
#             filepaths.append(f"{obj.bucket_name}/{obj.object_name}")  
#     return filepaths 

# filepaths = get_obj_filepaths(objects)
# print(filepaths)
start_time = time.time()  # for timing
for obj in objects:
    o = client.get_object(BUCKET_NAME, obj.object_name)
    data = json.load(io.BytesIO(o.data))
    data_dict = json.loads(data)
    # print(data_dict[0])
    # print(data_dict[0].keys())

    for item in data_dict:  # for each of the 5 anime titles
        # print(item)

        # directors table
        try:
            director_name = item["credits"]["Director:"][0]["name"]
            cursor.execute(insert_into_directors, (director_name,))
            conn.commit()
        except:
            pass


        # writers table
        try:
            writers = item["credits"]["Writers:"]
            for writer in writers:  # [{'link': '/name/nm2969426/', 'name': 'Isuna Hasekura'}, {'link': 'fullcredits#writers/', 'name': '1 more credit'}]
                if re.search(r"/name/", writer["link"]):
                    writer_name = writer["name"]
                    cursor.execute(insert_into_writers, (writer_name,))
                    conn.commit()            
        except:
            pass                 

        # stars table
        try:
            stars = item["credits"]["Stars:"]
            for star in stars:  # [{'link': '/name/nm1101677/', 'name': 'Jun Fukuyama'}, {'link': 'fullcredits/', 'name': 'See full cast & crew'}]
                if re.search(r"/name/", star["link"]):
                    star_name = star["name"]
                    cursor.execute(insert_into_stars, (star_name,))
                    conn.commit()   
        except:
            pass

        # genres table
        try:
            genres = item["genres"]
            for genre in genres:  # ['Animation', 'Adventure', 'Fantasy']
                cursor.execute(insert_into_genres, (genre,))
                conn.commit()   
        except:
            pass

        # titles table
        duration = item["duration"]
        is_series = item["isSeries"]
        name = item["title"].strip()
        try:
            rating_count = int(''.join(item["ratingCount"].split(',')))
        except:
            rating_count = None
        try:
            rating_value = item["ratingValue"]
        except:
            rating_value = None
        try:
            release_date = item["release_date"]
        except:
            release_date = None
        # movie_rated = item["movie_rated"]
        try:
            summary_text = item["summary_text"]
            summary_text = re.sub(r"\\n", "", summary_text)  # remove \n and \t 
            summary_text = summary_text.strip()  # remove leading and trailing white spaces
            summary_text = re.sub(r"\s{2,}", "", summary_text)  # remove white spaces that occur more than twice
            summary_text = summary_text.split("See full summary", 1)  # get everything before "See full summary"
            summary_text = summary_text[0]
            if "Add a Plot" in summary_text:
                summary_text = None
        except:
            summary_text = None

        cursor.execute(insert_into_titles, (duration, is_series, name, rating_count, rating_value, release_date, summary_text,))
        conn.commit()      

    # movie_rated
    # item["movie_rated"]  # need to fix

    # for d in data_dict:
    #     print(d.keys())
    #     print("\n")
    # print(json.dumps(data, indent=4, sort_keys=True))

print("--- Job took %s seconds ---" % (time.time() - start_time))
