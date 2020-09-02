"""Module for Post class."""

from typing import Optional

from telereddit.models.content_type import ContentType
from telereddit.helpers import escape_markdown
from telereddit.models.media import Media


class Post:
    """
    Represents a Reddit post.

    Parameters
    ----------
    subreddit : str
        Subreddit within which the post was created (or crossposted).
    permalink : str
        Reddit permalink of the post.
    title : str
        Title of the post.
    text : str
        Description of the post.
    media : `telereddit.models.media.Media`
        (Default value = None)

        Media associated with the post (if present), None otherwise. This
        determines the post type.

    """

    def __init__(
        self,
        subreddit: str,
        permalink: str,
        title: str,
        text: str,
        media: Optional[Media] = None,
    ):

        self.subreddit = subreddit
        self.permalink = permalink
        self.title = title
        self.text = text
        self.media = media

    def get_msg(self) -> str:
        """
        Get the full message of the post.

        This includes post title, description and footer. The footer consists of
        a link to the subreddit and a link to the post.
        """
        subreddit_url = f"https://www.reddit.com/{self.subreddit}"
        footer = (
            f"[Link to post](https://reddit.com{self.permalink}) \\| "
            f"[{escape_markdown(self.subreddit)}]({subreddit_url})"
        )
        return (
            f"*{escape_markdown(self.title)}*"
            f"\n{escape_markdown(self.text)}"
            f"\n\n{footer}"
        )

    def get_type(self) -> ContentType:
        """Return the post type: this is determined by the media type, if present."""
        return self.media.type if self.media else ContentType.TEXT
