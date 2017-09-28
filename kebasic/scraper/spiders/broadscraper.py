import re

import scrapy
from bs4 import BeautifulSoup, Comment
from scrapy.utils.project import get_project_settings

from kebasic.scraper.items import Page

BS_PARSER = 'html.parser'

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'


class BroadScraper(scrapy.Spider):
    name = 'BroadScraper'
    rotate_user_agent = True
    with open(get_project_settings()['ALLOWED_DOMAINS_PATH'], 'rt') as f:
        allowed_domains = list(f)

    def start_requests(self):
        with open(get_project_settings()['URLS_PATH'], 'rt') as urls:
            for url in urls:
                yield scrapy.Request(url, self.parse)

    def parse(self, response):
        web_page = response.text
        soup = BeautifulSoup(web_page, BS_PARSER)
        title = self._extract_title(soup)
        html = web_page
        text = self._extract_text(soup)
        metadata = self._extract_metadata(soup)
        page = Page(title=title, html=html, text=text, metadata=metadata)

        yield page

        urls = self._extract_urls(soup)

        for url in urls:
            if url is None or not url.startswith('http'):
                continue
            yield scrapy.Request(url, callback=self.parse)

    def _extract_text(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the visible text of the page

        :param soup:
        :return:
        """
        texts = soup.findAll(text=True)
        visible_texts = [text for text in texts if self._tag_visible(text)]
        cleaned_text = " ".join(t.strip() for t in visible_texts)
        return cleaned_text

    @staticmethod
    def _tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        elif isinstance(element, Comment):
            return False
        elif re.match('<!--.*-->', str(element)):
            return False
        elif re.match('\n', str(element)):
            return False
        else:
            return True

    @staticmethod
    def _extract_metadata(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the page metadata values

        :param soup:
        :return:
        """
        metadata = {}
        for meta in soup.find_all(TAG_META):
            meta_name = meta.name
            meta_description = meta.content

            if meta_description:
                metadata[meta_name] = meta_description

        return metadata

    @staticmethod
    def _extract_urls(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the links contained by the page

        :param soup:
        :return:
        """
        links = []
        for link in soup.find_all(TAG_ANCHOR):
            links.append(link.get(TAG_HREF))

        return links

    @staticmethod
    def _extract_title(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the title of the page

        :param soup:
        :return:
        """
        title = soup.title.name
        return title
