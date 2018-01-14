import logging
from time import strftime, gmtime

from datasources.webpagedao import MongoWebPageReader, CSVCatalogactionReader
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.weka import WekaKeywordTrainingCSV, WekaTrainigCSV
from utils.taxonomy import read_reverse_taxonomy


class KeywordsExecution(AbstractExecutor):
    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()
        reader = MongoWebPageReader(None)

        webpages = reader.load_webpages()

        webpages_category = {}
        for webpage in webpages:
            webpages_category[webpage.url] = {'category_id': webpage.category_id,
                                              'parent_category_id': webpage.parent_category_id}

        webpages = reader.load_webpages()

        now = strftime("%Y_%m_%d-%H_%M", gmtime())
        filename = "keywords_bing_{}_sum_combined_max_normalized.txt".format(now)

        writer = WekaKeywordTrainingCSV

        with writer(filename) as outf:
            outf.write_header()
            next(webpages)
            for webpage in webpages:
                webpage.text = cleaner.process(webpage.text)
                result = feature.process(webpage)
                if not result:
                    continue

                for algorithm in result['keywords']:
                    keywords = result['keywords']
                    keywords[algorithm] = scores_normalizer.normalize(result['keywords'][algorithm])

                combined_scores = scores_normalizer.normalize(scores_merger.merge(result['keywords']))
                result['keywords'] = InsertScores().insert(combined_scores, result['keywords']['site_keywords'])
                logging.info("Keyword extracted: {}".format(len(result['keywords'])))

                result.update(webpages_category[result['url']])

                outf.write(result)

        """
        executors_configs = {}
        executors_configs.update(cleaner.get_config())
        executors_configs.update(feature.get_config())
        """


class CrawlingExecution(AbstractExecutor):
    def run(self):
        self._configs['preprocessing_algorithms'].insert(-4, 'textprocessing.cleaner.StopWordsCleaner')
        self._configs['preprocessing_algorithms'].insert(-2, 'textprocessing.cleaner.Clean4SQL')
        cleaner = TextCleaningPipeline(self._configs)
        ontology = read_reverse_taxonomy(self._configs['taxonomy_path'])

        reader = CSVCatalogactionReader("catalogación_test.csv", ontology)
        webpages = list(reader.load_webpages())
        cleaned_webpages = cleaner.process(webpages)
        writer = WekaTrainigCSV
        with writer("catalogacion_test.csv") as outf:
            outf.write(cleaned_webpages)
