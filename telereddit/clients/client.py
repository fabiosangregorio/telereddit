from abc import ABC, abstractmethod


class Client(ABC):
    @abstractmethod
    def preprocess(self, parsed_url):
        pass

    @abstractmethod
    def get(self, url, status):
        pass

    @abstractmethod
    def postprocess(self, response):
        pass

    @abstractmethod
    def authenticate(self):
        pass

    def get_media(self, url):
        processed_url = self.preprocess(url)
        response = self.get(processed_url)
        if response.status == 401:
            self.authenticate()
            response = self.get(processed_url)
        elif response.status != 200:
            response = self.get(processed_url, response.status)
        return self.postprocess(response)
