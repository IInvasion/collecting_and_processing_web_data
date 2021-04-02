# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import os
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from pymongo import MongoClient


class LeruamerlenparserPipeline:
    """Leroymerlin parser spider pipeline."""

    def __init__(self):
        """Constructor."""
        client = MongoClient()
        self.mongo_base = client.goods


    def process_item(self, item, spider):
        """Process item."""
        collection = self.mongo_base[spider.query]

        collection.update_one(item, {'$setOnInsert': item}, upsert=True)

        return item


class LeroyMerlinPhotosPipeline(ImagesPipeline):
    """Leroymerlin parser photos download pipeline."""

    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)


    def file_path(self, request, response=None, info=None, *, item=None):
        """File path."""
        if item:
            return f"{item['name']}/" + os.path.basename(urlparse(request.url).path)


    def item_completed(self, results, item, info):
        """Item completed."""
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]

        return item
