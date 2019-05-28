from telegram import InlineKeyboardMarkup, InlineKeyboardButton


MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
MAX_TRIES = 4
EDIT_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="✕", callback_data="delete"),
    InlineKeyboardButton(text="↻", callback_data="edit"),
    InlineKeyboardButton(text="✓", callback_data="confirm")
]])
EDIT_FAILED_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="✕", callback_data="delete"),
    InlineKeyboardButton(text="Retry ↻", callback_data="edit"),
    InlineKeyboardButton(text="✓", callback_data="confirm")
]])
CONFIRMED_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Show another one", callback_data="more")
]])
