"""
Reddit API interface module.

Contains all the functions to call Reddit APIs, retrieve the desired information
and build telereddit objects.
"""

import requests
import random
import icontract

from typing import Any

import telereddit.helpers as helpers
from telereddit.config.config import secret
from telereddit.models.post import Post
from telereddit.models.content_type import ContentType
from telereddit.exceptions import (
    PostRequestError,
    SubredditPrivateError,
    SubredditDoesntExistError,
    PostRetrievalError,
    TeleredditError,
)
from telereddit.services.services_wrapper import ServicesWrapper


@icontract.require(
    lambda post_url: post_url is not None, "post_url must not be None"
)
@icontract.ensure(
    lambda result: helpers.chained_get(result, ["data", "children", 0, "data"])
    is not None
)
def _get_json(post_url: str) -> Any:
    """
    Get post json from Reddit API and handle all request/json errors.

    Parameters
    ----------
    post_url : str
        post url to fetch from the Reddit API.

    Returns
    -------
    json
        Json containing the post data.

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


@icontract.require(
    lambda post_url: post_url is not None, "post_url must not be None"
)
@icontract.ensure(lambda result: result is not None)
def get_post(post_url: str) -> Post:
    """
    Get the post from the Reddit API and construct the Post object.

    Parameters
    ----------
    post_url : str
        post url to fetch from the Reddit API.

    Returns
    -------
    `telereddit.models.post.Post`
        Post object containing all the retrieved post information.

    """
    json = _get_json(post_url)
    assert json is not None

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
            assert media is not None
            if media.type == ContentType.YOUTUBE:
                post_text = (
                    f"{post_text}\n\n[Link to youtube video]({media.url})"
                )

        post_text = helpers.escape_markdown(post_text)
        post = Post(subreddit, permalink, post_title, post_text, media)
        return post

    except Exception as e:
        if issubclass(type(e), TeleredditError):
            raise e
        raise PostRetrievalError({"post_url": post_url})
