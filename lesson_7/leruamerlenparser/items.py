# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose


def process_price(price):
    """Process price."""
    return int(price.replace(' ', ''))


def process_characteristics(params):
    """Process characteristics."""
    params = [x.replace('\n', '').strip() for x in params]

    return dict(zip(params[1::2], params[2::2]))


class LeruamerlenparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose())
    characteristics = scrapy.Field(output_processor=TakeFirst(), input_processor=Compose(process_characteristics))
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(process_price))


