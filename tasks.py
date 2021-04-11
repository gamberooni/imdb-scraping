from celery import Celery
import json
import requests
from bs4 import BeautifulSoup

app = Celery('write_to_file', 
                backend='redis://127.0.0.1:6379', 
                broker='amqp://admin:password@localhost:5672')

# @app.task
# def gen_prime(x):
#     multiples = []
#     results = []
#     for i in range(2, x+1):
#         if i not in multiples:
#             results.append(i)
#             for j in range(i*i, x+1, i):
#                 multiples.append(j)
#     return results

def getMovieDetails(url):
    data = {}
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    # page title
    title = soup.title
    data["title"] = title.string

    # rating
    try:
        ratingValue = soup.find("span", {"itemprop" : "ratingValue"})
        data["ratingValue"] = ratingValue.string
    except:
        data["ratingValue"] = None
        print(f"Rating value is None for url {url}")

    # no of rating given
    try: 
        ratingCount = soup.find("span", {"itemprop" : "ratingCount"})
        data["ratingCount"] = ratingCount.string
    except:
        data["ratingCount"] = None
        print(f"Rating count is None for url {url}")        

    # name
    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
    data["name"] = titleName.contents[0].replace(u'\xa0', u'')

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
        print(f"Duration is None for url {url}")

    # genre
    try:
        data["genres"] = []
        genre = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[:-1]
        for g in genre:
            data["genres"].append(re.search(r">.*<\/a>", str(g)).group()[1:-4])
    except:
        data["genres"] = None
        print(f"Genres is None for url {url}")

    # release date
    try:
        release_date = soup.find("div", {"class": "subtext"}).find_all("a", href=True)[-1]
        data["release_date"] = release_date.string.strip()
    except:
        data["release_date"] = None
        print(f"Release date is None for url {url}")

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
        data["summary_text"] = summary_text.text
    except:
        data["summary_text"] = None
        print(f"Summary text is None for url {url}")

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
        print(f"Credits is None for url {url}")

    return data

# @app.task
# def writeToFile(chunks, folderName):
#     '''
#     for each chunk (metadata of 5 titles in json format),
#     dump them into one .json file and store that .json file
#     in the folder which has the name of today's date
#     '''
#     for count, chunk in enumerate(chunks):  # each chunk has 5 json data
#         filename = f"{folderName}/anime_{count}.json"
#         print(f"Writing to file '{filename}")
#         json_list = []
#         with open(filename, 'w', encoding='utf-8') as f:
#             for i, c in enumerate(chunk):  # loop thru all the 5 json data
#                 url = f"https://www.imdb.com{c}"
#                 json_list.append(getMovieDetails(url))
#                 # movie_details = getMovieDetails(url)
#                 # json.dump(movie_details, f, sort_keys=True, indent=4)
#             movie_details = json.dumps(json_list)
#             json.dump(movie_details, f, sort_keys=True, indent=4)

@app.task
def writeToFile(chunk, filename):
    '''
    for each chunk (metadata of 5 titles in json format),
    dump them into one .json file and store that .json file
    in the folder which has the name of today's date
    '''
    json_list = []
    with open(filename, 'w', encoding='utf-8') as f:
        for c in chunk:  # loop thru all the 5 json data
            url = f"https://www.imdb.com{c}"
            json_list.append(getMovieDetails(url))
            # movie_details = getMovieDetails(url)
            # json.dump(movie_details, f, sort_keys=True, indent=4)
        movie_details = json.dumps(json_list)
        json.dump(movie_details, f, sort_keys=True, indent=4)

    # refactor this into no need to dump into file
    # wrap json data of 5 titles into one json object, then upload to minio immediately
    return 1    

# @app.task
# def getAllAnimeLinks(start_page=1):
#     '''
#     get all the links of all titles that has the keyword "anime"
#     by browsing page by page in imdb's search page
#     '''
#     i = start_page
#     links = []
#     while True:
#         print(f"Scraping page {i}...")
#         url = f"https://www.imdb.com/search/keyword/?keywords=anime&page={i}"
#         r = requests.get(url=url, stream=True)
#         soup = BeautifulSoup(r.text, 'html.parser')
#         res = soup.find_all("div",{"class":"lister-item mode-detail"})
#         if res:
#             for r in res:
#                 links.append(r.find("a")['href'])
#             i += 1
#         else:
#             print("No more links left...")
#             break
#     return links            
    
@app.task
def getAnimeLinks(page):
    '''
    get all the links of all titles that has the keyword "anime"
    of a particular page
    '''
    links = []
    print(f"Scraping page {page}...")
    url = f"https://www.imdb.com/search/keyword/?keywords=anime&page={page}"
    r = requests.get(url=url, stream=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    res = soup.find_all("div",{"class":"lister-item mode-detail"})
    if res:
        for r in res:
            links.append(r.find("a")['href'])

    return links            