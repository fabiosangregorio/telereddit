from enum import Enum


class ContentType(Enum):
    """ """
    TEXT, PHOTO, VIDEO, GIF, YOUTUBE, *_ = range(20)
