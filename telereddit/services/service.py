from abc import ABC, abstractmethod

from telereddit.models.exceptions import MediaRetrievalError


class Service(ABC):
    access_token = None
    is_authenticated = False
    has_external_request = True

    @classmethod
    @abstractmethod
    def preprocess(cls, url, json):
        pass

    @classmethod
    @abstractmethod
    def get(cls, url):
        pass

    @classmethod
    @abstractmethod
    def postprocess(cls, response):
        pass

    @classmethod
    @abstractmethod
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
                raise MediaRetrievalError({
                    "reddit_media_url": url,
                    "processed_media_url": processed_url
                })
        return cls.postprocess(response)
