import requests
from bs4 import BeautifulSoup
import json


import re
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

    # additional details
    subtext = soup.find("div",{'class':'subtext'})
    data["subtext"] = ""
    for i in subtext.contents:
        data["subtext"] += i.string.strip()

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
# r = requests.get(url=dsmugen_url)
# # Create a BeautifulSoup object
# soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.find_all('rating'))

# dsmugen_details = getMovieDetails(dsmugen_url)
# dsmugen_crew = getCrewData(dsmugen_url)
# print(json.dumps(dsmugen_details, sort_keys=True, indent=4))  # to pretty print
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

links = getAllAnimeLinks(138)
for link in links:
    url = f"https://www.imdb.com{link}"
    movie_details = getMovieDetails(url)
    print(json.dumps(movie_details, sort_keys=True, indent=4))  # to pretty print
    
# r = requests.get(url="https://www.imdb.com/search/keyword/?keywords=anime&page=1", stream=True)
# soup = BeautifulSoup(r.text, 'html.parser')
# res = soup.find_all("div",{"class":"lister-item mode-detail"})
# titles = []
# for r in res:
#     titles.append(r.find("a")['href'])
# print(titles)
