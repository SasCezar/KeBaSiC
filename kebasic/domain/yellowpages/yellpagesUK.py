import argparse
import collections
import requests
import re
import json
from bs4 import BeautifulSoup
from geopy import Nominatim



def create_results(results_to_be_parsed):

    risultati = {}
    risultati['competitors'] = []
    i=0
    for el in results_to_be_parsed:
        if i<=10:
            tmp = {}

            try:
                tmp['url'] = el.find_all('a', class_="btn btn-yellow businessCapsule--ctaItem")[1].get("href")
            except:
                tmp['url'] = ''
            try:
                tmp['name'] = el.find_all('span', class_="businessCapsule--name")[0].getText()
            except:
                tmp['name'] = ''
            try:
                tmp['description'] = el.find_all("p", class_="payoff-txt")[0].getText()
            except:
                tmp['description'] = ''


            geolocator = Nominatim(user_agent="KebTest")
            address = el.find_all('a', class_ = "col-sm-24 businessCapsule--address businessCapsule--link")[0].getText().strip().replace('\n', ' ')
            location = geolocator.geocode(address)
            if location is not None:
                tmp['lat'] = location.latitude
                tmp['long'] = location.longitude
            else:
                tmp['lat'] = ''
                tmp['long'] = ''

            ordered_tmp = collections.OrderedDict(sorted(tmp.items()))

            risultati['competitors'].append(ordered_tmp)
            i += 1

    return risultati



def scraping(keyword, location):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'www.yell.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
               }


    url = 'https://www.yell.com/ucs/UcsSearchAction.do?keywords='+keyword+'&location='+location

    response = requests.get(url, verify=False, headers=headers)
    if response.status_code == 200:
        page = BeautifulSoup(response.text, 'html')
        results_to_be_parsed= page.find_all("div", class_="col-sm-15 col-md-14 col-lg-15 businessCapsule--mainContent")
        risultati=create_results(results_to_be_parsed)

    with open("/srv/shiny-server/kebasic/KeBaSiC/paginas.json", "w") as f:
        f.write(json.dumps(risultati, ensure_ascii=True))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-keywords", default="")
    parser.add_argument("-location", default="United Kingdom")
    args = parser.parse_args()

    keywords = vars(args)['keywords']

    stopwords = []
    with open("/srv/shiny-server/kebasic/KeBaSiC/resources/IT/stopwords/stopwords_it_en.txt", 'r') as f:
        for line in f:
            stopwords.append(line.strip())

    keywords = keywords.split(" ")
    keywords = [x for x in keywords if x not in stopwords]
    keyword = "%20".join(keywords)

    scraping(keyword, vars(args)['location'])

main()