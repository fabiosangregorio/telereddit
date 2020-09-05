"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""

import os
import importlib
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton  # type: ignore

_delete_btn = InlineKeyboardButton(text="✕", callback_data="delete")
_edit_btn = InlineKeyboardButton(text="↻", callback_data="edit")
_edit_failed_btn = InlineKeyboardButton(text="Retry ↻", callback_data="edit")
_more_btn = InlineKeyboardButton(text="＋", callback_data="more")

MAX_TRIES = 4
MAX_MEDIA_SIZE = 20000000
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
REDDIT_DOMAINS = ["reddit.com", "redd.it", "reddit.app.link"]

EDIT_KEYBOARD = InlineKeyboardMarkup([[_delete_btn, _edit_btn, _more_btn]])
EDIT_FAILED_KEYBOARD = InlineKeyboardMarkup(
    [[_delete_btn, _edit_failed_btn, _more_btn]]
)
NO_EDIT_KEYBOARD = InlineKeyboardMarkup([[_delete_btn, _more_btn]])
DELETE_KEYBOARD = InlineKeyboardMarkup([[_delete_btn]])


# Dynamic environment secret configuration
def load_secret() -> None:
    global secret, ENV, SENTRY_ENABLED
    _env_key = os.environ.get("REDDIT_BOTS_MACHINE")
    if _env_key is not None:
        ENV = _env_key.lower()
    else:
        logging.warning(
            'No "REDDIT_BOTS_MACHINE" environment variable found. Using generic secret.'
        )
        ENV = "generic"

    secret = importlib.import_module(
        f"telereddit.config.secret_{ENV}"
    ).secret_config  # type: ignore
    SENTRY_ENABLED = (
        secret.SENTRY_TOKEN is not None and len(secret.SENTRY_TOKEN) > 0
    )


SENTRY_ENABLED: bool = False
ENV: str = None
secret = None