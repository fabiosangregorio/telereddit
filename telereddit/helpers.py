import re
import requests

from telereddit.config.config import MAX_TITLE_LENGTH


def get_random_post_url(subreddit):
    return f"https://www.reddit.com/{subreddit}/random"


def get_subreddit_names(text):
    """
    Returns a list of the (prefixed) subreddit names present in the given text.
    """
    regex = r"\br/[A-Za-z0-9][A-Za-z0-9_]{2,20}(?=\s|\W |$|\W$|/)\b"
    return re.findall(regex, text, re.MULTILINE)


def get_subreddit_name(text, reverse=False):
    """
    Returns the first (or last if reverse=True) (prefixed) subreddit name if
    present in the given text, None otherwise.
    """
    subs = get_subreddit_names(text)
    if len(subs):
        return subs[-1] if reverse else subs[0]
    else:
        return None


def escape_markdown(text):
    """
    Returns the given text with escaped common markdown characters.
    See: https://core.telegram.org/bots/api#Markdown-style
    """
    # Reddit escaping: \\_ \\* \\[ \\] ( ) \\~ \\` &gt; # + - = | { } . !
    return text.replace("*", "\\*").replace("_", "\\_")


def truncate_text(text, length=MAX_TITLE_LENGTH):
    """
    Returns the given text, truncated at `length` characters, plus ellipsis.
    """
    if length < 0:
        return text
    return text[:length] + (text[length:] and "...")


def polish_text(text):
    """
    Returns the given text without newline characters.
    """
    return text.replace("\n", " ")


def get_urls_from_text(text):
    """
    Returns a list of the urls present in the given text.
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
                r = requests.get(w, headers={"User-agent": "telereddit_bot"})
                start = r.text.find("https://")
                url = r.text[start : r.text.find('"', start)]
                urls.append(url.partition("/?")[0])
            except Exception:
                urls.append("None")
    return urls


def get(obj, attr, default=None):
    """
    Returns the value `attr` if it is not None, default otherwise.
    """
    return obj[attr] if attr in obj and obj[attr] is not None else default


def chained_get(obj, attrs, default=None):
    """
    Travels the nested object based on `attrs` and returns the value of the
    last attr if not None, default otherwise.
    """
    for attr in attrs:
        obj = get(obj, attr, default)
        if obj == default:
            break
    return obj
