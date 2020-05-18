"""Miscellaneous helpers for the whole application."""

import re
import requests

from telereddit.config.config import MAX_TITLE_LENGTH


def get_random_post_url(subreddit):
    """
    Return the "random post" url relative to the Reddit API.

    Parameters
    ----------
    subreddit : str
        Subreddit for which to get the url.

    Returns
    -------
    str
        A new string representing the url, including the base url of reddit.

    """
    return f"https://www.reddit.com/{subreddit}/random"


def get_subreddit_names(text):
    """
    Return a list of the ("r/" prefixed) subreddit names present in the text.

    Subreddits are searched using the official subreddit name validation.

    .. seealso::
        Subreddit name validation regex:
        https://github.com/reddit-archive/reddit/blob/master/r2/r2/models/subreddit.py#L114

    Parameters
    ----------
    text : str
        String of text in which to search for subreddit names.

    Returns
    -------
    array
        Array of valid subreddit names present in the given text ("r/" prefixed).

    """
    regex = r"\br/[A-Za-z0-9][A-Za-z0-9_]{2,20}(?=\s|\W |$|\W$|/)\b"
    return re.findall(regex, text, re.MULTILINE)


def get_subreddit_name(text, reverse=False):
    """
    Return the first (or last) ("r/" prefixed) subreddit name in the given text.

    Parameters
    ----------
    text : str
        String of text in which to search for the subreddit name.

    reverse : Boolean
        (Default value = False)

        Whether to return the first or last match in the string.

    Returns
    -------
    str or None
        The subreddit name if present in the text, None otherwise.

    """
    subs = get_subreddit_names(text)
    if len(subs):
        return subs[-1] if reverse else subs[0]
    else:
        return None


def escape_markdown(text):
    """
    Return the given text with escaped common markdown characters.

    .. seealso::
        Official Telegram supported Markdown documentation:
        https://core.telegram.org/bots/api#Markdown-style

    Parameters
    ----------
    text : str
        Unescaped text to escape.

    Returns
    -------
    str
        New string containing the escaped text.

    """
    return text.replace("*", "\\*").replace("_", "\\_")


def truncate_text(text, length=MAX_TITLE_LENGTH):
    """
    Return the given text, truncated at `length` characters, plus ellipsis.

    Parameters
    ----------
    text : str
        String to truncate.

    length : int
        (Default value = MAX_TITLE_LENGTH)

        Length to which to truncate the text, not including three characters of
        ellipsis.

    Returns
    -------
    str
        New string containing the truncated text, plus ellipsis.

    """
    if length < 0:
        return text
    return text[:length] + (text[length:] and "...")


def polish_text(text):
    """
    Return the given text without newline characters.

    Parameters
    ----------
    text : str
        Text to polish

    Returns
    -------
    str
        New string containing the polished text.

    """
    return text.replace("\n", " ")


def get_urls_from_text(text):
    """
    Return a list of the reddit urls present in the given text.

    Parameters
    ----------
    text : str
        Text to search for urls.

    Returns
    -------
    array
        Array containing all the reddit links extracted from the text.

    """
    polished = polish_text(text)
    urls = list()
    for w in polished.split(" "):
        w_lower = w.lower()
        if "reddit.com" in w_lower:
            urls.append(w.partition("/?")[0])
        if "redd.it" in w_lower:
            urls.append(
                f'https://www.reddit.com/comments/{w.partition("redd.it/")[2]}'
            )
        if "reddit.app.link" in w_lower:
            try:
                r = requests.get(
                    w,
                    headers={"User-agent": "telereddit_bot"},
                    allow_redirects=False,
                )
                start = r.text.find("https://")
                url = r.text[start : r.text.find('"', start)]
                if len(url) > 0:
                    urls.append(url.partition("/?")[0])
            except Exception:
                pass
    return urls


def get(obj, attr, default=None):
    """
    Return the value of `attr` if it exists and is not None, default otherwise.

    Useful when you don't want to have a `KeyError` raised if the attribute is
    missing in the object.

    Parameters
    ----------
    obj : object
        The object for which to return the attribute.
    attr : str
        The key of the attribute to return.
    default : any
        (Default value = None)

        What to return if `obj` doesn't have the `attr` attribute, or if it is
        None.

    Returns
    -------
    any
        The attribute or `default`.

    """
    return obj[attr] if attr in obj and obj[attr] is not None else default


def chained_get(obj, attrs, default=None):
    """
    Get for nested objects.

    Travel the nested object based on `attrs` array and return the value of
    the last attr if not None, default otherwise.

    Useful when you don't want to have a `KeyError` raised if an attribute of
    the chain is missing in the object.

    Parameters
    ----------
    obj : object
        The object for which to return the attribute.
    attrs : array
        Array of keys to search for recursively.
    default : any
        (Default value = None)

        What to return if `obj` doesn't have any of the `attrs` attributes, or
        if they are None.

    Returns
    -------
    any
        The attribute corresponding to the right-most key in `attrs`, if it
        exists and is not None, `default` otherwise.

    """
    for attr in attrs:
        obj = get(obj, attr, default)
        if obj == default:
            break
    return obj
