import sentry_sdk as sentry
import traceback

import telereddit.config.config as config


class TeleredditError(Exception):
    def __init__(self, msg, data=None, capture=False):
        super().__init__(msg)
        if config.SENTRY_ENABLED:
            if data is not None:
                with sentry.configure_scope() as scope:
                    for key, value in data.items():
                        scope.set_extra(key, value)
            if capture:
                sentry.capture_exception()
        traceback.print_exc()
        print(self)
        print(data)


class AuthenticationError(TeleredditError):
    def __init__(self, data=None, capture=True):
        super().__init__("Authentication failed", capture, data)


class SubredditError(TeleredditError):
    def __init__(self, msg, data=None, capture=False):
        super().__init__(msg, capture, data)


class PostError(TeleredditError):
    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, capture, data)


class MediaError(TeleredditError):
    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, capture, data)


class RequestError(TeleredditError):
    def __init__(self, data=None, capture=True):
        super().__init__("I can't find that subreddit.", capture, data)


class SubredditPrivateError(SubredditError):
    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit is private.", capture, data)


class SubredditDoesntExistError(SubredditError):
    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit doesn't exist.", capture, data)


class PostRetrievalError(PostError):
    def __init__(self, data=None, capture=True):
        super().__init__("The retrieval of the post failed.", capture, data)


class PostSendError(PostError):
    def __init__(self, data=None, capture=True):
        super().__init__("There has been an error in sending the post.", capture, data)


class MediaTooBigError(MediaError):
    def __init__(self, data=None, capture=True):
        super().__init__("Media is too big to be sent.", capture, data)


class MediaRetrievalError(MediaError):
    def __init__(self, data=None, capture=True):
        super().__init__("Error in getting the media", capture, data)
