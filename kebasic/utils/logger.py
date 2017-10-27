import logging
import os

LOGGING_STRING_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"


def initialize_logger(output_dir):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGGING_STRING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "wt", encoding="utf8", delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(LOGGING_STRING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "all.log"), "wt", encoding="utf8")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOGGING_STRING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
