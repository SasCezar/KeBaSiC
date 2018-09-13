import argparse
import collections
import urllib3
import re
import json
from bs4 import BeautifulSoup


def create_results(results_to_be_parsed):

    risultati = {}
    risultati['competitors'] = []
    i=0
    for el in results_to_be_parsed:
        if i<=10:
            tmp = {}
            text = el.text.split('\t')
            x = []
            for t in text:
                x.append(t.strip())
            text = x
            try:
                tmp['url'] = el.find_all('a', class_="btn btn-black icn-sitoWeb shinystat_ssxl")[0].get("href")
            except:
                print(text)
                tmp['url'] = ''
            tmp['name'] = text[2]
            tmp['description'] = el.find_all("p", class_="payoff-txt")[0].getText()
            try:
                coordinate = re.findall("\\n(\d+\.\d+)\\n(\d+\.\d+)\\n", text[6])
                tmp['lat'] = coordinate[0][0]
                tmp['long'] = coordinate[0][1]
            except:
                tmp['lat'] = ''
                tmp['long'] = ''

            ordered_tmp = collections.OrderedDict(sorted(tmp.items()))

            risultati['competitors'].append(ordered_tmp)
            i += 1

    return risultati



def scraping(keyword, location):
    keyword = keyword.replace(" ", "%20")
    if location is not '':
        url = 'https://www.paginegialle.it/ricerca/'+keyword+'/'+ location+'?'
    else:
        url = 'https://www.paginegialle.it/ricerca/' + keyword + '/'

    http_pool = urllib3.connection_from_url(url)
    r = http_pool.urlopen('GET', url)
    page = BeautifulSoup(r.data.decode('utf-8'), 'html')

    results_to_be_parsed= page.find_all("section", class_='vcard')

    risultati=create_results(results_to_be_parsed)

    with open("/srv/shiny-server/kebasic/KeBaSiC/paginas.json", "w") as f:
        f.write(json.dumps(risultati, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-keywords", default="")
    parser.add_argument("-location", default="")
    args = parser.parse_args()
    scraping(vars(args)['keywords'], vars(args)['location'])

main()


