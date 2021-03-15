"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""


from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # type: ignore


MAX_TRIES = 4
MAX_MEDIA_SIZE = 20000000
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
REDDIT_DOMAINS = ["reddit.com", "redd.it", "reddit.app.link"]


DELETE_BTN = {"text": "✕", "callback": "delete"}
EDIT_BTN = {"text": "↻", "callback": "edit"}
EDIT_FAILED_BTN = {"text": "Retry ↻", "callback": "edit"}
MORE_BTN = {"text": "＋", "callback": "more"}

EDIT_LAYOUT = [[DELETE_BTN, EDIT_BTN, MORE_BTN]]
EDIT_FAILED_LAYOUT = [[DELETE_BTN, EDIT_FAILED_BTN, MORE_BTN]]
NO_EDIT_LAYOUT = [[DELETE_BTN, MORE_BTN]]
DELETE_LAYOUT = [[DELETE_BTN]]


def get_keyboard(layout: str, message_id=None):
    rows_list = []
    for row in layout:
        cols_list = []
        for btn in row:
            if message_id is not None:
                callback = f"{btn['callback']}@{message_id}"
            else:
                callback = btn["callback"]
            cols_list.append(
                InlineKeyboardButton(text=btn["text"], callback_data=callback)
            )
        rows_list.append(cols_list)
    return InlineKeyboardMarkup(rows_list)
