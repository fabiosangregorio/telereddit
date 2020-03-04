from enum import Enum


class MediaType(Enum):
    PHOTO, VIDEO, GIF, YOUTUBE, *_ = range(20)


class Media:
    def __init__(self, url, media_type: MediaType, size=None):
        self.url = url
        self.type = media_type
        self.size = size
