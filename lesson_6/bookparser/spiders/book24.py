import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserBook24Item


class Book24Spider(scrapy.Spider):
    name = 'book24'
    custom_settings = {
        'ITEM_PIPELINES': {'bookparser.pipelines.BookParserBook24Pipeline': 300},
        'DOWNLOAD_DELAY': 0
    }
    url = 'https://book24.ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/novie-knigi/']

    def parse(self, response):
        links = response.xpath('//a[@class="book-preview__image-link"]/@href').extract()
        for link in links:
            yield response.follow(self.url + link, callback=self.parse_item)
        next_page = response.xpath('//a[contains(text(), "Далее")]/@href').extract_first()

        if next_page:
            yield response.follow(self.url + next_page, callback=self.parse)


    def parse_item(self, response:HtmlResponse):
        """Book item parser."""
        title = response.xpath('//h1/text()').extract_first()
        link = response.url
        author = response.xpath('//a[contains(@itemprop, "author")]/text()').extract_first()
        own_price = response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
        if not own_price:
            own_price = response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
            sale_price = None
        else:
            sale_price = response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
        rating = response.xpath('//div[contains(@class, "rating__rate-value")]/text()').extract_first()

        yield BookparserBook24Item(title=title, link=link, author=author, own_price=own_price, sale_price=sale_price,
                                   rating=rating)
