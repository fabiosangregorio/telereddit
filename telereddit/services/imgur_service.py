import json

import requests

import secret
from services.service import Service
from media import Media, MediaType


class Imgur(Service):
    access_token = None
    is_authenticated = False

    def __init__(self):
        Imgur.authenticate()

    @classmethod
    def preprocess(cls, parsed_url, json):
        url = parsed_url.path.replace('/', '')
        if '.' in url:
            media_hash = url.rpartition('.')[0]
        else:
            media_hash = url
        return f'https://api.imgur.com/3/image/{media_hash}'

    @classmethod
    def get(cls, url):
        return requests.get(url, headers={'Authorization': f'Client-ID {secret.IMGUR_CLIENT_ID}'})

    @classmethod
    def postprocess(cls, response):
        data = json.loads(response.content)['data']
        media = None
        if 'image/jpeg' in data['type'] or 'image/png' in data['type']:
            media = Media(data['link'], MediaType.PHOTO, data['size'])
        elif 'video' or 'image/gif' in data['type']:
            media = Media(data['mp4'], MediaType.VIDEO, data['mp4_size'])

        return media

    @classmethod
    def authenticate(cls):
        pass
