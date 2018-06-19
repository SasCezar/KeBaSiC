import csv
import os

from kebasic.utils.config import load_configs


def read_dict_csv(file_path):
    """
    Reads the keywords in the file as a dictionary

    :param file_path:
    :return:
    """
    if not file_path:
        return None
    with open(file_path, "rt", encoding="utf8") as inf:
        r = [{k.strip(): v.strip() for k, v in row.items()}
             for row in csv.DictReader(inf, skipinitialspace=True)]

    return r


def generate_queries(template_path, out_path, keywords_path=None):
    """
    Generates a file containing the queries that will be used to scrape a search engine

    :param template_path:
    :param out_path:
    :param keywords_path:
    :param sites_path:
    :return:
    """
    query_generator = QueryGenerator(template_path)
    keywords = read_dict_csv(keywords_path)
    queries = query_generator.generate_queries(keywords=keywords)
    query_generator.save_queries(out_path, queries)


class QueryGenerator(object):
    """
    Defines a query generator based on templates strings
    """

    def __init__(self, template_path):
        self._site_templates, self._query_templates = self._read_template(template_path)

    @staticmethod
    def _read_template(template_path):
        """
        Loads the template and separates sites templates and keywords templates

        :param template_path:
        :return:
        """
        site_templates = []
        query_templates = []
        with open(template_path, "rt", encoding="utf8") as inf:
            for line in inf:
                site_templates.append(line) if "{site}" in line else None
                query_templates.append(line) if "{site}" not in line else None

        return site_templates, query_templates

    def generate_queries(self, keywords=None):
        """
        Given two list of strings, returns a list of unique queries based on the class templates

        :param keywords:
        :return:
        """
        if keywords is None:
            keywords = []

        queries = set()
        for keyword in keywords:
            keyword_queries = self._generate_query(keyword, self._query_templates)
            queries |= keyword_queries

        return list(queries)

    @staticmethod
    def _generate_query(keyword, templates):
        """
        Given a keyword and a list of templates returns a list of formatted queries

        :param keyword:
        :param templates:
        :return:
        """
        queries = set()
        for template in templates:
            query = template.format(**keyword).strip()
            if query == template:
                continue
            queries.add(query)

        return queries

    @staticmethod
    def save_queries(out_path, queries):
        """
        Saves the queries to file

        :param out_path:
        :param queries:
        :return:
        """
        with open(out_path, "wt", encoding="utf8", newline='') as inf:
            inf.write(os.linesep.join(queries))


def main():
    config_path = "../config.json"

    config = load_configs(config_path)
    os.chdir("..")
    template_path = config["template_path"]
    query_out_path = config["query_out_path"]
    keywords_path = "utils/keys.txt"

    generate_queries(template_path, query_out_path, keywords_path)


if __name__ == "__main__":
    main()
