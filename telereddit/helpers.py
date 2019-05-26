import re
from config import MAX_TITLE_LENGTH


def get_subreddit_names(text):
    regex = r'r/[A-Za-z0-9][A-Za-z0-9_]{2,20}(?=\s|\W |$|\W$|/)'
    return re.findall(regex, text, re.MULTILINE)


def get_subreddit_name(text):
    subs = get_subreddit_names(text)
    if len(subs):
        return subs[0]
    else:
        return None


def escape_markdown(text):
    return text.replace('*', '\\*').replace('_', '\\_')


def truncate_text(text, length=MAX_TITLE_LENGTH):
    return text[:length] + (text[length:] and '...')


def polish_text(text):
    return text.replace('\n', ' ')


def get_urls_from_text(text):
    polished = polish_text(text)
    urls = list()
    for w in polished.lower().split(' '):
        if 'reddit.com' in w:
            urls.append(w.partition('/?')[0] + '.json')
        if 'redd.it' in w:
            urls.append(f'https://www.reddit.com/comments/{w.partition("redd.it/")[2]}.json')
    return urls
