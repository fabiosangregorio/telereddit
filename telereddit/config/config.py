from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def _edit_keyboard(edit_text):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(text="✕", callback_data="delete"),
        InlineKeyboardButton(text=edit_text, callback_data="edit"),
        InlineKeyboardButton(text="＋", callback_data="more")
    ]])


MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
MAX_TRIES = 4

EDIT_KEYBOARD = _edit_keyboard('↻')
EDIT_FAILED_KEYBOARD = _edit_keyboard('Retry ↻')
NO_EDIT_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="✕", callback_data="delete"),
    InlineKeyboardButton(text="＋", callback_data="more")
]])
