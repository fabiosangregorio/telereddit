import unittest
from services.services_wrapper import ServicesWrapper
from media import MediaType


class TestServices(unittest.TestCase):
    def test_youtube(self):
        # youtube link (attribution link)
        json = {
            "media": {
                "oembed": {
                    "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                }
            }
        }
        media = ServicesWrapper.get_media(
            "https://www.youtube.com/attribution_link?a=o3Cq80oOnoc&u=%2Fwatch%3Fv%3D3OSc_psp4k0%26feature%3Dshare",
            json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, MediaType.YOUTUBE)

        # youtube link (youtube.com)
        json = {
            "media": {
                "oembed": {}
            }
        }
        media = ServicesWrapper.get_media("https://www.youtube.com/watch?v=DJxchZ7qAzE", json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, MediaType.YOUTUBE)

        # youtube link (youtube.com)
        json = {
            "media": {
                "oembed": {
                    "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                }
            }
        }
        media = ServicesWrapper.get_media("https://www.youtu.be/watch?v=DJxchZ7qAzE", json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, MediaType.YOUTUBE)

    def test_imgur(self):
        # imgur gif
        media = ServicesWrapper.get_media("https://i.imgur.com/2WNMUqO.gifv")
        self.assertEqual(media.url, "https://i.imgur.com/2WNMUqO.mp4")
        self.assertEqual(media.type, MediaType.VIDEO)

    def test_gfycat(self):
        # gfycat gif
        media = ServicesWrapper.get_media("https://gfycat.com/HeartfeltHollowIberianchiffchaff")
        self.assertEqual(media.url, "https://giant.gfycat.com/HeartfeltHollowIberianchiffchaff.mp4")
        self.assertEqual(media.type, MediaType.VIDEO)

    def test_vreddit(self):
        # v.redd.it video
        json = {
            "media": {
                "reddit_video": {
                    "fallback_url": "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback"
                }
            }
        }
        media = ServicesWrapper.get_media("https://v.redd.it/4phan5t9wq031", json)
        self.assertEqual(media.url, "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback")
        self.assertEqual(media.type, MediaType.GIF)

    def test_generic(self):
        # i.redd.it image
        media = ServicesWrapper.get_media("https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(media.url, "https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(media.type, MediaType.PHOTO)

        # i.redd.it gif
        media = ServicesWrapper.get_media("https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(media.url, "https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(media.type, MediaType.GIF)