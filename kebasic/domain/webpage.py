import html
import itertools
import logging
import random
import re
from urllib.parse import urljoin
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup, Comment
from premailer import transform

TAG_META = 'meta'
TAG_ANCHOR = 'a'
TAG_HREF = 'href'

KEYWORDS = "keywords"
DESCRIPTION = "description"
NAME = "name"
CONTENT = "content"

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

logging.getLogger('CSSUTILS').setLevel(logging.CRITICAL)


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

    @text.setter
    def text(self, value):
        self._text = value

    def _download(self):
        print(self._url)
        request = Request(self._url, headers={'User-Agent': USER_AGENTS[random.randint(0, USER_AGENTS_LEN - 1)]})
        with urlopen(request) as webpage:
            self._html = BeautifulSoup(webpage, 'html.parser').prettify()

        self._html = html.unescape(self._html)
        self._html = ' '.join(self.html.split()).strip()
        return self

    def _parse(self):
        if not self.html:
            self._download()

        soup = BeautifulSoup(self.html, 'html.parser')
        # soup = self._consolidate_external_css(soup)
        # inlined_html = self._inline_css(soup.prettify())
        # soup = BeautifulSoup(inlined_html, "html.parser")
        soup = self._clean_style(soup)
        soup = self._filter_tags(soup)
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
        texts = soup.find_all(text=True)
        visible_texts = [text.strip() for text in texts if self._tag_visible(text)]
        cleaned_text = ". ".join(t for t in visible_texts if t)
        self._text = cleaned_text

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
        self._title = soup.title.name.strip() if soup.title else ""

    def _consolidate_external_css(self, soup):
        stylesheets = soup.find_all("link", {"rel": "stylesheet"})
        for s in stylesheets:
            href = s[TAG_HREF]
            css_url = self._normalize_url(href)
            request = Request(css_url, headers={'User-Agent': USER_AGENTS[random.randint(0, USER_AGENTS_LEN - 1)]})

            with urlopen(request) as webpage:
                css_file = webpage.read().decode('unicode_escape')
            style_tag = BeautifulSoup("<style type=\"text/css\">{}</style>".format(css_file), "html.parser")
            s.replaceWith(style_tag)

        soup.renderContents()
        return soup

    def _normalize_url(self, href):
        href = href.strip() if href else None
        if not href or href.startswith('#') or len(href) == 1:
            return False

        link = urljoin(self.url, href) if not href.startswith('http') else href
        return link

    def _inline_css(self, html):
        result = transform(html)
        return result

    def _clean_style(self, soup):
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_tag.decompose()

        soup.renderContents()
        return soup

    def _filter_tags(self, soup):
        # hidden_tags = soup.find_all('div', style=re.compile(r'(display:\s*none|visibility:\s*hidden)'))
        unwanted_divs = soup.find_all(class_=re.compile(r"(footer|header|cookie)", re.IGNORECASE))  # Check menu
        unwanted_sections = soup.find_all(['footer', 'header', 'noscript'])

        for tag in itertools.chain(unwanted_divs, unwanted_sections):
            tag.decompose()

        soup.renderContents()
        return soup
