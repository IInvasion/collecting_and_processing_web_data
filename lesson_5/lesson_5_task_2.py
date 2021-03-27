""" 2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
   Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары."""

import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from pymongo import MongoClient


_MVIDEO_URI = 'https://www.mvideo.ru'


def _main():
    """Entry point."""

    client = MongoClient('localhost', 27017)
    mongo_base = client['mvideo_goods_db']
    collection = mongo_base['goods']

    chrome_options = Options()
    chrome_options.add_argument('start-maximized')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(_MVIDEO_URI)

    bestsellers = driver.find_elements_by_xpath('//div[contains(text(),"Хиты продаж")]/ancestor::div[contains(@class, "section")]')

    item = bestsellers[0].find_element_by_tag_name('ul')

    item_params = json.loads(item.get_attribute('data-init-param'))
    items_number = item_params['ajaxContentLoad']['total']

    items = item.find_elements_by_class_name('gallery-list-item')

    while len(items) < items_number:
        button = WebDriverWait(item, 10).until(
            ec.element_to_be_clickable((By.XPATH, '//a[contains(@class, "next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right")]'))
            )
        button.click()
        time.sleep(3)
        items = item.find_elements_by_class_name('gallery-list-item')

    goods = bestsellers[0].find_elements_by_tag_name('li')

    # goods_list = list()
    for element in goods:
        good = element.find_element_by_tag_name('a')
        goods_dict = json.loads(good.get_attribute('data-product-info'))
        goods_dict['link'] = _MVIDEO_URI + good.get_attribute('href')
        goods_dict['img_link'] = good.find_element_by_tag_name('img').get_attribute('src')
        goods_dict['productPriceLocal'] = float(goods_dict['productPriceLocal'])

        # goods_list.append(goods_dict)
        collection.update_one(goods_dict, {'$setOnInsert': goods_dict}, upsert=True)

    


if __name__ == '__main__':
    sys.exit(_main())
