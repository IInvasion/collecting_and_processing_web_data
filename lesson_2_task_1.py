""" Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов Superjob и HH.
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия. ### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. """

import requests
import sys
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint

_HH_LINK = 'https://hh.ru/search/vacancy'
_SJ_LINK = 'https://russia.superjob.ru/vacancy/search/'
_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}


def _parse_hh(vacancy):
    """Headhunter parser."""
    vacancies_info = []

    params = {
        'text': vacancy,
        'search_field': 'name',
        'page': ''
    }

    req = requests.get(_HH_LINK, params=params, headers=_HEADERS)

    if req.ok:
        soup = bs(req.text,'html.parser')
        
        page_block = soup.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = '1'
        else:
            last_page = int(page_block.find_all('a', {'class': 'HH-Pager-Control'})[-2].getText())

    for page in range(0, last_page):
        params['page'] = page
        req = requests.get(_HH_LINK, params=params, headers=_HEADERS)
        if req.ok:
            soup = bs(req.text,'html.parser')
            vacancies = soup.find('div', {'data-qa': 'vacancy-serp__results'}) \
                            .find_all('div', {'class': 'vacancy-serp-item'})
            for vacancy in vacancies:
                vacancies_info.append(_parse_vacancy_hh(vacancy))

    return vacancies_info


def _parse_vacancy_hh(vacancy):
    """Headhunter vacancy parser."""

    vacancy_info = {}

    vacancy_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText().replace(u'\xa0', u' ')
    vacancy_info['vacancy_name'] = vacancy_name

    # vacancy salary
    salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.getText() \
                        .replace(u'\xa0', u'')

        salary = re.split(r'\s|-', salary)
        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
        else:
            salary_min = int(salary[0])
            salary_max = int(salary[1])
        salary_currency = salary[2]

    vacancy_info['salary_min'] = salary_min
    vacancy_info['salary_max'] = salary_max
    vacancy_info['salary_currency'] = salary_currency

    vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
    vacancy_info['vacancy_link'] = vacancy_link

    # vacancy site
    vacancy_info['site'] = 'hh.ru'

    return vacancy_info


def _parse_sj(vacancy):
    """Superjob parser."""

    vacancies_info = []

    params = {
        'keywords': vacancy,
        'profession_only': '1',
        'page': ''
    }

    req = requests.get(_SJ_LINK, params=params, headers=_HEADERS)

    if req.ok:
        soup = bs(req.text,'html.parser')
        page_block = soup.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        last_page = 1
    else:
        page_block = page_block.findParent()
        last_page = int(page_block.find_all('a')[-2].getText())

    for page in range(0, last_page + 1):
        params['page'] = page
        req = requests.get(_SJ_LINK, params=params, headers=_HEADERS)

        if req.ok:
            soup = bs(req.text,'html.parser')
            vacancy_items = soup.find_all('div', {'class': 'f-test-vacancy-item'})

            for vacancy in vacancy_items:
                vacancies_info.append(_parse_vacancy_sj(vacancy))

    return vacancies_info


def _parse_vacancy_sj(vacancy):
    """Superjob vacancy parser."""

    vacancy_info = {}

    # vacancy name
    vacancy_name = vacancy.find_all('a')
    vacancy_name = vacancy_name[0].getText()
    vacancy_info['vacancy_name'] = vacancy_name

    # vacancy salary
    salary = vacancy.find('span', {'class': 'f-test-text-company-item-salary'}) \
                    .findChildren()
    if salary[0].getText() == 'По договорённости':
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary[1].getText().split()
        salary_currency = salary[-1]
        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1] + salary[2])
        elif salary[0] == 'от':
            salary_min = int(salary[1] + salary[2])
            salary_max = None
        elif len(salary) == 3:
            salary_min = salary_max = int(salary[0] + salary[1])
        else:
            salary_min = int(salary[0] + salary[1])
            salary_max = int(salary[3] + salary[4])

    vacancy_info['salary_min'] = salary_min
    vacancy_info['salary_max'] = salary_max
    vacancy_info['salary_currency'] = salary_currency

    # vacancy link
    vacancy_link = vacancy.find_all('a')
    if len(vacancy_link) > 1:
        vacancy_link = vacancy_link[-2]['href']
    else:
        vacancy_link = vacancy_link[0]['href']
    vacancy_info['vacancy_link'] = f'https://www.superjob.ru{vacancy_link }'

    # vacancy site
    vacancy_info['site'] = 'www.superjob.ru'

    return vacancy_info


def parse_vacancy(vacancy):
    """Vacancy parser."""

    vacancies_info = []
    vacancies_info.extend(_parse_hh(vacancy))
    vacancies_info.extend(_parse_sj(vacancy))
    df = pd.DataFrame(vacancies_info)

    return df


def _main():
    """Entry point."""
    vacancy = 'Разработчик'
    df = parse_vacancy(vacancy)
    print(df)


if __name__ == '__main__':
    sys.exit(_main())
