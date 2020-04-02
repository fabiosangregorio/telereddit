import requests
import random
import traceback

from sentry_sdk import capture_exception

import helpers
from helpers import try_pass
from config.config import MAX_POST_LENGTH

from post import Post
from content_type import ContentType
from status import OkStatus, KoStatus

from services.services_wrapper import ServicesWrapper


def _get_json(post_url):
    response = try_pass(lambda: requests.get(f'{post_url}.json', headers={'User-agent': 'telereddit_bot'}))
    if(not response or not response.json()):
        return KoStatus("I'm sorry, I can't find that subreddit.")
    # some subreddits have the json data wrapped in brackets, some do not
    json = response.json()
    json = json if isinstance(json, dict) else json[0]

    status = OkStatus(json)
    if json.get('reason') == 'private':
        status = KoStatus("I'm sorry, this subreddit is private.")
    elif (json.get('error') == 404 or len(json['data']['children']) == 0
          or (len(response.history) > 0 and "search.json" in response.url)):
        # r/opla redirects to search.json page but subreddit doesn't exist
        status = KoStatus("I'm sorry, this subreddit doesn't exist.")

    return status


def get_post(post_url):
    status = _get_json(post_url)
    if not status.ok:
        status.err_code = "not_found"
        return status

    json = status.data

    try:
        idx = random.randint(0, len(json['data']['children']) - 1)
        data = json['data']['children'][idx]['data']
        subreddit = data['subreddit_name_prefixed']
        permalink = data['permalink']
        post_title = helpers.escape_markdown(data['title'])
        post_text = helpers.truncate_text(data['selftext'], MAX_POST_LENGTH)
        content_url = data['url']

        media = None
        if '/comments/' not in content_url:
            media = ServicesWrapper.get_media(content_url, data)
            if media.type == ContentType.YOUTUBE:
                post_text = f"{post_text}\n\n[Link to youtube video]({media.url})"

        post_text = helpers.escape_markdown(post_text)

        post = Post(subreddit, permalink, post_title, post_text, media)
        return OkStatus(post)

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return KoStatus("I'm sorry, the retrieval of the post failed.")
