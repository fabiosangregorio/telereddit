import traceback

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from sentry_sdk import capture_exception

from config import MAX_POST_LENGTH, MAX_TRIES

import reddit
import helpers


def send_random_posts(bot, chat_id, text):
    # searches in text for subreddit names and sends a random post from the subreddit
    subreddits = helpers.get_subreddit_names(text)
    for subreddit in subreddits:
        tries = 0
        while tries < MAX_TRIES:
            status, err_msg = send_post(bot, chat_id, subreddit)
            if status == 'success':
                break
            if status == 'retry':
                tries += 1
        if status != 'success':
            _send_exception_message(bot, chat_id, err_msg)


def send_post_from_url(bot, chat_id, post_url):
    status, err_msg = send_post(bot, chat_id, post_url=post_url)
    if status != 'success':
        _send_exception_message(bot, chat_id, err_msg)


def send_post(bot, chat_id, subreddit=None, post_url=None):
    post, status, err_msg = reddit.get_post(subreddit, post_url)
    if status == 'not_found':
        bot.sendMessage(chat_id, err_msg)
    elif status != 'success':
        return status, err_msg

    try:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="↻", callback_data="edit"),
            InlineKeyboardButton(text="✓", callback_data="send")
        ]])
        if 'www.youtube.com' in post.media_url:
            bot.sendMessage(chat_id, f"I'm sorry, youtube videos are not"
                            "supported yet :(", parse_mode='Markdown')
            return 'success', None

        # check if the post is a text post
        if '/comments/' in post.content_url:
            post_text = helpers.escape_markdown(
                post.text[:MAX_POST_LENGTH] +
                (post.text[MAX_POST_LENGTH:] and '...'))
            post_text = post_text + '\n\n' if post_text else ''
            post_msg = f"{post.title}{post_text}\n\n{post.footer}"
            bot.sendMessage(chat_id, text=post_msg,
                            parse_mode='Markdown', reply_markup=keyboard,
                            disable_web_page_preview=True)
        elif post.media_type == 'gif':
            bot.sendDocument(chat_id, post.media_url, caption=post.msg,
                             parse_mode='Markdown', reply_markup=keyboard,
                             disable_web_page_preview=True)
        elif post.media_type == 'video':
            bot.sendVideo(chat_id, post.media_url, caption=post.msg,
                          parse_mode='Markdown', reply_markup=keyboard,
                          disable_web_page_preview=True)
        else:
            bot.sendPhoto(chat_id, post.media_url, caption=post.msg,
                          parse_mode='Markdown', reply_markup=keyboard,
                          disable_web_page_preview=True)

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return 'retry', f"I'm sorry, an error occurred in sending the post from "\
            f"{post.subreddit} :(\nThe developer must have missed an if statement!"

    return 'success', None


def _send_exception_message(bot, chat_id, msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Try with another random post', callback_data='more')]
    ])
    bot.sendMessage(chat_id, msg, 'Markdown', reply_markup=keyboard)
