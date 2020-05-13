"""Service for v.redd.it GIFs."""
import requests

from telereddit.services.service import Service
import telereddit.helpers as helpers
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType


class Vreddit(Service):
    """Service for v.redd.it GIFs."""

    @classmethod
    def preprocess(cls, url, json):
        """
        Override of `telereddit.services.service.Service.preprocess` method.

        Tries to get the right media url from the reddit json.

        Reddit APIs are known to be unreliable in positioning the information
        needed, therefore we need to seach in the json for the correct piece of
        information in every specific case.
        """
        xpost = helpers.get(json, "crosspost_parent_list")
        if xpost is not None and len(xpost) > 0:
            # crossposts have media = null and have the fallback url in the
            # crosspost source
            fallback_url = helpers.chained_get(
                xpost[0], ["secure_media", "reddit_video", "fallback_url"]
            )
        else:
            fallback_url = helpers.chained_get(
                json, ["media", "reddit_video", "fallback_url"]
            )

        processed_url = fallback_url if fallback_url else f"{url}/DASH_1_2_M"
        if requests.head(processed_url).status_code >= 300:
            processed_url = f"{url}/DASH_1080"
        return processed_url

    @classmethod
    def postprocess(cls, response):
        """
        Override of `telereddit.services.service.Service.postprocess` method.

        Constructs the media object.
        """
        media = Media(response.url, ContentType.GIF)
        if "Content-length" in response.headers:
            media.size = int(response.headers["Content-length"])
        return media
