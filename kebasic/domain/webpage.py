import random
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

USER_AGENTS = [
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]
USER_AGENTS_LEN = len(USER_AGENTS)


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
        request = Request(self._url, headers={'User-Agent': USER_AGENTS[random.randint(0, USER_AGENTS_LEN - 1)]})
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
        if 'class' in element.parent.attrs and any(['blog-categories', 'minor-meta']) in element.parent['class']:
            print(element.parent['class'])
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
