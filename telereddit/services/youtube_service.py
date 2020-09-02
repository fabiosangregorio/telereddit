"""Service for Youtube URLs."""
from typing import Optional, Any

from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType
import telereddit.helpers as helpers


class Youtube(Service):
    """
    Service for Youtube URLs.

    Notes
    -----
    This service creates a `YOUTUBE` media, which will in the end create a text
    post.

    """

    access_token: Optional[str] = None
    is_authenticated: bool = False
    has_external_request: bool = False

    @classmethod
    def preprocess(cls, url: str, data: Any) -> str:
        """
        Override of `telereddit.services.service.Service.preprocess` method.

        Gets the youtube url from reddit json.
        """
        oembed_url: str = helpers.chained_get(data, ["media", "oembed", "url"])
        return oembed_url if oembed_url else url

    @classmethod
    def get(cls, url: str) -> str:
        """
        Override of `telereddit.services.service.Service.get` method.

        Fake get: simply returns the url given as parameter.
        """
        return url

    @classmethod
    def postprocess(cls, response) -> Media:
        """
        Override of `telereddit.services.service.Service.postprocess` method.

        Constructs the media object.
        """
        return Media(response, ContentType.YOUTUBE)
