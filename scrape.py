import requests
from bs4 import BeautifulSoup
import json
from minio import Minio
import re
import os
import datetime
import shutil


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

def getMovieDetails(url):
    data = {}
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    # page title
    title = soup.title
    data["title"] = title.string

    # rating
    ratingValue = soup.find("span", {"itemprop" : "ratingValue"})
    data["ratingValue"] = ratingValue.string

    # no of rating given
    ratingCount = soup.find("span", {"itemprop" : "ratingCount"})
    data["ratingCount"] = ratingCount.string

    # name
    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
    data["name"] = titleName.contents[0].replace(u'\xa0', u'')

    # is_series
    # check if the string "Episodes" is present
    isSeries = soup.find("div", {"class": "article"}).find("h2")
    if isSeries:
        data["isSeries"] = True
    else:
        data["isSeries"] = False

    # duration
    data["duration"] = soup.find("time").string.strip()

    # genre
    data["genre"] = []
    genre = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[:-1]
    for g in genre:
        data["genre"].append(re.search(r">.*<\/a>", str(g)).group()[1:-4])

    # release date
    release_date = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[-1]
    data["release_date"] = release_date.string.strip()

    # movie rated
    subtext = soup.find("div", {"class": "subtext"})
    movie_rated = subtext.text.split()[0]
    # print(movie_rated.text.split())
    data["movie_rated"] = movie_rated

    # summary
    summary_text = soup.find("div",{'class':'summary_text'})
    data["summary_text"] = summary_text.string.strip()

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
    return data

aot_url = "https://www.imdb.com/title/tt2560140/"
dsmugen_url = "https://www.imdb.com/title/tt11032374/"

# data = {}
# r = requests.get(url=aot_url)
# # Create a BeautifulSoup object
# soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.find_all('rating'))

details = getMovieDetails(dsmugen_url)
print(json.dumps(details, sort_keys=True, indent=4))  # to pretty print

# crew = getCrewData(dsmugen_url)
# print(json.dumps(dsmugen_crew, sort_keys=True, indent=4))  

def getAllAnimeTitles(start_page=0):
    i = start_page
    titles = []
    while True:
        print(f"Scraping page {i}...")
        anime_url = f"https://www.imdb.com/search/keyword/?keywords=anime&page={i}"
        r = requests.get(url=url, stream=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        res = soup.find_all("div",{"class":"lister-item mode-detail"})
        if res:
            for r in res:
                titles.append(r.find_all("a")[1].string)
            i += 1
        else:
            print("No more titles left...")
            break
    return titles

def getAllAnimeLinks(start_page=0):
    '''
    get all the links of all titles that has the keyword "anime"
    by browsing page by page in imdb's search page
    '''
    i = start_page
    links = []
    while True:
        print(f"Scraping page {i}...")
        url = f"https://www.imdb.com/search/keyword/?keywords=anime&page={i}"
        r = requests.get(url=url, stream=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        res = soup.find_all("div",{"class":"lister-item mode-detail"})
        if res:
            for r in res:
                links.append(r.find("a")['href'])
            i += 1
        else:
            print("No more links left...")
            break
    return links

def writeToFile(chunks, folderName):
    '''
    for each chunk (metadata of 5 titles in json format),
    dump them into one .json file and store that .json file
    in the folder which has the name of today's date
    '''
    for count, chunk in enumerate(chunks):  # each chunk has 5 json data
        filename = f"{folderName}/anime_{count}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            for i, c in enumerate(chunk):  # loop thru all the 5 json data
                url = f"https://www.imdb.com{c}"
                movie_details = getMovieDetails(url)
                json.dump(movie_details, f, sort_keys=True, indent=4)

def uploadToMinio(bucketName, folderName):
    '''
    upload all the .json files in the folder to minio
    '''
    for filename in os.listdir(folderName):
        if filename.endswith(".json"):
            f = os.path.join(folderName, filename)
            client.fput_object(bucketName, f, f)
        else:
            continue

folderName = str(datetime.datetime.now().date())  # e.g. 2021-04-03
try:
    os.mkdir(folderName)  # will throw exception if the folder already exists
except:
    shutil.rmtree(folderName)  # delete the folder and recreate it
    os.mkdir(folderName)

# client = Minio(
#     "localhost:9000",
#     access_key="admin",
#     secret_key="password",
#     secure=False,
# )

# bucketName = "imdb"
# assert client.bucket_exists(bucketName), f"Bucket '{bucketName}' does not exist."

# links = getAllAnimeLinks(138)
# # from the whole list of the links of all titles, put 5 titles' metadata into one chunk
# chunks = [links[x:x+5] for x in range(0, len(links), 5)]  
# writeToFile(chunks, folderName) 
# uploadToMinio(bucketName, folderName)            

# r = requests.get(url="https://www.imdb.com/search/keyword/?keywords=anime&page=1", stream=True)
# soup = BeautifulSoup(r.text, 'html.parser')
# res = soup.find_all("div",{"class":"lister-item mode-detail"})
# titles = []
# for r in res:
#     titles.append(r.find("a")['href'])
# print(titles)
