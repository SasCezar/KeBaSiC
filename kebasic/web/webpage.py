import re
from urllib.request import urlopen

from bs4 import BeautifulSoup

valid_url_re = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
        if not url:
            raise NotValidURL("URL could not be empty")
        if not valid_url_re.match(url):
            raise NotValidURL("URL not conforms to URL formats")
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

    def download(self):
        with urlopen(self._url) as webpage:
            self._html = webpage

    def parse(self):
        if not self.html:
            self.download()

        soup = BeautifulSoup(self.html)

        self._title = soup.title.name
        self._text = self.extract_text(soup)
        self._metadata = self.extract_metadata(soup)
        self._links = self.extract_links(soup)

    @staticmethod
    def _tag_visible(element):
        if element.parent.name in ['style', 'script', 'document', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element)):
            return False
        elif re.match('\n', str(element)):
            return False
        else:
            return True

    def extract_text(self, soup):
        texts = soup.findAll(text=True)
        visible_texts = [text for text in texts if self._tag_visible(text)]
        return " ".join(t.strip() for t in visible_texts)

    def extract_metadata(self, soup):
        for meta in soup.find_all(TAG_META):
            meta_name = meta.name
            meta_description = meta.content

            if meta_description:
                self._metadata[meta_name] = meta_description

        return self.metadata

    def extract_links(self, soup):
        for link in soup.find_all(TAG_ANCHOR):
            self.links.append(link.get(TAG_HREF))

        return self.links
