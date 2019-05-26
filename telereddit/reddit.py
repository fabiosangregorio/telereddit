import requests
from collections import namedtuple
import random
import traceback

from sentry_sdk import capture_exception

import helpers
from config import MAX_POST_LENGTH


def _get_json(subreddit=None, post_url=None):
    '''
    Handles the http request and gets the json for the given subreddit/post url.

    Parameters
    ----------
    subreddit : str
        Prefixed subreddit name for which to get the json. Can be None if
        `post_url` is provided.
    post_url : str
        Full url of the post to retrieve. Can be None if `subreddit` is provided.

    Returns
    -------
    json
        Json for the given subreddit/post url if the subreddit exists
        and is public, an error otherwise.
    err_msg
        Message containing the reason for the error.
    '''
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
    '''
    Processes the post url to get the media url, based on common url patterns.

    Parameters
    ----------
    post_url : str
        Unprocessed media url.
    data : json
        Full json post data.

    Returns
    -------
    type
        The type of the media. Can be photo, gif, or video.
    media_url
        The processed media url.
    '''
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
        fallback_url = data.get('media', {}).get('reddit_video', {}).get('fallback_url')
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
    '''
    Processes the json and gets the post out of it, ready to be sent.

    Parameters
    ----------
    subreddit : str
        Prefixed subreddit name for which to get the json. Can be None if
        `post_url` is provided.
    post_url : str
        Full url of the post to retrieve. Can be None if `subreddit` is provided.

    Returns
    -------
    Post
        A namedtuple containing: subreddit, title, text, msg, footer, permalink,
        content_url, media_type, media_url
    Status
        The result of the post processing. Can be: success, not_found, failed.
    err_msg
        Message containing the reason for the error.
    '''
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
        subreddit = data['subreddit_name_prefixed']
        post_footer = f"[Link to post](https://reddit.com{permalink}) | "\
                      f"[{subreddit}]({subreddit_url})"

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
