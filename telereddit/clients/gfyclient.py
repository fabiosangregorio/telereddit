import requests

import telereddit.secret as secret
from telereddit.clients.client import Client
from telereddit.media import Media


class Gfycat(Client):
    access_token = ""

    def __init__(self):
        self.authenticate()

    def preprocess(self, parsed_url):
        gfyid = parsed_url.path  # sempre? es. https://gfycat.com/heavenlybiodegradablebuckeyebutterfly
        return f'https://api.gfycat.com/v1/gfycats/{gfyid}'

    def get(self, url, status=None):
        return requests.get(
            url,
            headers={'Authorization': f'Bearer {self.access_token}'},
            stream=True
        )

    def postprocess(self, response):
        gfy_item = response.gfyItem
        media = Media(gfy_item.webmUrl, 'gif', gfy_item.webmSize)
        if media.size > 20000000:
            media.url = gfy_item.max5mbGif
            media.size = 5000000
        return media

    def authenticate(self):
        response = requests.post("https://api.gfycat.com/v1/oauth/token", {
            'grant_type': 'client_credentials',
            'client_id': secret.GFYCAT_CLIENT_ID,
            'client_secret': secret.GFYCAT_CLINET_SECRET
        })
        if response.status_code >= 300:
            raise Exception("Gfycat authentication failed")

        self.access_token = response.access_token

