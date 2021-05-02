from bs4 import BeautifulSoup
import requests
import time
import math
import multiprocessing as mp
import logging
import datetime
from tasks import writeToFile
from prefect import task, Flow
import prefect

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

def getAnimeLinks(process_name, tasks, results):
    '''
    get all the links of all titles that has the keyword "anime"
    of a particular page
    '''
    logging.info('[%s] evaluation routine starts' % process_name)

    links = []
    while True:  # break loop if the argument from the queue is -1
        page = tasks.get()
        if page < 0:  # to indicate finished
            logging.info('[%s] evaluation routine quits' % process_name)
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

@task
def getAllAnimeLinks(num_processes, tasks, results, start_page=1, end_page=None):

    logger = prefect.context.get("logger")

    all_links = []

    if end_page == None:  # if end_page is not specified then scrape all pages
        end_page = getTotalPages()

    logging.info(f"Getting anime links from page {start_page} to page {end_page}.")
    
    for p in range(start_page, end_page+1):
        tasks.put(p)

    all_links = kill_mp(num_processes, tasks, results)  # kill the processes and get the results

    logger.info("Finished getting all anime links!")

    return all_links    


def kill_mp(num_processes, tasks, results):
    # Quit the worker processes by sending them -1
    for i in range(num_processes):
        tasks.put(-1)

    num_finished_processes = 0
    to_return = []
    while True:  # infinite loop until all processes are killed
        r = results.get()
        # Have a look at the results
        if r == -1:  # if the value of the argument in the queue is -1
            num_finished_processes += 1

            if num_finished_processes == num_processes:
                break
        else:
            # Output result
            to_return.append(r)
    
    return to_return

@task(nout=3)
def init_mp(target_func):
    logger = prefect.context.get("logger")

    manager = mp.Manager()
    # Define a list (queue) for tasks and computation results
    tasks = manager.Queue()
    results = manager.Queue()
    num_processes = mp.cpu_count() * 2 # number of processes = double of the number of cpus available

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

    logger.info(f"Initialized multiprocessing for function '{target_func}' with {num_processes} processes")

    return num_processes, tasks, results    

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
        num_processes, tasks, results = init_mp(getAnimeLinks)
        all_links = getAllAnimeLinks(num_processes, tasks, results)
        merged_all_links = concat_all_links(all_links)

        # go to each url to do scraping, then upload to MinIO
        object_prefix = str(datetime.datetime.now().date())  # e.g. 2021-04-03
        scrapeAndUpload(merged_all_links, object_prefix)

    flow.register("imdb-scraping")
    # flow.run()


if __name__ == "__main__":
    main()
