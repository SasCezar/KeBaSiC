import argparse
import logging
import os

from kebasic.execution.basic import BasicExecution
from kebasic.utils import utils
from kebasic.web import querygeneration


def main(configs):
    executor = BasicExecution(configs)
    executor.execute()
    logging.info(executor.language)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")
    parser.add_argument("-debug", action="store_true")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M', filename='kebasic.log', filemode='a')

    configs = utils.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    template_path = configs['template_path']
    out_path = configs['queries_out_path']
    keywords_path = configs['keywords_path']
    sites_path = configs['sites_path']

    querygeneration.generate_queries(template_path, out_path, keywords_path, sites_path)

    main(configs)
