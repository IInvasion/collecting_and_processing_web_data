import scrapy
from scrapy.http import HtmlResponse
from leruamerlenparser.items import LeruamerlenparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'Leroymerlin'
    allowed_domains = ['https://leroymerlin.ru/']


    def __init__(self, query):
        """Constructor."""
        super(LeroymerlinSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']
        self.query = query


    def parse(self, response):
        """Goods parser."""
        goods_links = response.xpath('//uc-plp-item-new/@href').extract()
        for link in goods_links:
            yield response.follow(link, callback=self.parse_item, dont_filter=True)

        next_page = response.xpath('//div[@class = "next-paginator-button-wrapper"]/a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse, dont_filter=True)


    def parse_item(self, response:HtmlResponse):
        """Parse item."""
        loader = ItemLoader(item=LeruamerlenparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//uc-pdp-media-carousel//picture[@slot="pictures"]/img/@src')
        loader.add_xpath('characteristics', '//dt[@class="def-list__term"]/text() | //dd[@class="def-list__definition"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')

        yield loader.load_item()
