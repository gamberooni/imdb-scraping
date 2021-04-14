from minio import Minio
import json
import io
import re
import psycopg2
from conf import POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
from conf import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from sql import *
import logging
import time


conn = psycopg2.connect(
    host=POSTGRES_HOSTNAME, 
    port=POSTGRES_PORT, 
    database=POSTGRES_DATABASE, 
    user=POSTGRES_USER, 
    password=POSTGRES_PASSWORD
    )
cursor = conn.cursor()

cursor.execute(set_search_path)  # set search path to the schema
conn.commit()

client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

bucket_name = os.getenv('BUCKET_NAME', "imdb")  
if client.bucket_exists(bucket_name):  # if bucket exists
    logging.info(f"Bucket '{bucket_name}' exists. Proceeding job.")
else:
    raise Exception(f"Bucket '{bucket_name}' does not exist. Aborting...")

FILE_PREFIX = "2021-04-14/"
# FILE_PREFIX = str(datetime.datetime.now().date())
objects = client.list_objects(bucket_name=bucket_name, prefix=FILE_PREFIX)

start_time = time.time()  # for timing
for obj in objects:
    o = client.get_object(bucket_name, obj.object_name)
    data = json.load(io.BytesIO(o.data))

    for item in data:  # for each of the 5 anime titles

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

        # directors table
        try:
            director_name = item["credits"]["Director:"][0]["name"]
            cursor.execute(insert_into_directors, (director_name,))
            conn.commit()       
        except:
            director_name = None

        # insert into titles_directors
        cursor.execute(insert_into_titles_directors, (name, director_name,))
        conn.commit()                 

        # writers table
        try:
            writers = item["credits"]["Writers:"]
            for writer in writers:  # [{'link': '/name/nm2969426/', 'name': 'Isuna Hasekura'}, {'link': 'fullcredits#writers/', 'name': '1 more credit'}]
                if re.search(r"/name/", writer["link"]):
                    writer_name = writer["name"]
                    cursor.execute(insert_into_writers, (writer_name,))
                    conn.commit()     

                    # insert into titles_writers
                    cursor.execute(insert_into_titles_writers, (name, writer_name,))
                    conn.commit()                               
        except:
            pass                 

        # stars and titles_stars table
        try:
            stars = item["credits"]["Stars:"]
            for star in stars:  # [{'link': '/name/nm1101677/', 'name': 'Jun Fukuyama'}, {'link': 'fullcredits/', 'name': 'See full cast & crew'}]
                if re.search(r"/name/", star["link"]):
                    star_name = star["name"]
                    # insert into stars
                    cursor.execute(insert_into_stars, (star_name,))
                    conn.commit()   

                    # insert into titles_stars
                    cursor.execute(insert_into_titles_stars, (name, star_name,))
                    conn.commit()                            
        except:
            pass

        # genres table
        try:
            genres = item["genres"]
            for genre in genres:  # ['Animation', 'Adventure', 'Fantasy']
                cursor.execute(insert_into_genres, (genre,))
                conn.commit()   

                # insert into titles_genres
                cursor.execute(insert_into_titles_genres, (name, genre,))
                conn.commit()                    
        except:
            pass

    # movie_rated
    # item["movie_rated"]  # need to fix

    # for d in data_dict:
    #     print(d.keys())
    #     print("\n")
    # print(json.dumps(data, indent=4, sort_keys=True))

print("--- Job took %s seconds ---" % (time.time() - start_time))
