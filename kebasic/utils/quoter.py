import csv

csv.field_size_limit(2147483647)


def read():
    with open('../webpages.csv', "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        results = []
        for parent_id, category_id, url, text in reader:
            results.append([parent_id, category_id, url, text])
    return results


def write(results, filter_list):
    with open('../webpages_quoted.csv', "wt", encoding="utf8", newline="") as outf:
        writer = csv.writer(outf, quoting=csv.QUOTE_ALL)
        writer.writerow(['parent_id', "category_id", "url", "text"])
        for parent_id, category_id, url, text in results:
            if not text.strip() or url in filter_list or ".pdf" in url:
                continue
            if "," in url:
                url = url.replace(",", "%2C")
            writer.writerow([parent_id, category_id, url, text])

    return


def read_filter():
    results = set()
    with open('../links_multiple_categories.csv', "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        for domain in reader:
            results.add(domain[0])

    return results


if __name__ == '__main__':
    r = read()
    filter_list = read_filter()
    write(r, filter_list)
