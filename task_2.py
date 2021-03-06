"""2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis). Найти среди них любое,
   требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл."""

import requests
import sys
import misc
import json


token = misc.token
URL = 'https://api.telegram.org/bot'


def _main():
    """Entry point."""
    req = requests.get(URL + token + '/getMe')

    with open('response.json', 'w') as f_obj:
        json.dump(req.text, f_obj)


if __name__ == '__main__':
    sys.exit(_main())
