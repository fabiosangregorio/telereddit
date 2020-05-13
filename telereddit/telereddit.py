#!/usr/bin/env python

"""
Entrypoint module.

Handles configuration, setup and starting of the bot, as well as receive
messages and dispatch actions to the other modules.
"""

import sentry_sdk

from telegram.ext import (
    Updater,
    CallbackContext,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
from telegram import Update
import logging

from telereddit.linker import Linker
import telereddit.helpers as helpers
import telereddit.config.config as config
from telereddit.config.config import secret


def on_chat_message(update: Update, context: CallbackContext):
    """
    Entrypoint of the bot's logic. Handles a single update message.

    Parameters
    ----------
    update : Update
        The Update object provided by python-telegram-bot
    context : CallbackContext
        The Context object provided by python-telegram-bot

    """
    msg = update.message
    if not msg or not msg.text:
        return

    linker = Linker(msg.chat_id)
    text = msg.text.lower()
    if any(r in text for r in config.REDDIT_DOMAINS):
        posts_url = helpers.get_urls_from_text(msg.text)
        for url in posts_url:
            linker.send_post_from_url(url)
    elif "r/" in text:
        subreddits = helpers.get_subreddit_names(text)
        for subreddit in subreddits:
            linker.send_random_post(subreddit)


def on_callback_query(update: Update, context: CallbackContext):
    """
    Handle all the several types of callback queries.

    (actions initiated from a keyboard).

    Parameters
    ----------
    update : Update
        The Update object provided by python-telegram-bot
    context : CallbackContext
        The Context object provided by python-telegram-bot

    """
    query_data = update.callback_query.data
    message = update.effective_message
    message_id = message.message_id
    text = (message.caption or message.text) + "\n"

    linker = Linker(message.chat_id)
    if query_data == "more":
        subreddit = helpers.get_subreddit_name(text, reverse=True)
        linker.send_random_post(subreddit)
    elif query_data == "edit":
        linker.edit_result(message)
    elif query_data == "delete":
        context.bot.deleteMessage(message.chat_id, message_id)

    context.bot.answerCallbackQuery(update.callback_query.id)


def main():
    """Entrypoint of telereddit. Handles configuration, setup and start of the bot."""
    if config.SENTRY_ENABLED:
        sentry_sdk.init(secret.SENTRY_TOKEN, environment=config.ENV)

    updater = Updater(token=secret.TELEGRAM_TOKEN, use_context=True)
    Linker.set_bot(updater.bot)

    print("Listening...")
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    dispatcher.add_handler(MessageHandler(Filters.all, on_chat_message))
    dispatcher.add_handler(CallbackQueryHandler(on_callback_query))
    updater.start_polling()
