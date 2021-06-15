#!/usr/bin/env python

"""
Entrypoint module.

Handles configuration, setup and starting of the bot, as well as receive
messages and dispatch actions to the other modules.
"""

import logging
import os
from typing import List

import sentry_sdk
from dotenv import load_dotenv
from pyreddit.pyreddit import helpers
from pyreddit.pyreddit.services.services_wrapper import ServicesWrapper
from telegram import Message, Update  # type: ignore
from telegram.ext import CallbackContext  # type: ignore
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler, Updater

import telereddit.config.config as config
from telereddit.linker import Linker


def on_chat_message(update: Update, context: CallbackContext) -> None:
    """
    Entrypoint of the bot's logic. Handles a single update message.

    Parameters
    ----------
    update : Update
        The Update object provided by python-telegram-bot
    context : CallbackContext
        The Context object provided by python-telegram-bot

    """
    msg: Message = update.message
    if not msg or not msg.text:
        return

    linker: Linker = Linker(msg.chat_id)
    text: str = msg.text.lower()
    if any(r in text for r in config.REDDIT_DOMAINS):
        posts_url: List[str] = helpers.get_urls_from_text(msg.text)
        for url in posts_url:
            linker.send_post_from_url(url)
    elif "r/" in text:
        subreddits: List[str] = helpers.get_subreddit_names(text)
        for subreddit in subreddits:
            linker.send_random_post(subreddit)


def on_callback_query(update: Update, context: CallbackContext) -> None:
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
    text = (message.caption or message.text) + "\n"

    linker = Linker(message.chat_id)
    if query_data == "more":
        subreddit = helpers.get_subreddit_name(text, reverse=True)
        if subreddit:
            linker.send_random_post(subreddit)
    elif query_data == "edit":
        linker.edit_result(message)
    elif query_data == "delete":
        linker.delete_message(message)

    context.bot.answerCallbackQuery(update.callback_query.id)


def init() -> str:
    """Init environment variables and services."""
    env = os.getenv("REDDIT_BOTS_MACHINE")
    if env is None or len(env) == 0:
        raise Exception("No REDDIT_BOTS_MACHINE env variable found.")

    load_dotenv(
        dotenv_path=os.path.join(
            os.path.dirname(__file__), f"config/{env.lower()}.env"
        )
    )

    ServicesWrapper.init_services()
    return env


def main() -> None:
    """Entrypoint of telereddit. Handles configuration, setup and start of the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    env = init()
    if os.getenv("SENTRY_TOKEN"):
        sentry_sdk.init(os.getenv("SENTRY_TOKEN"), environment=env)

    updater = Updater(token=os.getenv("TELEGRAM_TOKEN"), use_context=True)
    Linker.set_bot(updater.bot)

    print("Listening...")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.all, on_chat_message))
    dispatcher.add_handler(CallbackQueryHandler(on_callback_query))
    updater.start_webhook(
        listen="0.0.0.0", port=5000, url_path=os.getenv("TELEGRAM_TOKEN")
    )
    updater.bot.setWebhook(
        "https://telereddit.herokuapp.com/" + os.getenv("TELEGRAM_TOKEN")
    )
    updater.idle()
