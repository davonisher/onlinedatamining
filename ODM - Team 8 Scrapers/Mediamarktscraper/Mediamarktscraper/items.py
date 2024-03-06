# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class mediamarktscaperItem(scrapy.Item):
    # define the fields for your item here like:
    brand = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    rated = scrapy.Field()
    stars = scrapy.Field()
    url = scrapy.Field()
    pass
