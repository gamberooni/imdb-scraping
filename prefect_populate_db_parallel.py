from conf import POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
from conf import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME
from bs4 import BeautifulSoup
from minio import Minio
from prefect import task, Flow, Parameter
from sql import *
import datetime
import io
import json
import logging
import multiprocessing as mp
import prefect
import psycopg2
import re
import requests
import dask 

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def get_born_date(link):  
    url = f"https://www.imdb.com{link}"
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, 'html.parser')  # Create a BeautifulSoup object
    
    try:
        born_date = soup.find("time").text.split(',')
        born_year = int(born_date[-1].strip())
        born_month = born_date[0].strip().split(' ')[0]
        born_day = int(born_date[0].strip().split(' ')[-1])
    except:
        born_year = None
        born_month = None
        born_day = None
    
    return born_year, born_month, born_day

def populate_db(object_name):

    conn = psycopg2.connect(
        host=POSTGRES_HOSTNAME, 
        port=POSTGRES_PORT, 
        database=POSTGRES_DATABASE, 
        user=POSTGRES_USER, 
        password=POSTGRES_PASSWORD
        )
    cursor = conn.cursor()

    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    logging.info(f"Processing object: {object_name}")
    o = client.get_object(BUCKET_NAME, object_name)
    data = json.load(io.BytesIO(o.data))

    for item in data:  # for each of the 5 anime titles
        # titles table
        scrape_ts = item["scrape_ts"]

        duration = item["duration"]  
        if duration is not None:
            if re.search(r"h", duration) and re.search(r"min", duration):   # 1h 26min
                duration_hour = int(duration.split('h')[0])
                duration_minute = int(duration.split('h')[-1].replace('min', '').strip())        
            elif re.search(r"h", duration):                                 # 2h
                duration_hour = int(duration.replace('h', '').strip())
                duration_minute = 0
            else:                                                           # 26min
                duration_hour = 0
                duration_minute = int(duration.replace('min', '').strip())
            duration = duration_hour * 60 + duration_minute

        is_series = item["isSeries"]

        name = item["title"]

        url = item["url"]

        poster_url = item["poster_url"]

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

        try:
            release_year = int(re.findall(r'\d{4}', release_date)[0])
        except:
            release_year = None
        
        # movie_rated = item["movie_rated"]

        try:
            summary_text = item["summary_text"]
            if re.search(r"See full summary", summary_text):
                summary_text = re.sub(r"\s{2,}", "", summary_text)  # remove white spaces that occur more than twice
                summary_text = summary_text.split("See full summary", 1)  # get everything before "See full summary"
                summary_text = summary_text[0]
            # summary_text = re.sub(r"\\n", "", summary_text)  # remove \n and \t 
            # summary_text = summary_text.strip()  # remove leading and trailing white spaces
            if "Add a Plot" in summary_text:
                summary_text = None
        except:
            summary_text = None

        cursor.execute(insert_into_titles, 
            (scrape_ts, 
            duration, 
            is_series, 
            name, 
            url, 
            poster_url, 
            rating_count, 
            rating_value, 
            release_date, 
            release_year, 
            summary_text,))
        conn.commit()

        # directors table
        try:
            director_name = item["credits"]["Director:"][0]["name"]
            director_link = item["credits"]["Director:"][0]["link"]
            born_year, born_month, born_day = get_born_date(director_link)
            cursor.execute(insert_into_directors, (director_name,born_year,born_month,born_day,))
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
                    writer_link = writer["link"]
                    born_year, born_month, born_day = get_born_date(writer_link)
                    cursor.execute(insert_into_writers, (writer_name,born_year,born_month,born_day,))
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
                    star_link = star["link"]
                    born_year, born_month, born_day = get_born_date(star_link)

                    # insert into stars
                    cursor.execute(insert_into_stars, (star_name,born_year,born_month,born_day,))
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

    return

@task
def start_populate(object_prefix):

    logger = prefect.context.get("logger")

    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    if client.bucket_exists(BUCKET_NAME):  # if bucket exists
        logger.info(f"Bucket '{BUCKET_NAME}' exists. Proceeding job.")
    else:
        raise Exception(f"Bucket '{BUCKET_NAME}' does not exist. Aborting...")

    logger.info("Listing objects from bucket")
    objects = client.list_objects(bucket_name=BUCKET_NAME, prefix=object_prefix+"/")

    logger.info("Waiting for populate database job to complete...")

    object_names = []
    for o in objects:
        object_names.append(o.object_name)

    dask.compute([dask.delayed(populate_db)(obj) for obj in object_names], scheduler="processes",)
    
    logger.info("Finished populating database!")


def main():

    with Flow("populate_db") as flow:

        # OBJECT_PREFIX = "2021-04-19/"
        object_prefix = Parameter('object_prefix', default=str(datetime.datetime.now().date()))
        start_populate(object_prefix)

    flow.register("imdb-scraping")
    flow.run()


if __name__ == "__main__":
    main()
