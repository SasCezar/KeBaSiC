import argparse
import json
import logging

from kebasic.execution.basic import BasicExecution


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

    with open(args.config_file) as config_file:
        configs = json.load(config_file)

    main(configs)
