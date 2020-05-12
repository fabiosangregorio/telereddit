"""
Reddit API interface module. Contains all the functions to call Reddit APIs,
retrieve the desired information and build telereddit objects.
"""

import requests
import random

import telereddit.helpers as helpers
from telereddit.config.config import secret
from telereddit.models.post import Post
from telereddit.models.content_type import ContentType
from telereddit.exceptions import (
    PostRequestError,
    SubredditPrivateError,
    SubredditDoesntExistError,
    PostRetrievalError,
)
from telereddit.services.services_wrapper import ServicesWrapper


def _get_json(post_url):
    """

    Parameters
    ----------
    post_url :
        

    Returns
    -------

    
    """
    try:
        response = requests.get(
            f"{post_url}.json",
            headers={"User-agent": secret.TELEREDDIT_USER_AGENT},
        )
        json = response.json()
        # some subreddits have the json data wrapped in brackets, some do not
        json = json if isinstance(json, dict) else json[0]
    except Exception:
        raise PostRequestError({"post_url": post_url})

    if json.get("reason") == "private":
        raise SubredditPrivateError()
    elif (
        json.get("error") == 404
        or len(json["data"]["children"]) == 0
        or (len(response.history) > 0 and "search.json" in response.url)
    ):
        # r/opla redirects to search.json page but subreddit doesn't exist
        raise SubredditDoesntExistError()

    return json


def get_post(post_url):
    """

    Parameters
    ----------
    post_url :
        

    Returns
    -------

    
    """
    json = _get_json(post_url)

    try:
        idx = random.randint(0, len(json["data"]["children"]) - 1)
        data = json["data"]["children"][idx]["data"]
        subreddit = data["subreddit_name_prefixed"]
        permalink = data["permalink"]
        post_title = helpers.escape_markdown(data["title"])
        post_text = helpers.truncate_text(data["selftext"])
        content_url = data["url"]

        media = None
        if "/comments/" not in content_url:
            media = ServicesWrapper.get_media(content_url, data)
            if media.type == ContentType.YOUTUBE:
                post_text = (
                    f"{post_text}\n\n[Link to youtube video]({media.url})"
                )

        post_text = helpers.escape_markdown(post_text)
        post = Post(subreddit, permalink, post_title, post_text, media)
        return post

    except Exception:
        raise PostRetrievalError({"post_url": post_url})
