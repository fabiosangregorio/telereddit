class TeleredditError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class SubredditError(TeleredditError):
    def __init__(self, msg):
        super().__init__(msg)


class PostError(TeleredditError):
    def __init__(self, msg):
        super().__init__(msg)


class RequestError(TeleredditError):
    def __init__(self):
        super().__init__("I'm sorry, I can't find that subreddit.")


class SubredditPrivateError(SubredditError):
    def __init__(self):
        super().__init__("I'm sorry, this subreddit is private.")


class SubredditDoesntExistError(SubredditError):
    def __init__(self):
        super().__init__("I'm sorry, this subreddit doesn't exist.")


class PostRetrievalError(PostError):
    def __init__(self):
        super().__init__("I'm sorry, the retrieval of the post failed.")


class PostSendError(PostError):
    def __init__(self):
        super().__init__("I'm sorry, there has been an error in sending the post.")


class MediaTooBigError(PostError):
    def __init__(self):
        super().__init__("I'm sorry, media is too big to be sent.")
