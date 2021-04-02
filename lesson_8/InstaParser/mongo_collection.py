"""4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
   5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь"""

import sys
import misc
from pymongo import MongoClient
from pprint import pprint


def _main():
    """Entry point."""
    client = MongoClient('localhost', 27017)

    db = client['follows']

    users = db.InstaUserFollows
    for user in misc.parse_users:
        followers = users.find({'user_name': user, 'user_follower': True}, {'_id': False})
        following = users.find({'user_name': user, 'user_following': True}, {'_id': False})


if __name__ == '__main__':
    sys.exit(_main())
