"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""

import os
import importlib
import logging
from typing import Any

from telegram import InlineKeyboardMarkup, InlineKeyboardButton  # type: ignore
from pyreddit.pyreddit.config.config import load_secret

_delete_btn = InlineKeyboardButton(text="✕", callback_data="delete")
_edit_btn = InlineKeyboardButton(text="↻", callback_data="edit")
_edit_failed_btn = InlineKeyboardButton(text="Retry ↻", callback_data="edit")
_more_btn = InlineKeyboardButton(text="＋", callback_data="more")

# Dynamic environment secret configuration
load_secret("pyreddit")
secret: Any = None
_env_key = os.environ.get("TELEREDDIT_MACHINE")
if _env_key is not None:
    ENV = _env_key.lower()
    secret = importlib.import_module(
        f"telereddit.config.secret_{_env_key.lower()}"
    ).secret_config  # type: ignore
else:
    logging.warning(
        'No "TELEREDDIT_MACHINE" environment variable found. Using generic secret.'
    )
    ENV = "generic"
    secret = importlib.import_module(
        "telereddit.config.secret_generic"
    ).secret_config  # type: ignore

MAX_TRIES = 4
MAX_MEDIA_SIZE = 20000000
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
REDDIT_DOMAINS = ["reddit.com", "redd.it", "reddit.app.link"]

SENTRY_ENABLED = (
    secret.SENTRY_TOKEN is not None and len(secret.SENTRY_TOKEN) > 0
)

EDIT_KEYBOARD = InlineKeyboardMarkup([[_delete_btn, _edit_btn, _more_btn]])
EDIT_FAILED_KEYBOARD = InlineKeyboardMarkup(
    [[_delete_btn, _edit_failed_btn, _more_btn]]
)
NO_EDIT_KEYBOARD = InlineKeyboardMarkup([[_delete_btn, _more_btn]])
DELETE_KEYBOARD = InlineKeyboardMarkup([[_delete_btn]])
