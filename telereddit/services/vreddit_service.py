import helpers
import requests
from services.service import Service

from media import Media


class Vreddit(Service):
    is_authenticated = False

    @classmethod
    def preprocess(cls, parsed_url, json):
        fallback_url = helpers.chained_get(json, ['media', 'reddit_video', 'fallback_url'])
        url = fallback_url if fallback_url else f'{parsed_url}/DASH_1_2_M'
        return url

    @classmethod
    def get(cls, url):
        return requests.get(url, stream=True)

    @classmethod
    def postprocess(cls, response):
        media = Media(response.url, 'gif')
        if 'Content-length' in response.headers:
            media.size = int(response.headers['Content-length'])
        return media

    @classmethod
    def authenticate(cls):
        pass
