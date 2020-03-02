from abc import ABC, abstractmethod


class Client(ABC):
    is_authenticated = False

    @classmethod
    @abstractmethod
    def preprocess(cls, parsed_url, json):
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
        if cls.is_authenticated and response.status_code == 401:
            cls.authenticate()
            response = cls.get(processed_url)
        if response.status_code >= 300:
            raise Exception("client.get_media: error in getting the media")
        return cls.postprocess(response)
