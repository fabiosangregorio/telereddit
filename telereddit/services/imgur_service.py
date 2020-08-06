"""Service for Imgur images and videos."""
import json
from urllib.parse import urlparse
import requests
import re
from typing import Any
from requests import Response

from telereddit.config.config import secret
from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType


class Imgur(Service):
    """Service for Imgur images and videos."""

    @classmethod
    def preprocess(cls, url: str, json: Any) -> str:
        """
        Override of `telereddit.services.service.Service.preprocess` method.

        Gets the media hash from the url and creates the accepted provider media
        url.
        """
        media_hash: str = urlparse(url).path.rpartition("/")[2]
        r = re.compile(r"image|gallery").search(url)
        api: str = r.group() if r else "image"
        if "." in media_hash:
            media_hash = media_hash.rpartition(".")[0]
        return f"https://api.imgur.com/3/{api}/{media_hash}"

    @classmethod
    def get(cls, url: str) -> Response:
        """
        Override of `telereddit.services.service.Service.get` method.

        Makes an API call with the client ID as authorization.
        """
        return requests.get(
            url,
            headers={"Authorization": f"Client-ID {secret.IMGUR_CLIENT_ID}"},
        )

    @classmethod
    def postprocess(cls, response: Response) -> Media:
        """
        Override of `telereddit.services.service.Service.postprocess` method.

        Creates the right media object based on the size of provider's media.
        """
        data: Any = json.loads(response.content)["data"]
        media: Media
        if "images" in data:
            data = data["images"][0]
        if "image/jpeg" in data["type"] or "image/png" in data["type"]:
            media = Media(data["link"], ContentType.PHOTO, data["size"])
        elif "video" or "image/gif" in data["type"]:
            media = Media(data["mp4"], ContentType.VIDEO, data["mp4_size"])

        return media
