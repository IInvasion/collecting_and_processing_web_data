import scrapy
import re
import json
from InstaParser import misc
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from InstaParser.items import InstaparserItem


class InstauserfollowsSpider(scrapy.Spider):
    """Instaparser instauserfollows spider."""
    name = 'InstaUserFollows'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    ints_login = misc.username
    inst_pass = misc.password
    parse_users = misc.parse_users
    followers_hash = '5aefa9893005572d237da5068082d8d5'
    following_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
    graphql_url = 'https://www.instagram.com/graphql/query/'


    def parse(self, response:HtmlResponse):
        """Instaparser instauserfollow parser."""
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_login,
            formdata={'username': self.ints_login, 'enc_password': self.inst_pass, 'queryParams': {}, 'optIntoOneTap': 'false'},
            headers={'X-CSRFToken': csrf_token}
        )


    def user_login(self, response:HtmlResponse):
        """User login."""
        j_body = response.json()
        if j_body.get('authenticated'):
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.parse_user_data,
                    cb_kwargs={'username': user}
                )


    def parse_user_data(self, response:HtmlResponse, username):
        """User data parse."""
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id, 'include_reel': 'true', 'fetch_mutual': 'false', 'first': 12}
        url_following = f'{self.graphql_url}?query_hash={self.following_hash}&{urlencode(variables)}'

        yield response.follow(
            url_following,
            callback=self.parse_user_following,
            cb_kwargs={'variables': deepcopy(variables),
                       'username': username,
                       'user_id': user_id}
        )

        variables = {'id': user_id, 'include_reel': 'true', 'fetch_mutual': 'true', 'first': 24}
        url_followers = f'{self.graphql_url}?query_hash={self.followers_hash}&{urlencode(variables)}'

        yield response.follow(
            url_followers,
            callback=self.parse_user_followers,
            cb_kwargs={'variables': deepcopy(variables),
                       'username': username,
                       'user_id': user_id}
        )


    def parse_user_following(self, response:HtmlResponse, variables, username, user_id):
        """User followings parse."""
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_following = f'{self.graphql_url}?query_hash={self.following_hash}&{urlencode(variables)}'

            yield response.follow(
                url_following,
                callback=self.parse_user_following,
                cb_kwargs={'variables': deepcopy(variables),
                           'username': username,
                           'user_id': user_id}
            )

        followings = j_body.get('data').get('user').get('edge_follow').get('edges')
        for following in followings:
            yield InstaparserItem(
                user_name=username,
                user_id=user_id,
                is_following=True,
                is_follower=False,
                user_follow_id=following.get('node').get('id'),
                user_follow_name=following.get('node').get('username'),
                user_follow_photo=following.get('node').get('profile_pic_url')
            )


    def parse_user_followers(self, response:HtmlResponse, variables, username, user_id):
        """User followers parse."""
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_followers = f'{self.graphql_url}?query_hash={self.followers_hash}&{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.parse_user_followers,
                cb_kwargs={'variables': deepcopy(variables),
                           'username': username,
                           'user_id': user_id}
            )

        followers = j_body.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            yield InstaparserItem(
                user_name=username,
                user_id=user_id,
                is_following=False,
                is_follower=True,
                user_follow_id=follower.get('node').get('id'),
                user_follow_name=follower.get('node').get('username'),
                user_follow_photo=follower.get('node').get('profile_pic_url')
            )


    def fetch_csrf_token(self, text):
        """Fetch authorization token."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()

        return matched.split(':').pop().replace(r'"', '')


    def fetch_user_id(self, text, username):
        """Fetch wish user id."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()

        return json.loads(matched).get('id')
