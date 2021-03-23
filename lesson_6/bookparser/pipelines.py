# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserLabirintPipeline:
    """Labirint.ru parser pipeline."""
    def __init__(self):
        """Constructor."""
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books


    def process_item(self, item, spider):
        """Process item."""
        collection = self.mongo_base[spider.name]

        item['own_price'] = int(item['own_price'])

        if item['sale_price']:
            item['sale_price'] = int(item['sale_price'])

        if item['rating']:
            item['rating'] = float(item['rating'])

        collection.update_one(item, {'$setOnInsert': item}, upsert=True)

        return item


class BookParserBook24Pipeline:
    """Book24.ru parser pipeline."""
    def __init__(self):
        """Constructor."""
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books

    def process_item(self, item, spider):
        """Process item."""
        collection = self.mongo_base[spider.name]

        item['title'] = item['title'].strip().replace('\n', '')

        if isinstance(item['own_price'], str):
            item['own_price'] = int(item['own_price'].replace(' р.', '').replace(' ', ''))

        if isinstance(['sale_price'], str):
            item['sale_price'] = int(item['sale_price'])

        if item['rating']:
            item['rating'] = float(item['rating'])

        collection.update_one(item, {'$setOnInsert': item}, upsert=True)

        return item
