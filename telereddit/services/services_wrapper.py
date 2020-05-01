import logging
from urllib.parse import urlparse

from telereddit.services.gfycat_service import Gfycat
from telereddit.services.vreddit_service import Vreddit
from telereddit.services.imgur_service import Imgur
from telereddit.services.youtube_service import Youtube
from telereddit.services.generic_service import Generic


class ServicesWrapper:
    """ """
    gfycat = Gfycat()
    vreddit = Vreddit()
    imgur = Imgur()
    youtube = Youtube()
    generic = Generic()

    @classmethod
    def get_media(cls, url, json={}):
        """

        Parameters
        ----------
        url :
            
        json :
             (Default value = {})

        Returns
        -------

        """
        parsed_url = urlparse(url)
        base_url = parsed_url.netloc

        if "gfycat.com" in base_url:
            media = cls.gfycat.get_media(url, json)
        elif "v.redd.it" in base_url:
            media = cls.vreddit.get_media(url, json)
        elif "imgur.com" in base_url:
            media = cls.imgur.get_media(url, json)
        elif "youtube.com" in base_url or "youtu.be" in base_url:
            media = cls.youtube.get_media(url, json)
        else:
            logging.warning(
                f"services_wrapper: no suitable service found. base_url: {base_url}"
            )
            media = cls.generic.get_media(url, json)

        return media
