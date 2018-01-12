import csv
import json
from urllib.parse import urlparse

from utils.taxonomy import read_taxonomy

csv.field_size_limit(2147483647)


def load_categories():
    result = {}
    with open("../webpages_quoted.csv", "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        for parent_id, category_id, url, text in reader:
            parsed = urlparse(url)
            domain = parsed.netloc if "www." not in parsed.netloc else parsed.netloc.replace("www.", "")
            result[domain] = category_id

    return result


def add_categories():
    categories = load_categories()
    ids = read_taxonomy("../../resources/ES/taxonomy/taxonomy.csv")
    with open("../scraper/result.json", "rt", encoding="utf8") as inf, \
            open("categorized_results.json", "wt", encoding="utf8") as outf:
        i = 0
        n = 0
        for line in inf:
            n += 1

            obj = json.loads(line, encoding="utf8")
            url = obj["url"]
            parsed = urlparse(url)
            domain = parsed.netloc if "www." not in parsed.netloc else parsed.netloc.replace("www.", "")
            obj['domain'] = domain
            if domain not in categories:
                i += 1
                continue
            cat = categories[domain]
            if cat not in ids:
                print("ERROR: {}".format(cat))
                continue

            obj_cat = ids[cat]
            obj.update(obj_cat)
            string_obj = json.dumps(obj, ensure_ascii=False)
            outf.write(string_obj + "\n")

    percent = i / n
    print("Lines {} - Not Loaded {} - Percent {}".format(n, i, percent))


if __name__ == '__main__':
    add_categories()
