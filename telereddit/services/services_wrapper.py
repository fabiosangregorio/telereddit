"""Entrypoint of the whole services pattern."""

import logging
from urllib.parse import urlparse
from typing import Any
import icontract

from telereddit.services.gfycat_service import Gfycat
from telereddit.services.vreddit_service import Vreddit
from telereddit.services.imgur_service import Imgur
from telereddit.services.youtube_service import Youtube
from telereddit.services.generic_service import Generic
from telereddit.models.media import Media


class ServicesWrapper:
    """
    Entrypoint of the whole services pattern.

    It represents a Facade which hides the complexity of the media retrieval
    across various services and providers.

    An instance for each service class is set at class initialization.
    """

    gfycat: Gfycat = Gfycat()
    vreddit: Vreddit = Vreddit()
    imgur: Imgur = Imgur()
    youtube: Youtube = Youtube()
    generic: Generic = Generic()

    @classmethod
    @icontract.require(
        lambda cls, url, json: url is not None, "url must not be None"
    )
    @icontract.ensure(lambda result: result is not None)
    def get_media(cls, url: str, json: Any = {}) -> Media:
        """
        Given the url from the Reddit json, return the corresponding media obj.

        Main function with the responsibility to choose the right service.

        Parameters
        ----------
        url : str
            Url from Reddit API json.
        json : json
            (Default value = {})

            Reddit data json containing media fallback urls.

        Returns
        -------
        `telereddit.models.media.Media`
            The media object corresponding to the media post url.

        """
        base_url: str = urlparse(url).netloc
        media: Media

        if "gfycat.com" in base_url:
            media = cls.gfycat.get_media(url, json)
        elif "v.redd.it" in base_url:
            media = cls.vreddit.get_media(url, json)
        elif "imgur.com" in base_url:
            media = cls.imgur.get_media(url, json)
        elif "youtube.com" in base_url or "youtu.be" in base_url:
            media = cls.youtube.get_media(url, json)
        else:
            logging.info(
                f"services_wrapper: no suitable service found. base_url: {base_url}"
            )
            media = cls.generic.get_media(url, json)

        return media
