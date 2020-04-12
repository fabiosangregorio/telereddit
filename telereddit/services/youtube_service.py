from telereddit.services.service import Service
from telereddit.media import Media
from telereddit.content_type import ContentType
import telereddit.helpers as helpers


class Youtube(Service):
    access_token = None
    is_authenticated = False
    has_external_request = False

    @classmethod
    def preprocess(cls, url, json):
        oembed_url = helpers.chained_get(json, ['media', 'oembed', 'url'])
        return oembed_url if oembed_url else url

    @classmethod
    def get(cls, url):
        return url

    @classmethod
    def postprocess(cls, url):
        return Media(url, ContentType.YOUTUBE)

    @classmethod
    def authenticate(cls):
        pass
