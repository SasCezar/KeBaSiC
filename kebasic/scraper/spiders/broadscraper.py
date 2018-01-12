import logging
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.project import get_project_settings

from domain.webpagebuilder import WebPageBuilder
from kebasic.scraper.items import WebPage

BS_PARSER = 'html.parser'

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'


class BroadScraper(scrapy.Spider):
    name = 'BroadScraper'

    builder = WebPageBuilder()

    rotate_user_agent = True
    with open(get_project_settings()['ALLOWED_DOMAINS_PATH'], 'rt', encoding="utf8") as f:
        allowed_domains = [row.strip() for row in set(f)]

    response_type_whitelist = get_project_settings()['ALLOWED_MIME']

    def start_requests(self):
        with open(get_project_settings()['URLS_PATH'], 'rt', encoding="utf8") as urls:
            for url in urls:
                yield scrapy.Request(url.strip(), self.parse)

    def parse(self, response):
        url = response.url
        html = response.text
        page = self.builder.build(url, html)

        json_page = page.to_dict()
        json_page.pop("category_id")
        json_page.pop("parent_category_id")
        yield WebPage(**json_page)

        soup = BeautifulSoup(html, BS_PARSER)
        urls = self._extract_urls(response.url, soup)

        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    @staticmethod
    def _extract_urls(url, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the links contained by the page

        :param soup:
        :return:
        """
        links = []
        for anchor in soup.find_all(TAG_ANCHOR):
            href = anchor.get(TAG_HREF)
            href = href.strip() if href else None
            if not href or href.startswith('#') or len(href) == 1:
                continue

            if not href.startswith('http'):
                link = urljoin(url, href)
                if link == href:
                    continue
                logging.debug("URL = {} - HREF = {} - Joined = {}".format(url, href, link))
            else:
                link = href

            if not link.endswith('.pdf'):
                links.append(link)

        return links
