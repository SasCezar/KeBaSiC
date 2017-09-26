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

    def write_queries(self, out_path, keywords=None, sites=None):
        queries = self.generate_queries(keywords, sites)

        with open(out_path, "wt", encoding="utf8") as inf:
            for query in queries:
                inf.write(query)

    @staticmethod
    def _generate_queries(keywords, templates):
        queries = set()
        for keyword in keywords:
            for template in templates:
                query = template.format(**keyword)
                queries.add(query)

        return queries

    def generate_queries(self, keywords, sites):
        keyword_queries = self._generate_queries(keywords, self._query_templates)
        sites_query = self._generate_queries(sites, self._site_templates)
        keyword_queries.union(sites_query)

        return list(keyword_queries)  # TODO Check if is necessary to cast to list
