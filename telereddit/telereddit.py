#!/usr/bin/env python
import sentry_sdk

from telegram.ext import Updater, CallbackContext, MessageHandler, CallbackQueryHandler, Filters
from telegram import Update
import logging
import os
import importlib

from linker import Linker
import helpers
from config import config


def on_chat_message(update: Update, context: CallbackContext):
    '''Handles a single update message.'''
    msg = update.message
    if not msg.text:
        return

    linker = Linker(msg.chat_id)

    if any(r in msg.text.lower() for r in config.REDDIT_DOMAINS):
        posts_url = helpers.get_urls_from_text(msg.text)
        for url in posts_url:
            linker.send_post_from_url(url)
    elif 'r/' in msg.text.lower():
        linker.send_random_posts(msg.text)


def on_callback_query(update: Update, context: CallbackContext):
    '''Handles all the several types of callback queries.'''
    query_id = update.callback_query.id
    query_data = update.callback_query.data
    message = update.effective_message
    message_id = message.message_id
    text = (message.caption or message.text) + '\n'

    linker = Linker(message.chat_id)
    if query_data == 'more':
        linker.send_random_posts(text, num_posts=1)
    elif query_data == 'edit':
        linker.edit_result(update)
    elif query_data == 'delete':
        context.bot.deleteMessage(message_id)

    context.bot.answerCallbackQuery(query_id)


# Dynamic environment secret configuration
env_key = os.environ.get('TELEREDDIT_MACHINE')
if env_key is not None:
    secret = importlib.import_module(f'config.secret_{env_key.lower()}').secret_config
else:
    secret = importlib.import_module('config.secret_generic').secret_config

if __name__ == "__main__":
    sentry_sdk.init(secret.SENTRY_TOKEN)

    updater = Updater(token=secret.TELEGRAM_TOKEN, use_context=True)
    Linker.set_bot(updater.bot)

    print("Listening...")
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    dispatcher.add_handler(MessageHandler(Filters.all, on_chat_message))
    dispatcher.add_handler(CallbackQueryHandler(on_callback_query))
    updater.start_polling()
