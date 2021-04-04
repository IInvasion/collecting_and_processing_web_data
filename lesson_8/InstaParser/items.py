# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    is_following = scrapy.Field()
    is_follower = scrapy.Field()
    user_follow_id = scrapy.Field()
    user_follow_name = scrapy.Field()
    user_follow_photo = scrapy.Field()
