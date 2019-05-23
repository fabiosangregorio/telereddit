#!/usr/bin/env python
import time
import telepot
import sentry_sdk

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from secret import TELEGRAM_TOKEN, SENTRY_TOKEN
import reddit_linker
import helpers


# handle chat messages
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        return

    text = msg['text']
    if any(r in text.lower() for r in ['reddit.com', 'redd.it']):
        posts_url = helpers.get_urls_from_text(text)
        for url in posts_url:
            reddit_linker.send_post_from_url(bot, chat_id, url)
    elif 'r/' in text.lower():
        reddit_linker.send_random_posts(bot, chat_id, text)


# handle inline keyboard
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query', long=True)
    if query_data == 'more':
        # upon clicking the "more" button, send another random reddit post
        message = msg['message']
        chat_id = message['chat']['id']
        text = message.get('caption', message.get('text')) + '\n'
        subreddit = helpers.get_subreddit_names(text)
        if len(subreddit):
            subreddit = subreddit[0]
        reddit_linker.send_random_posts(bot, chat_id, subreddit)
    elif query_data == 'send':
        message_id = msg['message']['message_id']
        chat_id = msg['message']['chat']['id']
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Show another one", callback_data="more")
        ]])
        bot.editMessageReplyMarkup((chat_id, message_id), keyboard)
    # elif query_data == 'edit':

    bot.answerCallbackQuery(query_id)


sentry_sdk.init(SENTRY_TOKEN)
bot = telepot.Bot(TELEGRAM_TOKEN)

if __name__ == "__main__":
    bot.message_loop({
        'chat': on_chat_message,
        'callback_query': on_callback_query})

    # Keep the program running
    while 1:
        time.sleep(3)
