"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""


from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # type: ignore

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
