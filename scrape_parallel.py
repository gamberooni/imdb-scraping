from bs4 import BeautifulSoup
import requests
import time
import math
import multiprocessing as mp
import logging
import datetime
from tasks import writeToFile
import itertools

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

def getAnimeLinks(process_name, tasks, results):
    '''
    get all the links of all titles that has the keyword "anime"
    of a particular page
    '''
    logging.info('[%s] evaluation routine starts' % process_name)
    links = []
    while True:
        page = tasks.get()
        if page < 0:  # to indicate finished
            logging.info('[%s] evaluation routine quits' % process_name)
                # Indicate finished
            results.put(-1)
            break
        else:
            logging.info(f"Scraping page {page}...")
            url = f"https://www.imdb.com/search/keyword/?keywords=anime&page={page}"
            r = requests.get(url=url, stream=True)
            soup = BeautifulSoup(r.text, 'html.parser')
            res = soup.find_all("div",{"class":"lister-item mode-detail"})
            if res:
                for r in res:
                    links.append(r.find("a")['href'])

            # Add result to the queue
            results.put(links)                    

    return

def getAllAnimeLinks(start_page=1, end_page=None):
    all_links = []

    if end_page == None:  # if end_page is not specified then scrape all pages
        end_page = getTotalPages()

    logging.info(f"Getting anime links from page {start_page} to page {end_page}")
    
    for p in range(start_page, end_page+1):
        tasks.put(p)

    all_links = kill_mp(num_processes, tasks, results)

    logging.info("Finished getting all anime links!")

    return all_links    


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


def init_mp(target_func):
    manager = mp.Manager()
    # Define a list (queue) for tasks and computation results
    tasks = manager.Queue()
    results = manager.Queue()

    num_processes = mp.cpu_count()
    pool = mp.Pool(processes=num_processes)
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
        new_process.start() 

    return processes, num_processes, tasks, results    

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


if __name__ == "__main__":

    start_time = time.time()  # for timing

    processes, num_processes, tasks, results = init_mp(getAnimeLinks)
    all_links = getAllAnimeLinks()
    concat_all_links = []
    for i, links in enumerate(all_links):
        concat_all_links += links  # merge all the lists into one list

    concat_all_links = list(set(concat_all_links))

    object_prefix = str(datetime.datetime.now().date())  # e.g. 2021-04-03
    scrapeAndUpload(concat_all_links, object_prefix)

    logging.info("--- Job took %s seconds ---" % (time.time() - start_time))
