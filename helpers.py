def get_subreddit_name(text):
    text = text.replace('\n', ' ')
    start = text.find('r/')
    end = text.find(' ', start)
    word = text[start:end] if end is not -1 else text[start:]
    subreddit = word.split('/')[0] + '/' + word.split('/')[1]
    return subreddit


def escape_markdown(text):
    return text.replace('*', '\\*').replace('_', '\\_')


def truncate_text(text, length=100):
    return text[:length] + (text[length:] and '...')