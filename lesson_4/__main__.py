"""1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru,
   yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
   - название источника;
   - наименование новости;
   - ссылку на новость;
   - дата публикации.
2. Сложить собранные данные в БД"""

import sys
import requests
from lxml import html
from pprint import pprint
from datetime import datetime, date
from pymongo import MongoClient


_LINK_MAILRU_NEWS = 'https://news.mail.ru/'
_LINK_LENTARU = 'https://lenta.ru/'
_LINK_YANDEX_NEWS = 'https://yandex.ru/news/'


_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}


def _parse_news_mailru():
    """news.mail.ru scrapper."""

    req = requests.get(_LINK_MAILRU_NEWS, headers=_HEADERS)
    dom = html.fromstring(req.text)

    news = dom.xpath('//ul[contains(@class, "list")]/li[contains(@class, "list__item")]/a[position()=1]')

    news_list = list()
    for item in news:
        element = dict()

        news_name = item.xpath('.//text()')
        element['name'] = str(news_name[0]).replace(u'\xa0', u' ')

        news_link = item.xpath('../a/@href')
        element['link'] = str(news_link[0])

        req = requests.get(element['link'], headers=_HEADERS)
        dom = html.fromstring(req.text)

        news_date = dom.xpath('//span/@datetime')
        news_date = datetime.strptime(str(news_date[0]), '%Y-%m-%dT%H:%M:%S%z')
        element['date'] = news_date.strftime('%Y-%m-%d %H:%M')

        news_source = dom.xpath('//span[contains(@class, "note")]/*/span[contains(@class, "link__text")]/text()')
        element['source'] = str(news_source[0])

        news_list.append(element)

    return news_list


def _parse_news_lentaru():
    """Lenta.ru news scrapper."""
    req = requests.get(_LINK_LENTARU, headers=_HEADERS)
    dom = html.fromstring(req.text)

    news = dom.xpath('//section[contains(@class, "row b-top")]//div[contains(@class, "item")]')

    news_list = list()
    for item in news:
        element = dict()

        news_name = item.xpath('.//time/parent::a/text()')
        element['name'] = str(news_name[0]).replace(u'\xa0', u' ')

        news_link = item.xpath('.//time/parent::a/@href')
        element['link'] = 'https://lenta.ru' + str(news_link[0])

        news_date = item.xpath('.//time/@datetime')
        element['date'] = str(news_date[0]).strip()

        element['source'] = 'lenta.ru'

        news_list.append(element)

    return news_list


def _parse_news_yandex():
    """Yandex news scrapper."""
    req = requests.get(_LINK_YANDEX_NEWS, headers=_HEADERS)
    dom = html.fromstring(req.text)

    news = dom.xpath('//div[contains(@class, "news-top-flexible-stories")]/div[contains(@class, "mg-grid__col")]')

    news_list = list()
    for item in news:
        element = dict()

        news_name = item.xpath('.//h2/text()')
        element['name'] = str(news_name[0]).replace(u'\xa0', u' ')

        news_link = item.xpath('.//span[contains(@class, "mg-card-source__source")]/a/@href')
        element['link'] = str(news_link[0])

        news_date = item.xpath('.//span[contains(@class, "mg-card-source__time")]/text()')
        news_time = str(news_date[0])
        curr_time = datetime.today()
        curr_date = date.today()
        if (int(news_time[:2]) > curr_time.hour):
            date_string = str(curr_date.year) + '-' + str(curr_date.month) + '-' + str(curr_date.day - 1)
        else:
            date_string = str(curr_date.year) + '-' + str(curr_date.month) + '-' + str(curr_date.day)
        date_string += ' ' + news_time
        element['date'] = date_string

        news_source = item.xpath('.//span[contains(@class, "mg-card-source__source")]/a/text()')
        element['source'] = str(news_source[0])

        news_list.append(element)

    return news_list


def _parse_news():
    """News scrapper."""

    news_list = list()
    news_list.extend(_parse_news_mailru())
    news_list.extend(_parse_news_lentaru())
    news_list.extend(_parse_news_yandex())

    return news_list


def _main():
    """Entry point."""
    news_list = _parse_news()

    client = MongoClient()
    db = client['news']
    news = db.news

    for item in news_list:
        news.update_one(item, {'$setOnInsert': item}, upsert=True)


if __name__ == '__main__':
    sys.exit(_main())
