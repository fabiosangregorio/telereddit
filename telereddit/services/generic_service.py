from telereddit.services.service import Service
from telereddit.models.media import Media
from telereddit.content_type import ContentType


class Generic(Service):
    """ """
    @classmethod
    def postprocess(cls, response):
        """

        Parameters
        ----------
        response :
            

        Returns
        -------

        
        """
        file_size = None
        media_type = ContentType.PHOTO

        if ".gif" in response.url:
            media_type = ContentType.GIF
        elif ".mp4" in response.url:
            media_type = ContentType.VIDEO

        if "Content-length" in response.headers:
            file_size = int(response.headers["Content-length"])

        return Media(response.url, media_type, file_size)
