from services.service import Service
from media import Media, MediaType

from telereddit import helpers


class Youtube(Service):
    access_token = None
    is_authenticated = False
    has_external_request = False

    @classmethod
    def preprocess(cls, parsed_url, json):
        oembed_url = helpers.chained_get(json, ['media', 'oembed', 'url'])
        return oembed_url if oembed_url else parsed_url

    @classmethod
    def get(cls, url):
        return url

    @classmethod
    def postprocess(cls, url):
        return Media(url, MediaType.YOUTUBE)

    @classmethod
    def authenticate(cls):
        pass
