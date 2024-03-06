# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CoolbluescraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    price = scrapy.Field()
    reviews = scrapy.Field()
    stars = scrapy.Field()
    gaming_videocard = scrapy.Field()
    processor = scrapy.Field()
    screen_size = scrapy.Field()
    Coolblues_keuze = scrapy.Field()
    url = scrapy.Field()
    pass
