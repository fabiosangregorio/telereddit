#!/usr/bin/env python
import sentry_sdk

from telegram.ext import Updater, CallbackContext, MessageHandler, CallbackQueryHandler, Filters
from telegram import Update
import logging

from linker import Linker
import helpers
import config.config as config


def on_chat_message(update: Update, context: CallbackContext):
    '''Handles a single update message.'''
    msg = update.message
    if not msg.text:
        return

    linker = Linker(msg.chat_id)
    text = msg.text.lower()
    if any(r in text for r in config.REDDIT_DOMAINS):
        posts_url = helpers.get_urls_from_text(msg.text)
        for url in posts_url:
            linker.send_post_from_url(url)
    elif 'r/' in text:
        subreddits = helpers.get_subreddit_names(text)
        for subreddit in subreddits:
            linker.send_random_post(subreddit)


def on_callback_query(update: Update, context: CallbackContext):
    '''Handles all the several types of callback queries.'''
    query_data = update.callback_query.data
    message = update.effective_message
    message_id = message.message_id
    text = (message.caption or message.text) + '\n'

    linker = Linker(message.chat_id)
    if query_data == 'more':
        subreddit = helpers.get_subreddit_name(text, reverse=True)
        linker.send_random_post(subreddit)
    elif query_data == 'edit':
        linker.edit_result(message)
    elif query_data == 'delete':
        context.bot.deleteMessage(message.chat_id, message_id)

    context.bot.answerCallbackQuery(update.callback_query.id)


if __name__ == "__main__":
    sentry_sdk.init(config.secret.SENTRY_TOKEN)

    updater = Updater(token=config.secret.TELEGRAM_TOKEN, use_context=True)
    Linker.set_bot(updater.bot)

    print("Listening...")
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    dispatcher.add_handler(MessageHandler(Filters.all, on_chat_message))
    dispatcher.add_handler(CallbackQueryHandler(on_callback_query))
    updater.start_polling()
