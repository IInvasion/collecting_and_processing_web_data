"""Instagram spiders manual runner."""

import sys

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from InstaParser.spiders.InstaUserFollows import InstauserfollowsSpider
from InstaParser import settings

def _main():
    """Entry point."""
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstauserfollowsSpider)

    process.start()


if __name__ == '__main__':
    sys.exit(_main())
