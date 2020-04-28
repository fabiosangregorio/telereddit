from abc import ABC, abstractmethod
import requests

from telereddit.models.exceptions import MediaRetrievalError


class Service(ABC):
    has_external_request = True
    is_authenticated = False
    access_token = None

    @classmethod
    def preprocess(cls, url, json):
        return url

    @classmethod
    def get(cls, url):
        return requests.get(url, stream=True)

    @classmethod
    @abstractmethod
    def postprocess(cls, response):
        pass

    @classmethod
    def authenticate(cls):
        pass

    @classmethod
    def get_media(cls, url, json):
        processed_url = cls.preprocess(url, json)

        response = cls.get(processed_url)
        if cls.has_external_request:
            if cls.is_authenticated and response.status_code == 401:
                cls.authenticate()
                response = cls.get(processed_url)
            if response.status_code >= 300:
                raise MediaRetrievalError(
                    {
                        "service": cls.__name__,
                        "reddit_media_url": url,
                        "processed_media_url": processed_url,
                    }
                )
        return cls.postprocess(response)
