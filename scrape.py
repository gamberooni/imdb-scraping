from bs4 import BeautifulSoup
from tasks import getMovieDetails, writeToFile
import datetime
import logging
import math 
import itertools
import requests
import time
import json


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def getTotalPages():
    url = f"https://www.imdb.com/search/keyword/?keywords=anime&page=1"
    r = requests.get(url=url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')
    countInOnePage = int(soup.find("span", {"class": "lister-current-last-item"}).string)
    tmp = soup.find("div", {"class": "desc"}).text
    # 1 to 50 of 6,879 titles
     # ['\n1 to\n            50\n            ', ' 6,879 titles\n    | Next »\n']
    tmp = tmp.split('of')[-1]
    tmp = tmp.split('titles')[0].strip()
    totalCount = int(''.join(tmp.split(',')))
    return math.ceil(totalCount / countInOnePage)

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

def getAllAnimeLinks(start_page=1, end_page=None):
    all_links = []

    if end_page == None:  # if end_page is not specified then scrape all pages
        end_page = getTotalPages()

    logging.info(f"Getting anime links from page {start_page} to page {end_page}")
    
    for p in range(start_page, end_page+1):
        links = getAnimeLinks(p)
        all_links.append(links)
    
    all_links = list(itertools.chain(*all_links))  # merge all the lists into one list

    logging.info("Finished getting all anime links!")

    return all_links

def scrapeAndUpload(all_links, object_prefix):
    logging.info("Scrape and upload data to MinIO...")
    
    # from the whole list of the links of all titles, 
    # put 5 titles' metadata into one chunk
    chunks = [all_links[x:x+5] for x in range(0, len(all_links), 5)]

    for count, chunk in enumerate(chunks):  # each chunk has 5 json data
        object_name = f"{object_prefix}/anime_{count}.json"
        logging.info(f"Writing to object '{object_name}")
        upload = writeToFile.delay(chunk, object_name)  # use celery to do parallel processing
    upload = upload.wait(timeout=None, interval=0.5)  # force wait


# start_time = time.time()  # for timing

# all_links = getAllAnimeLinks()
# object_prefix = str(datetime.datetime.now().date())  # e.g. 2021-04-03
# scrapeAndUpload(all_links, object_prefix)

# logging.info("--- Job took %s seconds ---" % (time.time() - start_time))


aot_url = "https://www.imdb.com/title/tt2560140/"
dsmugen_url = "https://www.imdb.com/title/tt11032374/"
# test_url = "https://www.imdb.com/title/tt13370404/"

# details1 = getMovieDetails(test_url)
# details2 = getMovieDetails(dsmugen_url)
# details_list = []
# details_list.append(details1)
# details_list.append(details2)

# details = getMovieDetails(aot_url)
# # # print(type(details))
# print(json.dumps(details, sort_keys=True, indent=4))  # to pretty print


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

star_link = "/name/nm2569233/"
born_year, born_month, born_day = get_born_date(star_link)

# crew = getCrewData(dsmugen_url)
# print(json.dumps(dsmugen_crew, sort_keys=True, indent=4))  
