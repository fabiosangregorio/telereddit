"""Service for Gfycat GIFs."""
import json

import requests
from urllib.parse import urlparse

from telereddit.config.config import secret
from requests import Response
import icontract

from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType
from telereddit.exceptions import AuthenticationError
from typing import Any


@icontract.invariant(
    lambda self: self.is_authenticated is True and self.access_token is not None
)
class Gfycat(Service):
    """
    Service for Gfycat GIFs.

    Notes
    -----
    This is an authenticated OAuth service.

    """

    is_authenticated: bool = True

    def __init__(self):
        Gfycat.authenticate()

    @classmethod
    def preprocess(cls, url: str, json: Any) -> str:
        """
        Override of `telereddit.services.service.Service.preprocess` method.

        Extracts the gfycat Id from the url and constructs the provider url.
        """
        gfyid: str = urlparse(url).path.partition("-")[0]
        return f"https://api.gfycat.com/v1/gfycats/{gfyid}"

    @classmethod
    def get(cls, url: str) -> Response:
        """
        Override of `telereddit.services.service.Service.get` method.

        Makes a call to the provider's API.
        """
        return requests.get(
            url, headers={"Authorization": f"Bearer {cls.access_token}"}
        )

    @classmethod
    def postprocess(cls, response: Response) -> Media:
        """
        Override of `telereddit.services.service.Service.postprocess` method.

        Returns the media url which respects the Telegram API file limits, if
        present.
        """
        gfy_item: Any = json.loads(response.content)["gfyItem"]
        media: Media = Media(
            gfy_item["webmUrl"].replace(".webm", ".mp4"),
            ContentType.VIDEO,
            gfy_item["webmSize"],
        )
        # Telegram does not support webm
        # See: https://www.reddit.com/r/Telegram/comments/5wcqh8/sending_webms_as_videos/
        if media.size > 20000000:
            media.url = gfy_item["max5mbGif"]
            media.type = ContentType.GIF
            media.size = 5000000
        return media

    @classmethod
    @icontract.snapshot(lambda cls: cls.access_token, name="access_token")
    @icontract.ensure(lambda OLD, cls: cls.access_token != OLD.access_token)
    def authenticate(cls) -> None:
        """
        Override of `telereddit.services.service.Service.authenticate` method.

        Authenticates the service through OAuth.
        """
        response: Response = requests.post(
            "https://api.gfycat.com/v1/oauth/token",
            data=json.dumps(
                {
                    "grant_type": "client_credentials",
                    "client_id": secret.GFYCAT_CLIENT_ID,
                    "client_secret": secret.GFYCAT_CLIENT_SECRET,
                }
            ),
        )
        if response.status_code >= 300:
            raise AuthenticationError(
                {
                    "response_text": response.text,
                    # "client_id": secret.GFYCAT_CLIENT_ID,
                    # "client_secret": secret.GFYCAT_CLIENT_SECRET,
                }
            )

        cls.access_token = json.loads(response.content)["access_token"]
