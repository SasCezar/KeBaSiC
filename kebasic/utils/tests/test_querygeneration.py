import unittest

from kebasic.utils.querygeneration import QueryGenerator

template_path = 'google_query_template.txt'
keywords = [{'lvl1': 'category11', 'lvl2': 'category12'},
            {'lvl1': 'category21', 'lvl2': 'category22'}]

sites = [{'site': 'random.org'}, {'site': 'fb.com'}]

query_result = ['allintitle: category22 site:.es -filetype:pdf',
                'site:es.wikipedia.com category21 category22 -filetype:pdf',
                'site:es.wikipedia.com category11 category12 -filetype:pdf',
                'allintitle: category12 site:.es -filetype:pdf', 'related:random.org', 'related:fb.com']

site_query_result = ['related:random.org', 'related:fb.com']
keywords_query_result = ['allintitle: category22 site:.es -filetype:pdf',
                         'site:es.wikipedia.com category21 category22 -filetype:pdf',
                         'site:es.wikipedia.com category11 category12 -filetype:pdf',
                         'allintitle: category12 site:.es -filetype:pdf']

google_query_generator = QueryGenerator(template_path)


class TestQueryGenerator(unittest.TestCase):
    def test_query_generation(self):
        queries = google_query_generator.generate_queries(keywords, sites)
        self.assertListEqual(sorted(queries), sorted(query_result))

    def test_empty_site_query_generation(self):
        queries = google_query_generator.generate_queries(keywords, [])
        self.assertListEqual(sorted(queries), sorted(keywords_query_result))

    def test_empty_keywords_query_generation(self):
        queries = google_query_generator.generate_queries([], sites)
        self.assertListEqual(sorted(queries), sorted(site_query_result))

    def test_empty_query_generation(self):
        queries = google_query_generator.generate_queries([], [])
        self.assertListEqual(queries, [])

    def test_save_queries(self):
        query_path = "queries_result.txt"
        QueryGenerator.save_queries(query_path, query_result)

        loaded_query = []
        with open(query_path, "rt", encoding="utf8") as inf:
            for line in inf:
                loaded_query.append(line.strip())

        self.assertListEqual(loaded_query, query_result)
