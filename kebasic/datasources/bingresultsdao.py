import csv

from mongoengine import *

from datasources.mongoobjects import BingResults

connect('kebasic')


class BingResultsDAO(object):
    @staticmethod
    def get_website_categories():
        results = BingResults.objects()
        categories_list = []
        domains_list = []
        for result in results:
            for query_result in result.results:
                if result.parent_id == '0':
                    parent = result.category_id
                else:
                    parent = result.parent_id

                categories_list.append([parent, result.category_id])
                domains_list.append(query_result.link)

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


def save_csv(path, categories, domains):
    with open(path, "wt", encoding="utf8", newline="") as outf:
        writer = csv.writer(outf, delimiter=",", quoting=csv.QUOTE_ALL)
        for d in domains:
            r = categories[d] + [d]
            writer.writerow(r)


if __name__ == '__main__':
    r2csv = BingResultsDAO()
    categories, domains = r2csv.get_website_categories()
    save_csv("categories_domains_text.csv", categories, domains)
