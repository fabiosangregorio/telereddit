from telereddit.content_type import ContentType


class Media:
    """ """
    def __init__(self, url, media_type: ContentType, size=None):
        self.url = url
        self.type = media_type
        self.size = size
