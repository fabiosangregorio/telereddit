from telereddit.models.content_type import ContentType


class Post:
    """ """

    def __init__(self, subreddit, permalink, title, text, media=None):
        self.subreddit = subreddit
        self.permalink = permalink
        self.title = title
        self.text = text
        self.media = media

    def get_msg(self):
        """ """
        subreddit_url = f"https://www.reddit.com/{self.subreddit}"
        footer = (
            f"[Link to post](https://reddit.com{self.permalink}) | "
            f"[{self.subreddit}]({subreddit_url})"
        )
        return f" *{self.title}*\n{self.text}\n\n{footer}"

    def get_type(self):
        """ """
        return self.media.type if self.media else ContentType.TEXT
