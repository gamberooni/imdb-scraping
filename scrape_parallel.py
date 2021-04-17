from bs4 import BeautifulSoup
import requests
import time
import math
import multiprocessing as mp
import logging

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
        # links = getAnimeLinks(p)
        # all_links.append(links)

    # # Quit the worker processes by sending them -1
    # for i in range(num_processes):
    #     tasks.put(-1)

    # num_finished_processes = 0
    # while True:
    #     all_links = results.get()
    #     # Have a look at the results
    #     if all_links == -1:
    #         # Process has finished
    #         num_finished_processes += 1

    #         if num_finished_processes == num_processes:
    #             break
    #     else:
    #         # Output result
    #         print('Result:' + str(all_links))

    all_links = kill_mp(num_processes, tasks, results)

    # all_links = list(itertools.chain(*all_links))  # merge all the lists into one list

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


if __name__ == "__main__":
    # manager = mp.Manager()
    # # Define a list (queue) for tasks and computation results
    # tasks = manager.Queue()
    # results = manager.Queue()

    # num_processes = mp.cpu_count()
    # pool = mp.Pool(processes=num_processes)
    # processes = []
    # # Initiate the worker processes
    # for i in range(num_processes):

    #     # Set process name
    #     process_name = 'P%i' % i

    #     # Create the process, and connect it to the worker function
    #     new_process = mp.Process(target=getAnimeLinks, args=(process_name,tasks,results))

    #     # Add new process to the list of processes
    #     processes.append(new_process)

    #     # Start the process
    #     new_process.start()

    start_time = time.time()  # for timing

    processes, num_processes, tasks, results = init_mp(getAnimeLinks)
    all_links = getAllAnimeLinks()

    logging.info("--- Job took %s seconds ---" % (time.time() - start_time))

