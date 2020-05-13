"""Service for Imgur images and videos."""
import json
from urllib.parse import urlparse
import requests

from telereddit.config.config import secret
from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType


class Imgur(Service):
    """Service for Imgur images and videos."""

    @classmethod
    def preprocess(cls, url, json):
        """
        Override of `telereddit.services.service.Service.preprocess` method.

        Gets the media hash from the url and creates the accepted provider media
        url.
        """
        url = urlparse(url).path.replace("/", "")
        if "." in url:
            media_hash = url.rpartition(".")[0]
        else:
            media_hash = url
        return f"https://api.imgur.com/3/image/{media_hash}"

    @classmethod
    def get(cls, url):
        """
        Override of `telereddit.services.service.Service.get` method.

        Makes an API call with the client ID as authorization.
        """
        return requests.get(
            url,
            headers={"Authorization": f"Client-ID {secret.IMGUR_CLIENT_ID}"},
        )

    @classmethod
    def postprocess(cls, response):
        """
        Override of `telereddit.services.service.Service.postprocess` method.

        Creates the right media object based on the size of provider's media.
        """
        data = json.loads(response.content)["data"]
        media = None
        if "image/jpeg" in data["type"] or "image/png" in data["type"]:
            media = Media(data["link"], ContentType.PHOTO, data["size"])
        elif "video" or "image/gif" in data["type"]:
            media = Media(data["mp4"], ContentType.VIDEO, data["mp4_size"])

        return media
