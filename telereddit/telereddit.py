#!/usr/bin/env python
import sentry_sdk

from telegram.ext import Updater, CallbackContext, MessageHandler, CallbackQueryHandler, Filters
from telegram import Update
import logging

from secret import TELEGRAM_TOKEN, SENTRY_TOKEN

import reddit_linker
import helpers


def on_chat_message(update: Update, context: CallbackContext):
    '''Handles a single update message.'''
    msg = update.message
    if not msg.text:
        return

    if any(r in msg.text.lower() for r in ['reddit.com', 'redd.it', 'reddit.app.link']):
        posts_url = helpers.get_urls_from_text(msg.text)
        for url in posts_url:
            reddit_linker.send_post_from_url(context.bot, msg.chat_id, url)
    elif 'r/' in msg.text.lower():
        reddit_linker.send_random_posts(context.bot, msg.chat_id, msg.text)


def on_callback_query(update: Update, context: CallbackContext):
    '''Handles all the several types of callback queries.'''
    query_id = update.callback_query.id
    query_data = update.callback_query.data
    message = update.effective_message
    chat_id = message.chat_id
    message_id = message.message_id
    text = (message.caption or message.text) + '\n'

    if query_data == 'more':
        reddit_linker.send_random_posts(context.bot, chat_id, text)
    elif query_data == 'edit':
        reddit_linker.edit_result(context.bot, update)
    elif query_data == 'delete':
        context.bot.deleteMessage(chat_id, message_id)

    context.bot.answerCallbackQuery(query_id)


if __name__ == "__main__":
    sentry_sdk.init(SENTRY_TOKEN)

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    print("Listening...")
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    dispatcher.add_handler(MessageHandler(Filters.all, on_chat_message))
    dispatcher.add_handler(CallbackQueryHandler(on_callback_query))
    updater.start_polling()
