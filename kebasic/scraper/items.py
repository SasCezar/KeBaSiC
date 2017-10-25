# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


from scrapy import Item, Field


class Page(Item):
    """
    Defines a item for Scrapy, this item is a web page
    """
    url = Field()  # Is the URL of the web page
    html = Field()  # Contains the HTML text of the web page
    title = Field()  # Is the title of the web page
    text = Field()  # Is the visible tex contained in the page
    meta_keywords = Field()  # Contains the value of the meta-tag "keywords"
    meta_description = Field()  # Contains the value of the meta-tag "description"
