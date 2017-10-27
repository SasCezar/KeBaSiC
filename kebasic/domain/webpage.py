import re
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup, Comment

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'

KEYWORDS = "keywords"
DESCRIPTION = "description"
NAME = "name"
CONTENT = "content"


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
        self._meta_keywords = None
        self._meta_description = None
        self._parse()

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
    def meta_keywords(self):
        return self._meta_keywords

    @property
    def meta_description(self):
        return self._meta_description

    @property
    def text(self):
        return self._text

    def _download(self):
        print(self._url)
        request = Request(self._url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(request) as webpage:
            self._html = BeautifulSoup(webpage, 'html.parser').prettify()

        self._html = ' '.join(self.html.split()).strip()
        return self

    def _parse(self):
        if not self.html:
            self._download()

        soup = BeautifulSoup(self.html, 'html.parser')

        self._extract_title(soup)
        self._extract_text(soup)
        self._extract_metadata(soup)

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
        cleaned_text = " ".join(t.strip() for t in visible_texts if t.strip())
        self._text = cleaned_text.strip()

    def _extract_metadata(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the page metadata values
        :param soup:
        :return:
        """

        meta_keywords = soup.find(TAG_META, attrs={NAME: KEYWORDS})
        self._meta_keywords = meta_keywords.get(CONTENT, None) if meta_keywords else None
        meta_description = soup.find(TAG_META, attrs={NAME: DESCRIPTION})
        self._meta_description = meta_description.get(CONTENT, None) if meta_description else None

    def _extract_title(self, soup):
        """
        Given a BeautifulSoup representation of the html page extracts the title of the page
        :param soup:
        :return:
        """
        self._title = soup.title.name.strip()
