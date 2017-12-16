import html
import itertools
import logging
import random
import re
from urllib.request import urlopen, Request

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


class WebPageBuilder(object):
    def build(self, url, html_source=None):
        logging.info("Downloading webpage: {}".format(url))
        webpage = {'url': url}
        if not html_source:
            html_source = self._download_html(url)

        webpage['html'] = html_source
        webpage.update(self._extract(html_source))
        return WebPage(**webpage)

    @staticmethod
    def _download_html(url):
        request = Request(url, headers={'User-Agent': USER_AGENTS[random.randint(0, USER_AGENTS_LEN - 1)]})
        with urlopen(request) as webpage:
            html_source = BeautifulSoup(webpage, 'html.parser').prettify()

        html_source = html.unescape(html_source)
        html_source = ' '.join(html_source.split()).strip()
        return html_source

    def _extract(self, html_source):
        result = {}
        soup = BeautifulSoup(html_source, 'html.parser')
        soup = self._filter_tags(soup)
        result['title'] = self._extract_title(soup)
        result['meta_keywords'] = self._extract_meta_keywords(soup)
        result['meta_description'] = self._extract_meta_description(soup)
        result['text'] = self._extract_text(soup)
        return result

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
        title = soup.title.name.strip() if soup.title else ""
        return title

    @staticmethod
    def _filter_tags(soup):
        """
        Filters tags that don't contains information, or is noisy.
        :param soup:
        :return:
        """
        unwanted_divs = soup.find_all(class_=re.compile(r"(footer|header|cookie|style)", re.IGNORECASE))  # Check menu
        unwanted_sections = soup.find_all(['footer', 'header', 'noscript'])

        for tag in itertools.chain(unwanted_divs, unwanted_sections):
            tag.decompose()

        soup.renderContents()
        return soup
