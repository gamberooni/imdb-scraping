from minio import Minio
import json
import io
import re
import psycopg2
from conf import POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
from conf import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME
from sql import *
import logging
import time
import multiprocessing as mp
import requests
from bs4 import BeautifulSoup
import datetime


def init_mp(target_func):
    manager = mp.Manager()
    # Define a list (queue) for tasks and computation results
    tasks = manager.Queue()
    results = manager.Queue()
    num_processes = mp.cpu_count() * 2

    processes = []
    # Initiate the worker processes
    for i in range(num_processes):

        # Set process name
        process_name = 'P%i' % i

        # Create the process, and connect it to the worker function
        new_process = mp.Process(target=target_func, args=(process_name,tasks,results))

        # Add new process to the list of processes
        processes.append(new_process)

    # Start the process
    for process in processes:
        process.start()         

    return num_processes, tasks, results    

def kill_mp(num_processes, tasks, results):
    # Quit the worker processes by sending them -1
    for i in range(num_processes):
        tasks.put(-1)

    num_finished_processes = 0
    to_return = []
    while True:
        r = results.get()
        # Have a look at the results
        if r == -1:
            # Process has finished
            num_finished_processes += 1

            if num_finished_processes == num_processes:
                break
        else:
            # Output result
            to_return.append(r)
    
    return to_return

def get_born_date(link):  
    url = f"https://www.imdb.com{link}"
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')
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

def populate_db(process_name, tasks, results):

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

    bucket_name = BUCKET_NAME

    logging.info('[%s] evaluation routine starts' % process_name)            
    while True:
        object_name = tasks.get()
        if not isinstance(object_name, str):  # to indicate finished
            logging.info('[%s] evaluation routine quits' % process_name)
            results.put(-1)
            break
        else:
            logging.info(f"Processing object: {object_name}")
            o = client.get_object(bucket_name, object_name)
            data = json.load(io.BytesIO(o.data))

            for item in data:  # for each of the 5 anime titles

                # titles table
                now = datetime.datetime.now()
                scrape_ts = now.strftime("%Y-%m-%d %H:%M:%S")
                duration = item["duration"]  
                if duration is not None:
                    if re.search(r"h", duration) and re.search(r"min", duration):  # 1h 26min
                        duration_hour = int(duration.split('h')[0])
                        duration_minute = int(duration.split('h')[-1].replace('min', '').strip())        
                    elif re.search(r"h", duration):  # 2h
                        duration_hour = int(duration.replace('h', '').strip())
                        duration_minute = 0
                    else:  # 26min
                        duration_hour = 0
                        duration_minute = int(duration.replace('min', '').strip())
                    duration = duration_hour * 60 + duration_minute
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

                cursor.execute(insert_into_titles, (scrape_ts, duration, is_series, name, rating_count, rating_value, release_date, summary_text,))
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

            results.put(1)    

    return

def start_populate(object_prefix, num_processes, tasks, results):
    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    bucket_name = BUCKET_NAME

    if client.bucket_exists(bucket_name):  # if bucket exists
        logging.info(f"Bucket '{bucket_name}' exists. Proceeding job.")
    else:
        raise Exception(f"Bucket '{bucket_name}' does not exist. Aborting...")

    objects = client.list_objects(bucket_name=bucket_name, prefix=object_prefix)
    object_names = []
    for o in objects:
        object_names.append(o.object_name)

    for obj in object_names:  
        tasks.put(obj)

    _ = kill_mp(num_processes, tasks, results)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    start_time = time.time()  # for timing

    num_processes, tasks, results = init_mp(populate_db)
    OBJECT_PREFIX = "2021-04-18/"
    # OBJECT_PREFIX = str(datetime.datetime.now().date())
    start_populate(OBJECT_PREFIX, num_processes, tasks, results)

    logging.info("--- Job took %s seconds ---" % (time.time() - start_time))
