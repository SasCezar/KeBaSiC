import argparse
import logging
from configparser import ConfigParser


def main(configs):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.ini")
    parser.add_argument("-debug", action="store_true")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='kebasic.log',
                        filemode='a')

    configs = ConfigParser()
    configs.read(args.config_file)

    main(configs)
