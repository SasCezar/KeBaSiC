import csv
import json
import os

from kebasicio.webpageio import BingResultsWebPageReader, JSONWebPageReader
from utils.taxonomy import read_jot_taxonomy


def main():
    taxonomy = read_jot_taxonomy("../resources/JOT/updated_taxonomy_EN.csv", "../resources/JOT/keys_mapping.txt",
                                 "../resources/JOT/business_type _to_google_category.csv")

    reader = BingResultsWebPageReader
    pages = list(
        reader("../data/GoogleScraper_bing_JOTKeywords_25_pages_language.json", taxonomy).read())

    webpages = list(
        JSONWebPageReader("../output/scraper/GoogleScraper_bing_JOTKeywords_25_pages_language_1.json").read())

    cats = {}
    for page in pages:
        if 'parent_category_id' not in page:
            continue
        cats[page['url']] = {'parent_category_id': page['parent_category_id'],
                             'parent_category': page['parent_category'],
                             'category_id': page['category_id'], 'category': page['category_id']}

    seen = set()
    i = 0
    with open("../output/scraper/GoogleScraper_bing_JOTKeywords_25_pages_language_fixed.json", "wt",
              encoding="utf8") as jsonout:
        for webpage in webpages:
            if webpage['url'] in seen:
                continue
            seen.add(webpage['url'])
            if webpage['url'] not in cats:
                i = i + 1
                continue
            webpage.update(cats[webpage['url']])
            jsonout.write(json.dumps(webpage, ensure_ascii=False) + "\n")
    print(i)


def main2():
    mapping = {}
    with open("../resources/JOT/business_type _to_google_category.csv", "rt", encoding="utf8") as inf:
        for line in inf:
            splitted = line.split(",")
            lvl1 = splitted[0]
            lvl2 = splitted[1]
            id = splitted[2]
            id2 = splitted[3] if splitted[3] else None

            mapping[id] = {"parent_category": lvl1, "category": lvl2}
            if id2:
                mapping[id2] = {"parent_category": lvl1, "category": lvl2}

    result = []
    with open("C:\\Users\\sasce\\Downloads\\training_catalogacion_stemmed.csv", "rt", encoding="utf8") as inf:
        next(inf)
        reader = csv.reader(inf)
        for parent_id, category_id, url, text in reader:
            if category_id not in mapping and parent_id not in mapping:
                print(category_id + " url " + url)
                continue

            mapped_cat = mapping[category_id] if category_id in mapping else mapping[parent_id]
            result.append([mapped_cat['parent_category'], mapped_cat["category"], url])

    test_path = ''

    # with open(test_path, "rt", encoding="utf8") as inf:
    #     next(inf)
    #     reader = csv.reader(inf)
    #     for url, jot_cat, cat_id, _, _, _, _, _,_ in reader:
    #         if cat_id not in mapping:
    #             print(cat_id + " url " + url)
    #             continue
    #
    #         mapped_cat = mapping[cat_id]
    #         result.append([mapped_cat['parent_category'], mapped_cat["category"], url])

    with open("remapped_test_set.csv", "wt", encoding="utf8", newline='') as outf:
        writer = csv.writer(outf)
        for res in result:
            writer.writerow(res)


if __name__ == '__main__':
    os.chdir("..")
    main2()
