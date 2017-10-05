import csv
import os


def read_dict_csv(file_path):
    if not file_path:
        return None
    with open(file_path, "rt", encoding="utf8") as inf:
        r = [{k: v.strip() for k, v in row.items()}
             for row in csv.DictReader(inf, skipinitialspace=True)]

    return r


def generate_queries(template_path, out_path, keywords_path=None, sites_path=None):
    query_generator = QueryGenerator(template_path)

    keywords = read_dict_csv(keywords_path)

    sites = read_dict_csv(sites_path)

    queries = query_generator.generate_queries(keywords=keywords, sites=sites)

    query_generator.save_queries(out_path, queries)


class QueryGenerator(object):
    def __init__(self, template_path):
        self._site_templates, self._query_templates = self._read_template(template_path)

    @staticmethod
    def _read_template(template_path):
        site_templates = []
        query_templates = []
        with open(template_path, "rt", encoding="utf8") as inf:
            for line in inf:
                site_templates.append(line) if "{site}" in line else None
                query_templates.append(line) if "{site}" not in line else None

        return site_templates, query_templates

    def generate_queries(self, keywords=None, sites=None):
        queries = set()
        for keyword in keywords:
            keyword_queries = self._generate_query(keyword, self._query_templates)
            queries |= keyword_queries

        for site in sites:
            sites_query = self._generate_query(site, self._site_templates)
            queries |= sites_query

        return list(queries)

    @staticmethod
    def _generate_query(keyword, templates):
        queries = set()
        for template in templates:
            query = template.format(**keyword).strip()
            queries.add(query)

        return queries

    @staticmethod
    def save_queries(out_path, queries):
        with open(out_path, "wt", encoding="utf8", newline='') as inf:
            inf.write(os.linesep.join(queries))
