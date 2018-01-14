import csv
import os

from executions.basic import TextCleaningPipeline
from utils.config import load_configs

csv.field_size_limit(2147483647)


def read():
    with open('webpages_cleaned.csv', "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        results = []
        cat = {}
        urls = []
        for parent_id, category_id, url, text in reader:
            results.append([parent_id, category_id, url, text])
            cat[url] = [parent_id, category_id]
            urls.append(url)
    return cat, urls


def write_urls(results, stop):
    with open("bing_results_urls.txt", "wt", encoding="utf8") as outf:
        for parent_id, category_id, url, text in results:
            if url not in stop:
                outf.write(url + "\n")


def write(results, filter_list):
    with open('webpages_quoted.csv', "wt", encoding="utf8", newline="") as outf:
        configs = load_configs("config.json")
        cleaner = TextCleaningPipeline(configs)
        writer = csv.writer(outf, quoting=csv.QUOTE_ALL)
        writer.writerow(['parent_id', "category_id", "url", "text"])
        n = len(results)
        i = 0
        for parent_id, category_id, url, text in results:
            perc = i / n * 100
            print(perc)
            i = i + 1
            cleaned_text = cleaner.process(text).lower()
            if not cleaned_text.strip() or url in filter_list or ".pdf" in url:
                continue
            if "," in url:
                url = url.replace(",", "%2C")
            writer.writerow([parent_id, category_id, url, cleaned_text])

    return


def read_filter():
    results = set()
    with open('links_multiple_categories.csv', "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        for domain in reader:
            results.add(domain[0])

    return results


if __name__ == '__main__':
    os.chdir("C:\\Users\\sasce\\PycharmProjects\\KeBaSiC\\kebasic")
    r = read()
    filter_list = read_filter()
    # write(r, filter_list)
    write_urls(r, filter_list)
