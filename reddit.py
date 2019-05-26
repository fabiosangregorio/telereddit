import requests
from collections import namedtuple
import random
import traceback

from sentry_sdk import capture_exception

import helpers
from config import MAX_POST_LENGTH


def _get_json(subreddit=None, post_url=None):
    if not post_url:
        post_url = f'https://www.reddit.com/{subreddit}/random.json'
    try:
        json = requests.get(post_url, headers={'User-agent': 'telereddit_bot'}).json()
    except ValueError:
        return None, f"I'm sorry, I can't find that subreddit."

    if not json:
        return None, f"I'm sorry, I can't find that subreddit."

    # some subreddits have the json data wrapped in brackets, some do not
    json = json if isinstance(json, dict) else json[0]

    if json.get('reason') == 'private':
        return None, f"I'm sorry, this subreddit is private."

    not_found = json.get('error', 200) == 404 or len(json['data']['children']) == 0
    if not_found:
        return None, f"I'm sorry, this subreddit doesn't exist!"

    return json, None


def _get_media(post_url, data):
    # check if content is gif and return the gif url
    type = 'photo'
    if 'gfycat.com' in post_url:
        post_url, type = (post_url.replace('gfycat.com', 'thumbs.gfycat.com') +
                          '-size_restricted.gif'), 'gif'
        try:
            requests.get(post_url)
        except Exception:
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


def get_post(subreddit=None, post_url=None):
    if not subreddit and not post_url:
        return None, None, None

    json, err_msg = _get_json(subreddit, post_url)
    if err_msg:
        return None, 'not_found', err_msg

    try:
        idx = random.randint(0, len(json['data']['children']) - 1)
        data = json['data']['children'][idx]['data']
        subreddit_url = f'https://www.reddit.com/{subreddit}'
        content_url = data['url']
        permalink = data['permalink']
        post_footer = f"[Link to post](https://reddit.com{permalink}) | "\
                      f"[{subreddit}]({subreddit_url})"

        subreddit = data['subreddit_name_prefixed']
        post_title = data['title']

        post_text = helpers.truncate_text(data['selftext'], MAX_POST_LENGTH)
        post_text = helpers.escape_markdown(post_text)
        post_text = post_text + '\n\n' if post_text else ''
        full_msg = f"{post_title}{post_text}\n\n{post_footer}"

        media_type, media_url = _get_media(content_url, data)

        post = namedtuple('Post', 'subreddit title text msg footer permalink '
                          'content_url media_type media_url')
        return post(subreddit, post_title, post_text, full_msg, post_footer, permalink,
                    content_url, media_type, media_url), 'success', None

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return None, 'failed', f"I'm sorry, an error occurred in retrieving the post from "\
            f"{subreddit} :(\nThe developer must have missed an if statement!"
