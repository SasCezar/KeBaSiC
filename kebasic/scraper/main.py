from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kebasic.scraper.spiders.broadscraper import BroadScraper

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    scraper = BroadScraper()
    process.crawl(scraper)
    process.start()
