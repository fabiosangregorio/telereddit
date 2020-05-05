import sentry_sdk as sentry
import traceback

import telereddit.config.config as config


class TeleredditError(Exception):
    """
    Base class for all catched exceptions.

    The application follows the try/catch pattern to return errors in the
    program flow between two functions.

    Parameters
    ----------
    msg : str
        Exception message to be bubbled up.

        .. note::
            In most cases this error message will be sent as a Telegram message
            to warn the user that something went wrong.

    data : dict (Default value = None)
        Extra data to be sent to Sentry if `capture` is set to True.

    capture : Boolean (Default value = False)
        Whether to send the exception to Sentry issue tracking service, if
        Sentry is configured.

    Notes
    -----
    All children exceptions have the same parameters.
    """

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
    """Raised when a service cannot authenticate to the API provider."""

    def __init__(self, data=None, capture=True):
        super().__init__("Authentication failed", data, capture)


class SubredditError(TeleredditError):
    """
    Base class for subreddit related exceptions.

    Capture
    -------
    Unless specified otherwise, these are not a true error of the application
    and originate from a "correct" subreddit property, such as it being private
    or not existing, and therfore **should not** be captured by Sentry.
    """

    def __init__(self, msg, data=None, capture=False):
        super().__init__(msg, data, capture)


class PostError(TeleredditError):
    """
    Base class for post related exceptions.

    Capture
    -------
    Unless specified otherwise, these are true errors of the application and
    **should** be captured by Sentry.
    """

    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, data, capture)


class MediaError(TeleredditError):
    """
    Base class for media related exceptions.

    Capture
    -------
    These errors cause the retrieved post not to be sent, or to be sent not as
    it should be. Therefore they represent a critical part of the application.
    For this, unless specified otherwise, they **should** be captured by Sentry.
    """

    def __init__(self, msg, data=None, capture=True):
        super().__init__(msg, data, capture)


class SubredditPrivateError(SubredditError):
    """Raised when the subreddit is private, and therefore cannot be fetched."""

    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit is private.", data, capture)


class SubredditDoesntExistError(SubredditError):
    """Raised when the subreddit does not exist."""

    def __init__(self, data=None, capture=False):
        super().__init__("This subreddit doesn't exist.", data, capture)


class PostRequestError(PostError):
    """
    Raised when there's an error in the post request.

    .. note:: Not to be confused with `PostRetrievalError`
    """

    def __init__(self, data=None, capture=True):
        super().__init__("I can't find that subreddit.", data, capture)


class PostRetrievalError(PostError):
    """
    Raised when there's an error in the post json.

    E.g. a mandatory json field is missing or the json is not strucutred as
    expected.
    """

    def __init__(self, data=None, capture=True):
        super().__init__("The retrieval of the post failed.", data, capture)


class PostSendError(PostError):
    """
    Raised when there's an error in sending the post to the Telegram chat.

    E.g. the format of the message that is being sent is not the one Telegram
    APIs expect.
    """

    def __init__(self, data=None, capture=True):
        super().__init__(
            "There has been an error in sending the post.", data, capture
        )


class PostEqualsMessageError(PostError):
    """
    Raised when the post in the Telegram message is the same as the post
    retrieved.

    Capture
    -------
    This error is useful when editing a Telegram message with a different post.
    It is thus raised as a correct program flow, and therefore it **should not** be
    captured from Sentry.
    """

    def __init__(self, data=None, capture=False):
        super().__init__(
            "The retrieved post is equal to the already sent message.",
            data,
            capture,
        )


class MediaTooBigError(MediaError):
    """
    Raised when post media exceeds the max media size allowed by Telegram APIs.

    .. seealso::
        Telegram Bot API on sending files:
        https://core.telegram.org/bots/api#sending-files
    """

    def __init__(self, data=None, capture=True):
        super().__init__("Media is too big to be sent.", data, capture)


class MediaRetrievalError(MediaError):
    """Raised when there's an error in the media retrieval request."""

    def __init__(self, data=None, capture=True):
        super().__init__("Error in getting the media", data, capture)
