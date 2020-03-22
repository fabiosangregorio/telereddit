import traceback

from telegram import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from sentry_sdk import capture_exception
from config.config import MAX_TRIES, EDIT_KEYBOARD, EDIT_FAILED_KEYBOARD, NO_EDIT_KEYBOARD

import reddit
import helpers

from media import ContentType


def send_random_posts(bot, chat_id, text, num_posts=None):
    '''
    Searches the text for subreddit names and sends a random post from that
    subreddit.
    '''
    subreddits = helpers.get_subreddit_names(text)
    subreddits = subreddits[0:num_posts]
    for subreddit in subreddits:
        for _ in range(MAX_TRIES):
            status, err_msg = send_post(bot, chat_id, subreddit)
            if status == 'success':
                break
        if status != 'success':
            _send_exception_message(bot, chat_id, err_msg)


def send_post_from_url(bot, chat_id, post_url):
    '''Sends the post from the given url.'''
    status, err_msg = send_post(bot, chat_id, post_url=post_url)
    if status != 'success':
        _send_exception_message(bot, chat_id, err_msg, keyboard=False)


def send_post(bot, chat_id, subreddit=None, post_url=None):
    '''
    Sends a random post from the given subreddit if not None, sends the post
    from post_url otherwise.
    '''
    post, status, err_msg = reddit.get_post(subreddit, post_url)
    if status == 'not_found':
        bot.sendMessage(chat_id, err_msg)
        return 'success', None
    elif status != 'success':
        return status, err_msg

    if post.media and post.media.size and post.media.size > 20000000:
        return 'failed', "I'm sorry, media is too big to be sent."

    try:
        # if it is not a random post (e.g. shared via link) don't show the
        # edit custom keyboard
        keyboard = NO_EDIT_KEYBOARD if post_url else EDIT_KEYBOARD

        if post.get_type() == ContentType.TEXT:
            # check if the post is a text post
            bot.sendMessage(chat_id, text=post.get_msg(),
                            parse_mode='Markdown', reply_markup=keyboard,
                            disable_web_page_preview=True)
        elif post.get_type() == ContentType.YOUTUBE:
            bot.sendMessage(chat_id, text=post.get_msg(),
                            parse_mode='Markdown', reply_markup=keyboard)
            return 'success', None
        elif post.get_type() == ContentType.GIF:
            bot.sendDocument(chat_id, post.media.url, caption=post.get_msg(),
                             parse_mode='Markdown', reply_markup=keyboard,
                             disable_web_page_preview=True)
        elif post.get_type() == ContentType.VIDEO:
            bot.sendVideo(chat_id, post.media.url, caption=post.get_msg(),
                          parse_mode='Markdown', reply_markup=keyboard,
                          disable_web_page_preview=True)
        elif post.get_type() == ContentType.PHOTO:
            bot.sendPhoto(chat_id, post.media.url, caption=post.get_msg(),
                          parse_mode='Markdown', reply_markup=keyboard,
                          disable_web_page_preview=True)

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return 'retry', "I'm sorry, there has been an error in sending the post."

    return 'success', None


def edit_result(bot, update):
    '''
    Edits the given message with a new post from that subreddit, and edits the
    keyboard markup to give the user the ability to edit or confirm the message.
    '''
    message = update.effective_message
    chat_id = message.chat_id
    message_id = message.message_id
    text = (message.caption or message.text) + '\n'
    subreddit = helpers.get_subreddit_name(text, True)
    if subreddit is None:
        return

    tries = 0
    while tries < MAX_TRIES:
        post, status, err_msg = reddit.get_post(subreddit)
        if status != 'success':
            continue

        msg_is_text = message.caption is None

        if ((msg_is_text and message.text_markdown == post.get_msg())
           or message.caption_markdown == post.get_msg()):
            tries += 1
            continue  # if post is the same retry

        if not msg_is_text and post.get_type() in [ContentType.TEXT, ContentType.YOUTUBE]:
            tries += 1
            continue  # if message is not text and post is retry

        if msg_is_text:
            if post.get_type() == ContentType.TEXT:
                bot.editMessageText(post.get_msg(), chat_id, message_id,
                                    parse_mode='Markdown', reply_markup=EDIT_KEYBOARD,
                                    disable_web_page_preview=True)
            elif post.get_type() == ContentType.YOUTUBE:
                bot.editMessageText(post.get_msg(), chat_id, message_id,
                                    parse_mode='Markdown', reply_markup=EDIT_KEYBOARD)
        else:
            if post.get_type() == ContentType.GIF:
                media = InputMediaDocument(post.media.url, caption=post.get_msg(), parse_mode='Markdown')
            elif post.get_type() == ContentType.VIDEO:
                media = InputMediaVideo(post.media.url, caption=post.get_msg(), parse_mode='Markdown')
            elif post.get_type() == ContentType.PHOTO:
                media = InputMediaPhoto(post.media.url, caption=post.get_msg(), parse_mode='Markdown')
            bot.editMessageMedia(chat_id=chat_id, message_id=message_id, media=media,
                                 reply_markup=EDIT_KEYBOARD)

        break

    if tries >= MAX_TRIES:
        bot.editMessageReplyMarkup(chat_id, message_id,
                                   reply_markup=EDIT_FAILED_KEYBOARD)


def _send_exception_message(bot, chat_id, msg, keyboard=True):
    '''Handles the errors created in post retrieval and sending.'''
    if keyboard:
        bot.sendMessage(chat_id, msg, 'Markdown', reply_markup=NO_EDIT_KEYBOARD)
    else:
        bot.sendMessage(chat_id, msg, 'Markdown')
