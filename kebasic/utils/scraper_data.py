import csv
from urllib.parse import urlparse

csv.field_size_limit(2147483647)


def read():
    with open('../webpages_quoted.csv', "rt", encoding="utf8") as inf:
        reader = csv.reader(inf, quotechar='"')
        results = []

        for parent_id, category_id, url, text in reader:
            results.append(url)
    return results


def save_domains(urls):
    with open("starts_url.txt", "wt", encoding="utf8") as outf, open("allowed_domains.txt", "wt",
                                                                     encoding="utf8") as domf:
        for url in urls:
            parsed = urlparse(url)
            outf.write(parsed.scheme + "://" + parsed.netloc + "\n")
            domain = parsed.netloc if "www." not in parsed.netloc else parsed.netloc.replace("www.", "")
            domf.write(domain + "\n")


if __name__ == '__main__':
    urls = read()
    save_domains(urls)
