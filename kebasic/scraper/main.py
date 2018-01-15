import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from kebasic.scraper.spiders.broadscraper import BroadScraper

LOGGING_STRING_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

if __name__ == "__main__":
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format=LOGGING_STRING_FORMAT,
        level=logging.INFO
    )
    process = CrawlerProcess(get_project_settings())
    scraper = BroadScraper()
    process.crawl(scraper)
    process.start()
