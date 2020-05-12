"""Module for Post class."""

from telereddit.models.content_type import ContentType


class Post:
    """Represents a Reddit post."""

    def __init__(self, subreddit, permalink, title, text, media=None):
        """
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
        self.subreddit = subreddit
        self.permalink = permalink
        self.title = title
        self.text = text
        self.media = media

    def get_msg(self):
        """
        Gets the full message of the post. This includes post title, description
        and footer. The footer consists of a link to the subreddit and a link to
        the post.
        """
        subreddit_url = f"https://www.reddit.com/{self.subreddit}"
        footer = (
            f"[Link to post](https://reddit.com{self.permalink}) | "
            f"[{self.subreddit}]({subreddit_url})"
        )
        return f" *{self.title}*\n{self.text}\n\n{footer}"

    def get_type(self):
        """
        Returns the post type: this is determined by the media type, if present.
        """
        return self.media.type if self.media else ContentType.TEXT
