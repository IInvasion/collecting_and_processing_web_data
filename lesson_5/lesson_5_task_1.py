"""1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить
      данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)."""

import sys
import misc
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from selenium.common import exceptions


_LOGIN = misc.login
_PASSWORD = misc.password


def _parse_email(driver):
    """Parse email."""

    letter = dict()

    time.sleep(1)

    letter_contact = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.CLASS_NAME, 'letter-contact')
        )
    ).get_attribute('title')

    letter_subject = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.XPATH, '//h2')
        )
    ).text

    letter_date = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.XPATH, '//div[@class="letter__date"]')
        )
    ).text

    letter_body = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.CLASS_NAME, 'letter__body')
        )
    ).text

    letter['sender'] = letter_contact
    letter['subject'] = letter_subject
    letter['date'] = letter_date
    letter['body'] = letter_body

    return letter


def _main():
    """Entry point."""

    client = MongoClient('localhost', 27017)
    mongo_base = client['mail_db']
    collection = mongo_base['messages']

    chrome_options = Options()
    chrome_options.add_argument('start-maximized')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://mail.ru')

    login = driver.find_element_by_name('login')
    login.send_keys(_LOGIN)
    login.send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.NAME, 'password'))
            )

    password = driver.find_element_by_name('password')
    password.send_keys(_PASSWORD)
    password.send_keys(Keys.ENTER)

    first_letter = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (By.CLASS_NAME, 'js-letter-list-item')
        )
    )
    first_letter.click()

    while True:
        email = _parse_email(driver)
        try:
            collection.update_one(email, {'$setOnInsert': email}, upsert=True)

            button_next = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable(
                    (By.CLASS_NAME, 'button2_arrow-down')
                )
            )
            button_next.click()
        except:
            print('All email letters are over')
            break


if __name__ == '__main__':
    sys.exit(_main())
