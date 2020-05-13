"""Module for ContentType class."""

from enum import Enum


class ContentType(Enum):
    """Enumerable to represent different `telereddit.models.post.Post` types."""

    TEXT, PHOTO, VIDEO, GIF, YOUTUBE, *_ = range(20)
