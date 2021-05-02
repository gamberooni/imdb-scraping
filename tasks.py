from bs4 import BeautifulSoup
from celery import Celery
from minio import Minio
import re
import requests
import io
import json
import logging
from conf import BUCKET_NAME, MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, RABBITMQ_URI, REDIS_URI
import dask

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


app = Celery('tasks', 
    backend=REDIS_URI, 
    broker=RABBITMQ_URI
    )

client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
    )

bucket_name = BUCKET_NAME
assert client.bucket_exists(bucket_name), f"Bucket '{bucket_name}' does not exist."

def getCrewData(url):
    crew_data = {
        "crew": []
    }
    r = requests.get(url=url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    #page title
    title = soup.find('title')
    crew_data["title"] = title.string
    cast_list = soup.find("table", {"class" : "cast_list"})

    trows = cast_list.find_all('tr')

    for tr in trows:
        td = tr.find_all('td')
        if len(td)==4:
            row = [i.text for i in td]
            crew_data["crew"].append({
                "name":re.sub("[^a-zA-Z' ]+", '', row[1]).strip(),
                "character":re.sub("[^a-zA-Z' ]+", '', row[3]).strip()
            })
    return crew_data

def getAllGenres():
    genres = []
    url = f"https://www.imdb.com/search/title/"
    r = requests.get(url=url, stream=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    res = soup.find_all("tbody")
    for r in res:
        r_td = r.find_all("td")
        for td in r_td:
            genre = td.find("input", {"name": "genres"})
            if genre:
                genres.append(genre.get("value"))
    return genres

@dask.delayed
def getMovieDetails(url, scrape_ts):
    logging.info(f"Getting details for {url}")
    data = {}
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    # scrape timestamp
    data["scrape_ts"] = scrape_ts

    # page title
    title = soup.title.string
    data["title"] = title
    # data["title"] = title.split(' - IMDb')[0]

    # title url
    data["url"] = url

    try:
        data["poster_url"] = soup.find("div", {"class": "poster"}).find('img')['src']
    except:
        data["poster_url"] = None
        logging.debug(f"Poster URL for {url} is None")

    # rating
    try:
        ratingValue = soup.find("span", {"itemprop" : "ratingValue"})
        data["ratingValue"] = ratingValue.string
    except:
        data["ratingValue"] = None
        logging.debug(f"Rating value is None for url {url}")

    # no of rating given
    try: 
        ratingCount = soup.find("span", {"itemprop" : "ratingCount"})
        data["ratingCount"] = ratingCount.string
    except:
        data["ratingCount"] = None
        logging.debug(f"Rating count is None for url {url}")        

    # name
    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
    data["name"] = titleName.contents[0].strip()
    # data["name"] = titleName.contents[0].replace(u'\xa0', u'')

    # is_series
    # check if the string "Episodes" is present
    try: 
        isSeries = soup.find("div", {"class": "article"}).find("h2")
        data["isSeries"] = True
    except:
        data["isSeries"] = False

    # duration
    try:
        data["duration"] = soup.find("time").string.strip()
    except:
        data["duration"] = None 
        logging.debug(f"Duration is None for url {url}")

    # genre
    try:
        data["genres"] = []
        genre = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[:-1]
        for g in genre:
            data["genres"].append(re.search(r">.*<\/a>", str(g)).group()[1:-4])
    except:
        data["genres"] = None
        logging.debug(f"Genres is None for url {url}")

    # release date
    try:
        release_date = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[-1]
        data["release_date"] = release_date.string.strip()
    except:
        data["release_date"] = None
        logging.debug(f"Release date is None for url {url}")

    # movie rated
    # subtext = soup.find("div", {"class": "subtext"})
    # print(f"subtext: {subtext}")
    # print(f"subtext text: {subtext.text}")
    # movie_rated = subtext.text.split()[0]

    # print(movie_rated)
    # # print(movie_rated.text.split())

    # data["movie_rated"] = movie_rated

    # summary
    try:
        summary_text = soup.find("div",{'class':'summary_text'})
        data["summary_text"] = summary_text.text.strip()
    except:
        data["summary_text"] = None
        logging.debug(f"Summary text is None for url {url}")

    try:
        credit_summary_item = soup.find_all("div",{'class':'credit_summary_item'})
        data["credits"] = {}
        for i in credit_summary_item:
            item = i.find("h4")
            names = i.find_all("a")
            data["credits"][item.string] = []
            for i in names:
                data["credits"][item.string].append({
                    "link": i["href"],
                    "name": i.string
                })
    except:
        data["credits"] = None
        logging.debug(f"Credits is None for url {url}")

    return data

@dask.delayed
def put_json(bucket_name, object_name, d):
    """
    jsonify a dict and write it as object to the bucket
    """
    # prepare data and corresponding data stream
    data = json.dumps(d).encode("utf-8")
    data_stream = io.BytesIO(data)
    data_stream.seek(0)

    # put data as object into the bucket
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream, 
        length=len(data),
        content_type="application/json"
    )

# @app.task
def writeToFile(chunk, object_name, scrape_ts):
    '''
    for each chunk (metadata of 5 titles in json format),
    dump them into one .json file and store that .json file
    in the folder which has the name of today's date
    '''
    title_list = []
    for link in chunk:  # loop thru all the 5 json data
        url = f"https://www.imdb.com{link}"
        title = getMovieDetails(url, scrape_ts)
        title_list.append(title)

    put_json(bucket_name, object_name, title_list)
