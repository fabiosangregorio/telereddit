"""
Catched exceptions of the software.

The application follows the try/catch pattern to return errors in the program
flow between two functions.
"""

import logging
import os
import traceback
from typing import Any

import sentry_sdk as sentry


class TeleredditError(Exception):
    """
    Base class for all catched exceptions.

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

    def __init__(self, msg: Any, data: Any = None, capture: bool = False):
        super().__init__(msg)
        if (
            os.getenv("SENTRY_TOKEN") is not None
            and len(os.getenv("SENTRY_TOKEN")) > 0  # type: ignore
        ):
            if data is not None:
                with sentry.configure_scope() as scope:
                    for key, value in data.items():
                        scope.set_extra(key, value)
            if capture:
                sentry.capture_exception()
        traceback.print_exc()
        logging.exception(
            "\nEXCEPTION: %s, MESSAGE: %s, DATA: %s",
            self.__class__.__name__,
            self,
            data,
        )


class PostError(TeleredditError):
    """
    Base class for post related exceptions.

    Capture
    -------
    Unless specified otherwise, these are true errors of the application and
    **should** be captured by Sentry.
    """

    def __init__(self, msg: Any, data: Any = None, capture: bool = True):
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

    def __init__(self, msg: Any, data: Any = None, capture: bool = True):
        super().__init__(msg, data, capture)


class PostSendError(PostError):
    """
    Raised when there's an error in sending the post to the Telegram chat.

    E.g. the format of the message that is being sent is not the one Telegram
    APIs expect.
    """

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__(
            "There has been an error in sending the post.", data, capture
        )


class PostEqualsMessageError(PostError):
    """
    Raised when the post in the Telegram message is the same as the retrieved.

    Capture
    -------
    This error is useful when editing a Telegram message with a different post.
    It is thus raised as a correct program flow, and therefore it **should not**
    be captured from Sentry.
    """

    def __init__(self, data: Any = None, capture: bool = False):
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

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__("Media is too big to be sent.", data, capture)
