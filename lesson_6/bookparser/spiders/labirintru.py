import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserLabirintItem


class LabirintruSpider(scrapy.Spider):
    """Labirint.ru spider."""
    name = 'labirintru'
    custom_settings = {
        'ITEM_PIPELINES': {'bookparser.pipelines.BookparserLabirintPipeline': 300}
    }
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/novelty/?page=1']

    def parse(self, response):
        """Novelty page parser."""
        links = response.xpath('//a[@class="product-title-link"]/@href').extract()
        for link in links:
            yield response.follow('https://www.labirint.ru' + link, callback=self.parse_item)

        next_page = response.xpath('//a[@class="pagination-next__text"]/@href').extract_first()
        if next_page:
            yield response.follow('https://www.labirint.ru/novelty/' + next_page, callback=self.parse)


    def parse_item(self, response:HtmlResponse):
        """Book item parser."""
        title = response.xpath('//h1/text()').extract_first()
        link = response.url
        author = response.xpath('//a[@data-event-label="author"]/text()').extract_first()
        own_price = response.xpath('//span[@class="buying-price-val-number"]/text()').extract_first()
        if not own_price:
            own_price = response.xpath('//span[@class="buying-priceold-val-number"]/text()').extract_first()
        sale_price = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').extract_first()
        rating = response.xpath('//div[@id="rate"]/text').extract_first()

        yield BookparserLabirintItem(title=title, link=link, author=author, own_price=own_price, sale_price=sale_price,
                                     rating=rating)
