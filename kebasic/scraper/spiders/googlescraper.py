import datetime
from urllib.parse import urljoin, urlparse, parse_qsl

from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.project import get_project_settings
from scrapy.utils.response import get_base_url

from kebasic.scraper.items import GoogleSearchItem

"""
A spider to parse the google search result bootstraped from given queries.
"""


class GoogleSearchSpider(Spider):
    name = 'googlesearch'

    with open(get_project_settings()['QUERIES'], "rt", encoding="utf8") as inf:
        queries = list(set(inf))

    region = 'es'
    download_delay = 5
    base_url_fmt = 'http://www.google.{region}/search?hl=en&as_q=&as_epq={query}&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr={country}&as_qdr=all&as_sitesearch=&as_occt=any&safe=images&tbs=&as_filetype=&as_rights='
    download_html = False
    limit_country = False

    def start_requests(self):
        for query in arg_to_iter(self.queries):
            url = self.make_google_search_request(self.region, query)
            yield Request(url=url, meta={'query': query})

    def make_google_search_request(self, country, query):
        if not self.limit_country:
            country = ''
        return self.base_url_fmt.format(country=country, region=self.region, query='+'.join(query.split()).strip('+'))

    def parse(self, response):
        hxs = Selector(response)
        for sel in hxs.xpath('//div[@id="ires"]//li[@class="g"]//h3[@class="r"]'):
            name = u''.join(sel.xpath(".//text()").extract())
            url = _parse_url(sel.xpath('.//a/@href').extract()[0])
            if len(url):
                if self.download_html:
                    yield Request(url=url, callback=self.parse_item, meta={'name': name,
                                                                           'query': response.meta['query']})
                else:
                    yield GoogleSearchItem(url=url, name=name, query=response.meta['query'],
                                           crawled=datetime.datetime.utcnow().isoformat())

        next_page = hxs.xpath('//table[@id="nav"]//td[contains(@class, "b") and position() = last()]/a')
        if next_page:
            url = self._build_absolute_url(response, next_page.xpath('.//@href').extract()[0])
            yield Request(url=url, callback=self.parse, meta={'query': response.meta['query']})

    def parse_item(self, response):
        name = response.meta['name']
        query = response.meta['query']
        url = response.url
        html = response.body[:1024 * 256]
        timestamp = datetime.datetime.utcnow().isoformat()
        yield GoogleSearchItem({'name': name,
                                'url': url,
                                'html': html,
                                'query': query,
                                'crawled': timestamp})

    def _build_absolute_url(self, response, url):
        return urljoin(get_base_url(response), url)


def _parse_url(href):
    """
    Parse the website from anchor href.
    """
    queries = dict(parse_qsl(urlparse(href).query))
    return queries.get('q', '')
