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
        print("\nException type:", self.__class__.__name__)
        print("Exception message: ", self)
        print("Exception data: ", data)


class AuthenticationError(TeleredditError):
    def __init__(self, data=None, capture=True):
        super().__init__("Authentication failed", data, capture)


class SubredditError(TeleredditError):
    def __init__(self, msg, data=None, capture=False):
        super().__init__(msg, data, capture)


class PostError(TeleredditError):
    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, data, capture)


class MediaError(TeleredditError):
    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, data, capture)


class RequestError(TeleredditError):
    def __init__(self, data=None, capture=True):
        super().__init__("I can't find that subreddit.", data, capture)


class SubredditPrivateError(SubredditError):
    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit is private.", data, capture)


class SubredditDoesntExistError(SubredditError):
    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit doesn't exist.", data, capture)


class PostRetrievalError(PostError):
    def __init__(self, data=None, capture=True):
        super().__init__("The retrieval of the post failed.", data, capture)


class PostSendError(PostError):
    def __init__(self, data=None, capture=True):
        super().__init__("There has been an error in sending the post.", data, capture)


class PostEqualsMessageError(PostError):
    def __init__(self, data=None, capture=False):
        super().__init__(
            "The retrieved post is equal to the already sent message.", data, capture
        )


class MediaTooBigError(MediaError):
    def __init__(self, data=None, capture=True):
        super().__init__("Media is too big to be sent.", data, capture)


class MediaRetrievalError(MediaError):
    def __init__(self, data=None, capture=True):
        super().__init__("Error in getting the media", data, capture)
