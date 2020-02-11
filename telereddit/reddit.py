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
        post_url = f'https://www.reddit.com/{subreddit}/random'
    try:
        json = requests.get(f'{post_url}.json',
                            headers={'User-agent': 'telereddit_bot'}).json()
        if not json:
            raise ValueError
    except ValueError:
        return None, "I'm sorry, I can't find that subreddit."

    # some subreddits have the json data wrapped in brackets, some do not
    json = json if isinstance(json, dict) else json[0]
    err_msg = None

    if json.get('reason') == 'private':
        json, err_msg = None, "I'm sorry, this subreddit is private."
    elif json.get('error') == 404 or len(json['data']['children']) == 0:
        json, err_msg = None, "I'm sorry, this subreddit doesn't exist."

    return json, err_msg


def _get_media(post_url, json={}):
    '''
    Processes the post url to get the media url, based on common url patterns.

    Parameters
    ----------
    post_url : str
        Unprocessed media url.
    json : json
        Full json post data.

    Returns
    -------
    A namedtuple (type, url, size)
    type
        The type of the media. Can be photo, gif, or video.
    url
        The processed media url.
    size
        The filesize of the media. It can be None.
    '''
    fallback_url = helpers.chained_get(json, ['media', 'reddit_video', 'fallback_url'])
    media_type = 'photo'
    file_size = None
    if 'gfycat.com' in post_url:
        url_prefix = post_url.replace('gfycat.com', 'thumbs.gfycat.com')
        post_url = url_prefix + '-size_restricted.gif'
        try:
            requests.get(post_url, stream=True)
        except Exception:
            post_url = url_prefix + '-mobile.mp4'

    if 'v.redd.it' in post_url:
        post_url = fallback_url if fallback_url else f'{post_url}/DASH_1_2_M'
        media_type = 'gif'

    if 'imgur' in post_url:
        post_url = post_url.replace('.png', '.jpg')
        if '.gifv' in post_url:
            gif_hash = post_url.split('/')[-1].replace('.gifv', '')
            post_url, media_type = f'https://imgur.com/download/{gif_hash}', 'gif'
        elif not post_url.replace('.jpg', '').endswith(('s', 'b', 't', 'm', 'l', 'h')):
            post_url, media_type = post_url.replace('.jpg', '') + 'h.jpg', 'photo'

    if '.gif' in post_url:
        media_type = 'gif'
    if '.mp4' in post_url:
        media_type = 'video'

    if 'youtube.com' in post_url or 'youtu.be' in post_url:
        oembed_url = helpers.chained_get(json, ['media', 'oembed', 'url'])
        if oembed_url:
            post_url = oembed_url
        media_type = 'youtube'
    else:
        file_size = int(
            requests.get(
                post_url, 
                headers={'Authorization': 'Client-ID 90bd24c00c6efe0'}, 
                stream=True
            ).headers['Content-length'])

    media = namedtuple('media', 'type url size')
    return media(media_type, post_url, file_size)


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
        permalink = data['permalink']
        subreddit = data['subreddit_name_prefixed']
        subreddit_url = f'https://www.reddit.com/{subreddit}'
        post_footer = f"[Link to post](https://reddit.com{permalink}) | "\
                      f"[{subreddit}]({subreddit_url})"
        post_title = helpers.escape_markdown(data['title'])
        post_text = helpers.truncate_text(data['selftext'], MAX_POST_LENGTH)
        content_url = data['url']

        media_size = None
        media = media_url = media_size = None
        if '/comments/' in content_url:
            post_type, media_url = 'text', None
        else:
            media = _get_media(content_url, data)
            post_type = media.type
            media_url = media.url
            media_size = media.size

        post_text = helpers.escape_markdown(post_text)
        if media and media.type == 'youtube':
            post_text = post_text + f"\n\n[Link to youtube video]({media.url})"

        full_msg = f"*{post_title}*\n{post_text}\n\n{post_footer}"

        post = namedtuple('Post', 'subreddit title text msg footer permalink '
                          'content_url type media_url media_size')
        return post(subreddit, post_title, post_text, full_msg, post_footer, permalink,
                    content_url, post_type, media_url, media_size), 'success', None

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return None, 'failed', f"I'm sorry, the retrieval of the post failed."
