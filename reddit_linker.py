import requests
import random
import traceback

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from sentry_sdk import capture_exception

from config import MAX_POST_LENGTH, MAX_TRIES

import helpers


def send_random_posts(bot, chat_id, text):
    # searches in text for subreddit names and sends a random post from the subreddit
    subreddits = helpers.get_subreddit_names(text)
    for subreddit in subreddits:
        tries = 0
        while tries < MAX_TRIES:
            status, fail_msg = send_post(bot, chat_id, subreddit)
            if status == 'success':
                break
            if status == 'failed':
                tries += 1
        if status != 'success':
            _send_exception_message(bot, chat_id, subreddit, fail_msg)


def send_post_from_url(bot, chat_id, post_url):
    subreddit = helpers.get_subreddit_names(post_url)
    if not len(subreddit):
        return
    subreddit = subreddit[0]
    status, fail_msg = send_post(bot, chat_id, subreddit, post_url)
    if status == 'failed':
        _send_exception_message(bot, chat_id, subreddit, fail_msg)


def _get_post(subreddit, post_url=None):
    if not post_url:
        post_url = f'https://www.reddit.com/{subreddit}/random.json'
    try:
        json = requests.get(post_url, headers={'User-agent': 'telereddit_bot'}).json()
    except ValueError:
        return None, f"I'm sorry, I can't find {subreddit}."

    if not json:
        return None, f"I'm sorry, I can't find {subreddit}."

    # some subreddits have the json data wrapped in brackets, some do not
    json = json if isinstance(json, dict) else json[0]

    if json.get('reason') == 'private':
        return None, f"I'm sorry, the subreddit {subreddit} is private."

    not_found = json.get('error', 200) == 404 or len(json['data']['children']) == 0
    if not_found:
        return None, f"I'm sorry, the subreddit {subreddit} doesn't exist!"

    return json, None


def send_post(bot, chat_id, subreddit, post_url=None):
    json, err_msg = _get_post(subreddit, post_url)
    if err_msg:
        bot.sendMessage(chat_id, err_msg)
        return 'success', None

    subreddit_url = f'https://www.reddit.com/{subreddit}'
    try:
        idx = random.randint(0, len(json['data']['children']) - 1)
        data = json['data']['children'][idx]['data']

        post_text = data['selftext']
        content_url = data['url']
        permalink = data['permalink']
        post_title = helpers.escape_markdown(helpers.truncate_text(data['title']))
        post_footer =f"[Link to post](https://reddit.com{permalink}) | "\
            f"[{subreddit}]({subreddit_url})"
        full_msg = f"{post_title}\n\n{post_footer}"
        media_type, media_url = _get_media(content_url, data)
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return 'failed', f"I'm sorry, an error occurred in retrieving the post from "\
            f"{subreddit} :(\nThe developer must have missed an if statement!"

    try:
        # setting up the "Show more" button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Show more', callback_data='reddit')]
        ])
        if 'www.youtube.com' in media_url:
            bot.sendMessage(chat_id, 
                f"I'm sorry, youtube videos are not supported yet :(", 'Markdown')
            return 'success', None

        # check if the post is a text post
        if '/comments/' in content_url:
            post_text = helpers.escape_markdown(
                post_text[:MAX_POST_LENGTH] + 
                (post_text[MAX_POST_LENGTH:] and '...'))
            bot.sendMessage(chat_id, f"{post_title}\n\n{post_text}\n\n{post_footer}",
                            'Markdown', reply_markup=keyboard)
        elif media_type == 'gif':
            bot.sendDocument(chat_id, media_url, full_msg, 
                             'Markdown', reply_markup=keyboard)
        elif media_type == 'video':
            bot.sendVideo(chat_id, media_url, full_msg, 
                          'Markdown', reply_markup=keyboard)
        else:
            bot.sendPhoto(chat_id, media_url, full_msg, 
                          'Markdown', reply_markup=keyboard)

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return 'failed', f"I'm sorry, an error occurred in sending the post from "\
            f"{subreddit} :(\nThe developer must have missed an if statement!"

    return 'success', None


def _get_media(post_url, data):
    # check if content is gif and return the gif url
    type = 'photo'
    if 'gfycat.com' in post_url:
        post_url, type = (post_url.replace('gfycat.com', 'thumbs.gfycat.com') +
                          '-size_restricted.gif'), 'gif'
        try:
            requests.get(post_url)
        except:
            post_url, type = (post_url.replace('gfycat.com', 'thumbs.gfycat.com') +
                              '-mobile.mp4'), 'gif'

    if 'v.redd.it' in post_url:
        fallback_url = data.get('media', {}).get('reddit_video', {}).get('scrubber_media_url')
        post_url = fallback_url if fallback_url else f'{post_url}/DASH_1_2_M'
        type = 'gif'

    if 'imgur' in post_url:
        post_url = post_url.replace('.png', '.jpg')
        if '.gifv' in post_url:
            gif_hash = post_url.split('/')[-1].replace('.gifv', '')
            post_url, type = f'https://imgur.com/download/{gif_hash}', 'gif'
        elif not post_url.replace('.jpg', '').endswith(('s', 'b', 't', 'm', 'l', 'h')):
            post_url, type = post_url.replace('.jpg', '') + 'h.jpg', 'photo'

    if '.gif' in post_url:
        type = 'gif'
    if '.mp4' in post_url:
        type = 'video'

    return type, post_url


def more_button_callback(bot, msg):
    # upon clicking the "more" button, send another random reddit post
    message = msg['message'] 
    chat_id = message['chat']['id']
    text = message.get('caption', message.get('text')) + '\n'
    subreddit = helpers.get_subreddit_names(text)
    if len(subreddit):
        subreddit = subreddit[0]
    send_random_posts(bot, chat_id, subreddit)


def _send_exception_message(bot, chat_id, subreddit, msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Try with another random post', callback_data='reddit')]
    ])
    bot.sendMessage(chat_id, msg, 'Markdown', reply_markup=keyboard)
