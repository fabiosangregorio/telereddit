from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import os
import importlib

# Dynamic environment secret configuration
env_key = os.environ.get('TELEREDDIT_MACHINE')
if env_key is not None:
    secret = importlib.import_module(f'telereddit.config.secret_{env_key.lower()}').secret_config
else:
    secret = importlib.import_module('telereddit.config.secret_generic').secret_config


def _edit_keyboard(edit_text):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(text="✕", callback_data="delete"),
        InlineKeyboardButton(text=edit_text, callback_data="edit"),
        InlineKeyboardButton(text="＋", callback_data="more")
    ]])


REDDIT_DOMAINS = ['reddit.com', 'redd.it', 'reddit.app.link']
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
MAX_TRIES = 4

EDIT_KEYBOARD = _edit_keyboard('↻')
EDIT_FAILED_KEYBOARD = _edit_keyboard('Retry ↻')
NO_EDIT_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="✕", callback_data="delete"),
    InlineKeyboardButton(text="＋", callback_data="more")
]])
