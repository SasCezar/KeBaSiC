import argparse
import csv
import logging
import os

from kebasic.dao.webpagedao import CSVWebPageDAO
from kebasic.execution.basic import FeatureExtractionExecution
from kebasic.utils import utils


def write_csv(result):
    with open('keywords.csv', 'wt', encoding="utf8", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file,
                                     fieldnames=["url", "site_keywords", "RAKE", "TextRank", "TermFrequencies"])
        dict_writer.writeheader()
        dict_writer.writerows(result)


def main(configs):
    executor = FeatureExtractionExecution(configs)
    webpages = CSVWebPageDAO(configs['websites_path']).load_webpages()
    result = executor.execute(webpages)
    write_csv(result)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")
    parser.add_argument("-debug", action="store_true")

    args = parser.parse_args()

    # log_level = logging.DEBUG if args.debug else logging.INFO
    log_level = logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M', filename='kebasic.log', filemode='a')

    configs = utils.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    main(configs)
