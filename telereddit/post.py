from content_type import ContentType


class Post():
    def __init__(self, subreddit, title, text, footer, media=None):
        self.subreddit = subreddit
        self.title = title
        self.text = text
        self.footer = footer
        self.media = media

    def get_msg(self):
        return f" *{self.title}*\n{self.text}\n\n{self.footer}"

    def get_type(self):
        return self.media.type if self.media else ContentType.TEXT
