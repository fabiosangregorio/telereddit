import requests

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from chatbase import Message

from config import MAX_REDDIT_POST_LENGTH
from secret import CHATBASE_TOKEN as TOKEN


def send_link(bot, chat_id, text):
    if 'r/' not in text.lower():
        return

    while 'r/' in text:
        # remove reddit links from the text and send it to the chat
        start = text.find('r/')
        end = text.find(' ', start)
        link = text[start:end] if end is not -1 else text[start:]
        text = text.replace(link, '')

        send_random_post(bot, chat_id, link)


def send_random_post(bot, chat_id, link):
    try:
        random_url = 'https://' + f'www.reddit.com/{link}/random.json'.replace('//', '/')
        req = requests.get(random_url, headers={'User-agent': 'telereddit_bot'}).json()

        # check if subreddit is private
        if hasattr(req, 'reason') and req['reason'] == 'private':
            bot.sendMessage(chat_id, 'Subreddit privato')
            return

        # some subreddits have the json data wrapped in brackets, some do not
        data = req['data']['children'][0]['data'] if isinstance(req, dict) else req[0]['data']['children'][0]['data']
        subreddit_url = f'www.reddit.com/{link}'
        post_title = data['title'][:100] + (data['title'][100:] and '...') # truncate the title if it's too long
        post_text = data['selftext']
        post_url = data['url']

        # setting up the "more" button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Show more', callback_data='reddit')]
        ])
        msg_text = f"{post_title}\n\n[Link to post]({post_url}) | [{link}]({subreddit_url})"

        post_is_gif, gif_url = is_gif(post_url)

        # check if the post is a text post
        if '/comments/' in post_url:
            post_text = post_text[:MAX_REDDIT_POST_LENGTH] + (post_text[MAX_REDDIT_POST_LENGTH:] and '...')
            bot.sendMessage(chat_id, f"{msg_text}\n\n{post_text}", reply_markup=keyboard, parse_mode='Markdown')
        # check if the post contains a gif
        elif post_is_gif:
            bot.sendDocument(chat_id, gif_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')
        elif '.mp4' in post_url:
            bot.sendVideo(chat_id, post_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            bot.sendPhoto(chat_id, post_url, msg_text, reply_markup=keyboard, parse_mode='Markdown')
        msg = Message(api_key=TOKEN,
            platform="Telegram",
            version="1.0",
            user_id=chat_id,
            message=link,
            intent="random_post")
        msg.send()
    except Exception as e:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Try again', callback_data='reddit')]
        ])
        print(e)
        bot.sendMessage(chat_id, f"I'm sorry, an error occurred in retrieving\nthe random post from {link} :(\n"\
            "The developer must have missed an if statement!", reply_markup=keyboard, parse_mode='Markdown')
        msg = Message(api_key=TOKEN,
            platform="Telegram",
            version="1.0",
            user_id=chat_id,
            message=link,
            not_handled=True,
            intent="random_post")
        msg.send()


# check if content is gif and return the gif url
def is_gif(post_url):
    gif = False
    if 'gfycat.com' in post_url:
        post_url, gif = post_url.replace('gfycat.com','thumbs.gfycat.com') + '-size_restricted.gif', True
        try:
            requests.get(post_url)
        except:
            post_url, gif = post_url.replace('gfycat.com','thumbs.gfycat.com') + '-mobile.mp4', True
            
    if 'v.redd.it' in post_url:
        post_url, gif = f'{post_url}/DASH_1_2_M', True
    if 'imgur' in post_url and '.gif' in post_url:
        post_url, gif = post_url.replace('.gifv','.jpg'), True
    if '.gif' in post_url:
        gif = True

    return gif, post_url


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

    send_link(bot, chat_id, link)
