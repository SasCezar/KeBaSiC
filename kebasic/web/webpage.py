import re
from urllib.request import urlopen

from bs4 import BeautifulSoup, Comment

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'


class NotValidURL(Exception):
    pass


class WebPage(object):
    def __init__(self, url, html=None):
        """
        Represents a generic web page. The class implements methods for decomposing the web page.
        :param url:
        :param html:
        """
        if not url and not html:
            raise NotValidURL("URL could not be empty")
        self._url = url
        self._html = html
        self._title = ""
        self._text = ""
        self._metadata = {}
        self._links = []

    @property
    def url(self):
        return self._url

    @property
    def html(self):
        return self._html

    @property
    def title(self):
        return self._title

    @property
    def metadata(self):
        return self._metadata

    @property
    def links(self):
        return self._links

    @property
    def text(self):
        return self._text

    def download(self):
        with urlopen(self._url) as webpage:
            self._html = BeautifulSoup(webpage, 'html.parser').prettify()

        self._html = ' '.join(self.html.split())
        return self

    def parse(self):
        if not self.html:
            self.download()

        soup = BeautifulSoup(self.html, 'html.parser')

        self._extract_title(soup)
        self._extract_text(soup)
        self._extract_metadata(soup)
        self._extract_links(soup)

        return self

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
        texts = soup.findAll(text=True)
        visible_texts = [text for text in texts if self._tag_visible(text)]
        cleaned_text = " ".join(t.strip() for t in visible_texts)
        self._text = cleaned_text

    def _extract_metadata(self, soup):
        """

        Given a BeautifulSoup representation of the html page extracts the page metadata values

        :param soup:
        :return:
        """
        for meta in soup.find_all(TAG_META):
            meta_name = meta.name
            meta_description = meta.content

            if meta_description:
                self._metadata[meta_name] = meta_description

    def _extract_links(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the links contained by the page

        :param soup:
        :return:
        """
        for link in soup.find_all(TAG_ANCHOR):
            self.links.append(link.get(TAG_HREF))

    def _extract_title(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the title of the page

        :param soup:
        :return:
        """
        self._title = soup.title.name
