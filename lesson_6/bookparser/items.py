# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserLabirintItem(scrapy.Item):
    """Bookparser item."""
    title = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    own_price = scrapy.Field()
    sale_price = scrapy.Field()
    rating = scrapy.Field()


class BookparserBook24Item(scrapy.Item):
    """Bookparser item."""
    title = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    own_price = scrapy.Field()
    sale_price = scrapy.Field()
    rating = scrapy.Field()
