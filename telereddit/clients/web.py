from urllib.parse import urlparse

from clients.gfycat import Gfycat
from clients.vreddit import Vreddit
from clients.imgur import Imgur


class Web:
    gfycat = Gfycat()
    vreddit = Vreddit()
    imgur = Imgur()

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

        return media

        # else if 'imgur.com' in base_url:
        #
        # else if 'youtube.com' in base_url or 'youtu.be' in base_url:
        #
        # else:
