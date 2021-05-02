from bs4 import BeautifulSoup
import requests
import time
import math
import multiprocessing as mp
import logging
import datetime
from tasks import writeToFile
from prefect import task, Flow, Parameter
import prefect
import dask

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def getTotalPages():
    url = f"https://www.imdb.com/search/keyword/?keywords=anime&page=1"
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, 'html.parser')  # Create a BeautifulSoup object

    # number of titles in one page
    titlesInOnePage = int(soup.find("span", {"class": "lister-current-last-item"}).string)  # 50
    tmp = soup.find("div", {"class": "desc"}).text  # 1 to 50 of 6,879 titles
    
     # ['\n1 to\n            50\n            ', ' 6,879 titles\n    | Next »\n']
    tmp = tmp.split('of')[-1]
    tmp = tmp.split('titles')[0].strip()
    totalCount = int(''.join(tmp.split(',')))  # 6879

    return math.ceil(totalCount / titlesInOnePage)

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

@task
def getAllAnimeLinks(start_page=1, end_page=None):

    logger = prefect.context.get("logger")

    if end_page == None:  # if end_page is not specified then scrape all pages
        end_page = getTotalPages()

    logging.info(f"Getting anime links from page {start_page} to page {end_page}")

    links = dask.compute(
        [dask.delayed(getAnimeLinks)(p) for p in range(start_page, end_page+1)],
        scheduler="processes",
    )  # returns as tuple

    logger.info("Finished getting all anime links!")

    return links[0]    

@task
def scrapeAndUpload(all_links, object_prefix):
    logger = prefect.context.get("logger")
    logger.info("Scrape and upload data to MinIO...")
    
    # from the whole list of the links of all titles, 
    # put 5 titles' metadata into one chunk
    chunks = [all_links[x:x+5] for x in range(0, len(all_links), 5)]

    # scrape timestamp
    now = datetime.datetime.now()
    scrape_ts = now.strftime("%Y-%m-%d %H:%M:%S")  # time when the scraping starts for all 

    for count, chunk in enumerate(chunks):  # each chunk has 5 json data
        object_name = f"{object_prefix}/anime_{count}.json"
        logger.info(f"Writing to object '{object_name}")

        # find out how to do this 
        # dask.compute(dask.delayed(writeToFile)(chunk, object_name, scrape_ts), scheduler="processes")

        upload = writeToFile.delay(chunk, object_name, scrape_ts)  # use celery to do parallel processing

    logger.info("Waiting for Celery to finish the processing...")
    upload = upload.wait(timeout=None, interval=0.5)  # force wait

@task
def concat_all_links(all_links):

    logger = prefect.context.get("logger")

    merged_all_links = []
    for i, links in enumerate(all_links):
        merged_all_links += links  # merge all the lists into one list
    merged_all_links = list(set(merged_all_links))

    logger.info("Concatenated and performed deduplication on all links")

    return merged_all_links

def main():

    with Flow("scrape") as flow:
        # get all the links so that I know which url to scrape from
        # num_processes, tasks, results = init_mp(getAnimeLinks)
        all_links = getAllAnimeLinks()
        merged_all_links = concat_all_links(all_links)

        # go to each url to do scraping, then upload to MinIO
        object_prefix = Parameter('object_prefix', default=str(datetime.datetime.now().date()))  # e.g. 2021-04-03/
        scrapeAndUpload(merged_all_links, object_prefix)

    flow.register("imdb-scraping")
    # flow.run()


if __name__ == "__main__":
    main()
