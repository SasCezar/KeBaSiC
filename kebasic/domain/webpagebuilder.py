import itertools
import logging
import random
import re
from html import unescape

import requests
from bs4 import BeautifulSoup, Comment

from domain.webpage import WebPage

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
]

USER_AGENTS_LEN = len(USER_AGENTS)

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'

KEYWORDS = "keywords"
DESCRIPTION = "description"
NAME = "name"
CONTENT = "content"

HTML_PARSER = 'html.parser'

URL = 'url'
HTML = 'html'
TEXT = 'text'
HTTP = 'http'
META_DESCRIPTION = 'meta_description'
META_KEYWORDS = 'meta_keywords'


class WebPageBuilder(object):
    def build(self, url, html=None, **kwargs):
        url = url.strip()
        logging.info("Building webpage: {}".format(url))
        webpage = {URL: url}
        if not html:
            if HTTP not in url:
                url = 'http://' + url
            html = self._download_html(url)

        webpage[HTML] = html
        webpage.update(kwargs)
        webpage.update(self._extract(html, kwargs))
        return WebPage(**webpage)

    @staticmethod
    def _download_html(url):
        logging.debug("Downloading webpage: {}".format(url))
        response = requests.get(url, timeout=10,
                                headers={'User-Agent': USER_AGENTS[random.randint(0, USER_AGENTS_LEN - 1)],
                                         'Accept-Language': 'es'})

        webpage = response.content

        html_source = BeautifulSoup(webpage, HTML_PARSER).prettify()

        html_source = unescape(html_source)
        html_source = ' '.join(html_source.split()).strip()
        return html_source

    def _extract(self, html_source, kwargs):
        result = {}
        soup = BeautifulSoup(html_source, HTML_PARSER)
        soup = self._filter_tags(soup)
        result[TEXT] = self._extract_text(soup) if TEXT not in kwargs else kwargs[TEXT]
        result[META_KEYWORDS] = self._extract_meta_keywords(soup) if META_KEYWORDS not in kwargs else kwargs[
            META_KEYWORDS]
        result[META_DESCRIPTION] = self._extract_meta_description(soup) if META_DESCRIPTION not in kwargs else kwargs[
            META_DESCRIPTION]

        metatags = self._extract_metatags(soup)
        result['meta_tags'] = metatags
        result['links_text'] = self.extract_links_text(soup)
        return result

    def _extract_metatags(self, soup):
        result = set()
        name_metatags = soup.find_all("meta", attrs={"name": re.compile(r"(.*description|.*title)", re.IGNORECASE)})
        property_metatags = soup.find_all("meta",
                                          attrs={"property": re.compile(r"(.*description|.*title)", re.IGNORECASE)})
        for tag in itertools.chain(name_metatags, property_metatags):
            content = tag.get(CONTENT, None)
            result.add(content)
        return self._remove_overlapping(result)

    def _remove_overlapping(self, items):
        result = items
        for a, b in itertools.combinations(items, 2):
            if a == b:
                continue
            if a in b and a in result:
                result.remove(a)
            if b in a and b in result:
                result.remove(b)
        return list(result)

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

    def _extract_text(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the visible text of the page
        :param soup:
        :return:
        """
        texts = soup.find_all(text=True)
        visible_texts = [text.strip() for text in texts if self._tag_visible(text)]
        text = ". ".join(t for t in visible_texts if t)
        return text

    @staticmethod
    def _extract_meta_keywords(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the page metadata keywords
        :param soup:
        :return:
        """

        meta_keywords = soup.find(TAG_META, attrs={NAME: KEYWORDS})
        meta_keywords = meta_keywords.get(CONTENT, None) if meta_keywords else None
        return meta_keywords

    @staticmethod
    def _extract_meta_description(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the page metadata description
        :param soup:
        :return:
        """
        meta_description = soup.find(TAG_META, attrs={NAME: DESCRIPTION})
        meta_description = meta_description.get(CONTENT, None) if meta_description else None
        return meta_description

    @staticmethod
    def _extract_title(soup):
        """
        Given a BeautifulSoup representation of the html page extracts the title of the page
        :param soup:
        :return:
        """
        title = soup.title.string.strip() if soup.title else ""
        return title

    @staticmethod
    def _filter_tags(soup):
        """
        Filters tags that don't contains information, or is noisy.
        :param soup:
        :return:
        """
        unwanted_divs = soup.find_all("div", class_=re.compile(r"(footer|cookie|style)", re.IGNORECASE))  # Check menu
        unwanted_sections = soup.find_all(['footer', 'header', 'noscript', 'sidebar'])
        hidded_tags = soup.find_all(style=re.compile(r"(display:none|visibility:hidden)", re.IGNORECASE))

        for tag in itertools.chain(unwanted_divs, unwanted_sections, hidded_tags):
            tag.decompose()

        soup.renderContents()
        return soup

    @staticmethod
    def extract_links_text(soup):
        links = soup.find_all('a')
        result = set()
        for link in links:
            text = link.text.strip()
            if text:
                result.add(text)

        return result
