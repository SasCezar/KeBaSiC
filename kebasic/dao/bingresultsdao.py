import csv

from mongoengine import *

from mongo.mongoobjects import BingResults

connect('kebasic')


class BingResultsDAO(object):
    @staticmethod
    def get_domains_categories(lvl=0):
        results = BingResults.objects()
        categories_list = []
        domains_list = []
        for result in results:
            for query_result in result.results:
                if lvl == 0 and result.parent_id == 0:
                    cat = result.parent_id
                else:
                    cat = result.category_id

                categories_list.append(cat)
                domains_list.append(query_result.domain)

        categories = {}
        domains = []
        seen = set()
        for category, domain in zip(categories_list, domains_list):
            if domain in seen:
                continue
            categories[domain] = category
            domains.append(domain)
            seen.add(domain)

        return categories, domains


def save_csv(path, res):
    with open(path, "wt", encoding="utf8", newline="") as outf:
        writer = csv.writer(outf, delimiter=",")
        for r in res:
            writer.writerow(r)


if __name__ == '__main__':
    r2csv = BingResultsDAO()
    res = r2csv.get_domains_categories()
    save_csv("categories.csv", res)
