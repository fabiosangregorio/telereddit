import requests

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from chatbase import Message
from sentry_sdk import capture_exception

from config import MAX_REDDIT_POST_LENGTH
from secret import CHATBASE_TOKEN as TOKEN


def _get_subreddit_name(text):
    start = text.find('r/')
    end = text.find(' ', start)
    word = text[start:end] if end is not -1 else text[start:]
    subreddit = word.split('/')[0] + '/' + word.split('/')[1]
    return subreddit


def _escape_markdown(text):
    return text.replace('*', '\\*').replace('_', '\\_')


def send_random_posts(bot, chat_id, text):
    while 'r/' in text:
        # remove reddit links from the text and send it to the chat
        subreddit = _get_subreddit_name(text)
        text = text.replace(subreddit, '')
        post_url = 'https://' + f'www.reddit.com/{subreddit}/random.json'.replace('//', '/')
        send_post(bot, chat_id, subreddit, post_url)


def send_post(bot, chat_id, subreddit=None, post_url=None):
    try:
        req = requests.get(post_url, headers={'User-agent': 'telereddit_bot'}).json()
        if not subreddit:
            subreddit = _get_subreddit_name(post_url)

        # check if subreddit is private
        if hasattr(req, 'reason') and req['reason'] == 'private':
            bot.sendMessage(chat_id, 'Subreddit privato')
            return

        # some subreddits have the json data wrapped in brackets, some do not
        data = req['data']['children'][0]['data'] if isinstance(req, dict) else req[0]['data']['children'][0]['data']
        subreddit_url = f'www.reddit.com/{subreddit}'
        post_title = data['title'][:100] + (data['title'][100:] and '...') # truncate the title if it's too long
        post_text = data['selftext']
        post_url = data['url']
        permalink = data['permalink']

        # setting up the "more" button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Show more', callback_data='reddit')]
        ])
        msg_text = f"{_escape_markdown(post_title)}\n\n[Link to post](https://reddit.com{permalink}) | [{subreddit}]({subreddit_url})"
        media_type, media_url = _get_media(post_url)
    except Exception as e:
        _send_exception_message(bot, chat_id, f"I'm sorry, an error occurred in retrieving\nthe post from {subreddit} :(\n"\
            "The developer must have missed an if statement!", e)

    try:
        # check if the post is a text post
        if '/comments/' in post_url:
            post_text = _escape_markdown(post_text[:MAX_REDDIT_POST_LENGTH] + (post_text[MAX_REDDIT_POST_LENGTH:] and '...'))
            bot.sendMessage(chat_id, f"{post_text}\n\n{msg_text}", reply_markup=keyboard, parse_mode='Markdown')
        elif media_type == 'gif':
            bot.sendDocument(chat_id, media_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')
        elif media_type == 'video':
            bot.sendVideo(chat_id, media_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            bot.sendPhoto(chat_id, media_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')

        msg = Message(api_key=TOKEN,
            platform="Telegram",
            version="1.0",
            user_id=chat_id,
            message=subreddit,
            intent="random_post")
        msg.send()
    except Exception as e:
        _send_exception_message(bot, chat_id, f"I'm sorry, an error occurred in sending\nthe post from {subreddit} :(\n"\
            "The developer must have missed an if statement!", e)


def _send_exception_message(bot, chat_id, msg, e):
    capture_exception(e)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Try again', callback_data='reddit')]
    ])
    bot.sendMessage(chat_id, msg, reply_markup=keyboard, parse_mode='Markdown')
    msg = Message(api_key=TOKEN,
        platform="Telegram",
        version="1.0",
        user_id=chat_id,
        message=subreddit,
        not_handled=True,
        intent="random_post")
    msg.send()


# check if content is gif and return the gif url
def _get_media(post_url):
    type = 'photo'
    if 'gfycat.com' in post_url:
        post_url, type = post_url.replace('gfycat.com','thumbs.gfycat.com') + '-size_restricted.gif', 'gif'
        try:
            requests.get(post_url)
        except:
            post_url, type = post_url.replace('gfycat.com','thumbs.gfycat.com') + '-mobile.mp4', 'gif'
            
    if 'v.redd.it' in post_url:
        post_url, type = f'{post_url}/DASH_1_2_M', 'gif'

    if 'imgur' in post_url:
        post_url = post_url.replace('.png', '.jpg')
        if '.gif' in post_url:
            post_url, type = post_url.replace('.gifv','.jpg'), 'gif'
        elif not post_url.replace('.jpg', '').endswith(('s', 'b', 't', 'm', 'l', 'h')):
            post_url, type = post_url.replace('.jpg', '') + 'h.jpg', 'photo'

    if '.gif' in post_url:
        type = 'gif'
    
    if '.mp4' in post_url:
        type = 'video'

    return type, post_url


# upon clicking the "more" button, send another random reddit post
def more_button_callback(bot, msg):
    message = msg['message'] 
    chat_id = message['chat']['id']
    text = message.get('caption', message.get('text')) + '\n'
    start = text.find('r/')
    link = text[start:text.find('\n', start)]

    msg = Message(api_key=TOKEN,
        platform="Telegram",
        version="1.0",
        user_id=chat_id,
        message=link,
        intent="show_more")
    msg.send()

    send_random_posts(bot, chat_id, link)
