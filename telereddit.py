#!/usr/bin/env python
import time
import telepot
import sentry_sdk

from secret import TELEGRAM_TOKEN, SENTRY_TOKEN
import reddit_linker


# handle chat messages
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        return

    text = msg['text']
    if 'www.reddit.com' in text.lower():
        post_url = [word for word in text.lower().split(' ') 
                    if 'www.reddit.com' in word][0]
        post_url = post_url.partition('/?')[0] + '.json'
        reddit_linker.send_post(bot, chat_id, post_url=post_url)
    elif 'r/' in text.lower():
        reddit_linker.send_random_posts(bot, chat_id, text)


# handle inline keyboard
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if query_data == 'reddit':
        reddit_linker.more_button_callback(bot, msg)
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
