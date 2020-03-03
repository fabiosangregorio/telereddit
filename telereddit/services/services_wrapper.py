import logging
from urllib.parse import urlparse

from services.gfycat_service import Gfycat
from services.vreddit_service import Vreddit
from services.imgur_service import Imgur
from services.youtube_service import Youtube


class ServicesWrapper:
    gfycat = Gfycat()
    vreddit = Vreddit()
    imgur = Imgur()
    youtube = Youtube()

    @classmethod
    def get_media(cls, url, json={}):
        parsed_url = urlparse(url)
        base_url = parsed_url.netloc
        media = None

        if 'gfycat.com' in base_url:
            media = cls.gfycat.get_media(parsed_url, json)
        elif 'v.redd.it' in base_url:
            media = cls.vreddit.get_media(parsed_url, json)
        elif 'imgur.com' in base_url:
            media = cls.imgur.get_media(parsed_url, json)
        elif 'youtube.com' in base_url or 'youtu.be' in base_url:
            media = cls.youtube.get_media(parsed_url, json)
        else:
            logging.warning("services_wrapper: no suitable service found")

        return media
