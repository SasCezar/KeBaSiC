# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Page(scrapy.Item):
    url = scrapy.Field()
    domain = scrapy.Field()
    html = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    metadata = scrapy.Field()
