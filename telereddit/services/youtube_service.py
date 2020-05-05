from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType
import telereddit.helpers as helpers


class Youtube(Service):
    """ """

    access_token = None
    is_authenticated = False
    has_external_request = False

    @classmethod
    def preprocess(cls, url, json):
        """

        Parameters
        ----------
        url :
            
        json :
            

        Returns
        -------

        
        """
        oembed_url = helpers.chained_get(json, ["media", "oembed", "url"])
        return oembed_url if oembed_url else url

    @classmethod
    def get(cls, url):
        """

        Parameters
        ----------
        url :
            

        Returns
        -------

        
        """
        return url

    @classmethod
    def postprocess(cls, url):
        """

        Parameters
        ----------
        url :
            

        Returns
        -------

        
        """
        return Media(url, ContentType.YOUTUBE)
