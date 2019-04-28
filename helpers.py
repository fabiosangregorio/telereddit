import re

def get_subreddit_names(text):
    regex = r'r/[A-Za-z0-9][A-Za-z0-9_]{2,20}(?=\s|\W |$|\W$|/)'
    return re.findall(regex, text, re.MULTILINE)


def escape_markdown(text):
    return text.replace('*', '\\*').replace('_', '\\_')


def truncate_text(text, length=100):
    return text[:length] + (text[length:] and '...')


def polish_text(text):
    return text.replace('\n', ' ')