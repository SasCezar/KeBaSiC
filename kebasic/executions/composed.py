import csv
import json
import logging

import pandas
from weka.core import jvm

from classification.weka_classifier import WEKAClassifier
from domain.webpagebuilder import WebPageBuilder
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.penalizer import ScorePenalizer
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.webpageio import BingResultsWebPageReader, JSONWebPageReader
from kebasicio.weka import WekaWebPageTrainingCSV
from kebasicio.writer import StdOutFileWriter
from textprocessing.cleaner import PunctuationCleaner
from utils.taxonomy import read_jot_taxonomy


class KeywordsExecution(AbstractExecutor):
    """
    Implements an execution for keywords extraction
    """

    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()

        path = self._configs['input_path']
        reader = JSONWebPageReader(path)  # Edit the class according to the structure of the input file
        webpages = reader.read()
        writer = StdOutFileWriter
        builder = WebPageBuilder()
        punctuation_cleaner = PunctuationCleaner()
        jvm.start(packages=True)
        wekaclass = WEKAClassifier(self._configs['lvl1_model'], language=self._configs['language'])
        wekaclass2 = WEKAClassifier(self._configs['lvl2_model'], language=self._configs['language'])
        out_filename = self._configs['out_path']
        with writer(out_filename, self._configs['std_out']) as outf:
            for json_webpage in webpages:
                try:
                    webpage = builder.build(**json_webpage)
                    webpage.text = cleaner.process(webpage.text)
                    cleaned_meta = []
                    if webpage.meta_keywords:
                        webpage.meta_keywords = cleaner.process(webpage.meta_keywords)

                    if webpage.meta_description:
                        webpage.meta_description = cleaner.process(webpage.meta_description)
                    for tag in webpage.meta_tags:
                        cleaned_meta.append(cleaner.process(tag))

                    webpage.meta_tags = cleaned_meta

                    cleaned_headers = []
                    for tag in webpage.headers:
                        cleaned = punctuation_cleaner.run(cleaner.process(tag))
                        if cleaned:
                            cleaned_headers.append(cleaned)

                    webpage.headers = cleaned_headers

                    result = feature.process(webpage)
                    if not result:
                        continue
                    for algorithm in result['keywords']:
                        keywords = result['keywords']
                        keywords[algorithm] = scores_normalizer.normalize(result['keywords'][algorithm])

                    combined_scores = scores_normalizer.normalize(scores_merger.merge(result['keywords']))
                    result['keywords']['combined'] = InsertScores().insert(combined_scores,
                                                                           result['keywords']['site_keywords'])

                    result['keywords']['combined'] = InsertScores().insert(result['keywords']['combined'],
                                                                           result['keywords']['meta_tags'])

                    # result['keywords']['combined'] = InsertScores().insert(result['keywords']['combined'],
                    #                                                        result['keywords']['headers'])
                    result['keywords'] = result['keywords']['combined']
                    result['keywords'] = ScorePenalizer().penalize(result['keywords'],
                                                                   [cleaner.process(x) for x in webpage.links_text])
                    logging.info("Keyword extracted: {}".format(len(result['keywords'])))
                    result['parent_category_id'] = wekaclass.classify(webpage.text)
                    result['category_id'] = wekaclass2.classify(webpage.text)

                    string_result = json.dumps(result, ensure_ascii=False)
                    outf.write(string_result)
                except Exception as e:
                    logging.error(e)
                    continue

        jvm.stop()


class DatasetCrawlingExecution(AbstractExecutor):
    def run(self):
        taxonomy = read_jot_taxonomy("../resources/JOT/keys_mapping.txt",
                                     "../resources/JOT/business_type _to_google_category.csv")
        filename = self._configs['input']
        reader = BingResultsWebPageReader
        pages = list(
            reader(filename, taxonomy).read())

        logging.info("Loaded {}".format(len(pages)))
        crawler = ParallelCrawling({}, self._configs["workers"])
        webpages = crawler.run(pages)
        out_path = self._configs['output']
        print("Crawled webpages {}".format(len(webpages)))
        with open(out_path + ".json", "wt", encoding="utf8") as jsonout:
            for webpage in webpages:
                jsonout.write(json.dumps(webpage.to_dict(), ensure_ascii=False) + "\n")

        reader = JSONWebPageReader(out_path + ".json")
        webpages = reader.read()

        i = 0
        seen = set()
        builder = WebPageBuilder()
        cleaner = TextCleaningPipeline(self._configs)
        dict_h1, dict_h2, inv_dict_h1, inv_dict_h2, dict_parent_category = readTaxonomy(
            "../resources/JOT/training_taxonomy.csv")
        with open(out_path + "_lvl1.csv", "wt", encoding="utf8", newline="") as out1, \
                open(out_path + "_lvl2.csv", "wt", encoding="utf8", newline="") as out2:
            writer1 = csv.writer(out1, quoting=csv.QUOTE_NONE)
            writer2 = csv.writer(out2, quoting=csv.QUOTE_NONE)
            for webpage in webpages:
                try:
                    built = builder.build(**webpage)
                    webpage = built.to_dict()
                    if webpage['url'] in seen:
                        continue
                    seen.add(webpage['url'])
                    i += 1
                    logging.info("Completed {} rows".format(i))
                    webpage['text'] = cleaner.process(webpage['text'])
                    if webpage['text']:
                        # writer1.writerow([webpage['parent_category_id'].lower().strip(), webpage['text']])
                        row1 = [int(inv_dict_h1[webpage['parent_category_id'].lower().strip()]), webpage['parent_category_id'].lower().strip(), webpage['text']]
                        writer1.writerow(row1)
                        row2 = [int(inv_dict_h2[webpage['category_id'].lower().strip()]), webpage['category_id'].lower().strip(), webpage['text']]
                        writer2.writerow(row2)
                        # writer2.writerow([webpage['category_id'].lower().strip(), webpage['text']])
                except:
                    continue


def readTaxonomy(taxonomy_path):
    #    taxonomy_path = "../taxonomy.csv"
    taxonomy = pandas.read_csv(taxonomy_path, sep=',')
    tax_h1 = taxonomy[pandas.isnull(taxonomy).any(axis=1)]
    tax_h1 = tax_h1[['id', 'lvl1']]
    tax_h1["id"] = tax_h1["id"].apply(str)
    tax_h1 = tax_h1.set_index('id')
    dict_h1 = tax_h1.to_dict()

    tax_h2_all = taxonomy.dropna()
    tax_h2 = tax_h2_all[['id', 'lvl2']]
    tax_h2["id"] = tax_h2["id"].apply(str)
    tax_h2 = tax_h2.set_index('id')
    dict_h2 = tax_h2.to_dict()

    inv_dict_h1 = {v: k for k, v in dict_h1["lvl1"].items()}
    inv_dict_h2 = {v: k for k, v in dict_h2["lvl2"].items()}

    tax_h2_all["lvl1"] = tax_h2_all["lvl1"].apply(lambda x: inv_dict_h1[x])
    tax_h2_all["lvl2"] = tax_h2_all["lvl2"].apply(lambda x: inv_dict_h2[x])

    dict_parent_category = dict(zip(tax_h2_all["lvl2"], tax_h2_all["lvl1"]))

    return dict_h1, dict_h2, inv_dict_h1, inv_dict_h2, dict_parent_category


class ReformatExecution(AbstractExecutor):
    def run(self):
        path = "../output/scraper/GoogleScraper_test_results.json.json"
        reader = JSONWebPageReader(path)
        webpages = reader.read()

        out_path = "../data/train_set.json"
        i = 0
        seen = set()
        builder = WebPageBuilder()
        cleaner = TextCleaningPipeline(self._configs)
        with WekaWebPageTrainingCSV(out_path) as outf:
            for webpage in webpages:
                try:
                    built = builder.build(**webpage)
                    webpage = built.to_dict()
                    if webpage['url'] in seen:
                        continue
                    seen.add(webpage['url'])
                    i += 1
                    logging.info("Completed {} rows".format(i))
                    webpage['text'] = cleaner.process(webpage['text'])
                    outf.write(webpage)
                except:
                    continue
