"""Leroymerlin parser runner."""

import sys
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from leruamerlenparser.spiders.Leroymerlin import LeroymerlinSpider
from leruamerlenparser import settings


def _main():
    """Entry point."""
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, query='Шторы')

    process.start()


if __name__ == '__main__':
    sys.exit(_main())
