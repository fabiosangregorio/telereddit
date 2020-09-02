"""Module for Media class."""

from typing import Optional
from telereddit.models.content_type import ContentType


class Media:
    """
    Represents a media content in the application.

    This can be any of `telereddit.models.content_type.ContentType`: photo,
    video, gif, etc.

    Parameters
    ----------
    url : str
        URL of the media on the internet. This will be used by
        Telegram to send the media to the chat.

    media_type : `telereddit.models.content_type.ContentType`
        Content type of the media. This is used in
        `telereddit.linker.Linker` to determine what type of message to send
        to the chat.

    size : int
        Size (in bytes) of the media content. This can be none if it
        is unkwnown, but it is crucial because of Telegram file size
        limitations.

    """

    def __init__(
        self, url: str, media_type: ContentType, size: Optional[int] = None
    ):
        self.url = url
        self.type = media_type
        self.size = size
