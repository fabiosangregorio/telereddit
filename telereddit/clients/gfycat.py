import json

import requests

import secret
from clients.client import Client
from media import Media


class Gfycat(Client):
    access_token = None
    is_authenticated = True

    def __init__(self):
        Gfycat.authenticate()

    @classmethod
    def preprocess(cls, parsed_url, json):
        gfyid = parsed_url.path
        return f'https://api.gfycat.com/v1/gfycats/{gfyid}'

    @classmethod
    def get(cls, url):
        return requests.get(url, headers={'Authorization': f'Bearer {cls.access_token}'})

    @classmethod
    def postprocess(cls, response):
        gfy_item = json.loads(response.content)['gfyItem']
        media = Media(gfy_item["webmUrl"].replace('.webm', '.mp4'), 'video', gfy_item["webmSize"])
        # Telegram does not support webm
        # See: https://www.reddit.com/r/Telegram/comments/5wcqh8/sending_webms_as_videos/
        if media.size > 20000000:
            media.url = gfy_item["max5mbGif"]
            media.type = 'gif'
            media.size = 5000000
        return media

    @classmethod
    def authenticate(cls):
        response = requests.post("https://api.gfycat.com/v1/oauth/token", data=json.dumps({
            'grant_type': 'client_credentials',
            'client_id': secret.GFYCAT_CLIENT_ID,
            'client_secret': secret.GFYCAT_CLINET_SECRET
        }))
        if response.status_code >= 300:
            raise Exception("Gfycat authentication failed")

        cls.access_token = json.loads(response.content)["access_token"]
