# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


from scrapy import Item, Field


class Page(Item):
    url = Field()
    html = Field()
    title = Field()
    text = Field()
    metadata = Field()


class GoogleSearchItem(Item):
    name = Field()
    region = Field()
    url = Field()
    html = Field()
    query = Field()
    crawled = Field()
