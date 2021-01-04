# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


class MediaScraperItem(scrapy.Item):
    title = scrapy.Field()
    subtitle = scrapy.Field()
    link = scrapy.Field()
    text = scrapy.Field()
    time = scrapy.Field()
    date = scrapy.Field()
    domain = scrapy.Field()
    views = scrapy.Field()
    language = scrapy.Field()
    category = scrapy.Field()
