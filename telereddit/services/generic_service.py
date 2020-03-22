import requests
from urllib.parse import urlunparse

from services.service import Service
from media import Media
from content_type import ContentType


class Generic(Service):
    access_token = None
    is_authenticated = False

    @classmethod
    def preprocess(cls, parsed_url, json):
        return urlunparse(parsed_url)

    @classmethod
    def get(cls, url):
        return requests.get(url, stream=True)

    @classmethod
    def postprocess(cls, response):
        file_size = None
        media_type = ContentType.PHOTO

        if '.gif' in response.url:
            media_type = ContentType.GIF
        elif '.mp4' in response.url:
            media_type = ContentType.VIDEO

        if 'Content-length' in response.headers:
            file_size = int(response.headers['Content-length'])

        return Media(response.url, media_type, file_size)

    @classmethod
    def authenticate(cls):
        pass
