import unittest
from services.services_wrapper import ServicesWrapper


class TestServices(unittest.TestCase):
    def test_get_media(self):
        # i.redd.it image
        media = ServicesWrapper.get_media("https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(media.url, "https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(media.type, 'photo')

        # v.redd.it video
        json = {
            "media": {
                "reddit_video": {
                    "fallback_url": "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback"
                }
            }
        }
        media = reddit._get_media("https://v.redd.it/4phan5t9wq031", json)
        self.assertEqual(media.url, "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback")
        self.assertEqual(media.type, 'gif')

        # i.redd.it gif
        media = reddit._get_media("https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(media.url, "https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(media.type, 'gif')

        # imgur gif
        media = reddit._get_media("https://i.imgur.com/2WNMUqO.gifv")
        self.assertEqual(media.url, "https://imgur.com/download/2WNMUqO")
        self.assertEqual(media.type, 'gif')

        # gfycat gif
        media = reddit._get_media("https://gfycat.com/HeartfeltHollowIberianchiffchaff")
        self.assertEqual(media.url, "https://thumbs.gfycat.com/HeartfeltHollowIberianchiffchaff-size_restricted.gif")
        self.assertEqual(media.type, 'gif')

        # youtube link (attribution link)
        json = {
            "media": {
                "oembed": {
                    "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                }
            }
        }
        media = reddit._get_media("https://www.youtube.com/attribution_link?a=o3Cq80oOnoc&u=%2Fwatch%3Fv%3D3OSc_psp4k0%26feature%3Dshare", json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, 'youtube')

        # youtube link (youtube.com)
        json = {
            "media": {
                "oembed": {}
            }
        }
        media = reddit._get_media("https://www.youtube.com/watch?v=DJxchZ7qAzE", json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, 'youtube')

        # youtube link (youtube.com)
        json = {
            "media": {
                "oembed": {
                    "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                }
            }
        }
        media = reddit._get_media("https://www.youtu.be/watch?v=DJxchZ7qAzE", json)
        self.assertEqual(media.url, "https://www.youtube.com/watch?v=DJxchZ7qAzE")
        self.assertEqual(media.type, 'youtube')

    def test_get_post(self):
        # text post
        post, status, err_msg = reddit.get_post('r/showerthoughts')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/showerthoughts')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/showerthoughts', post.footer.lower())
        self.assertEqual(post.type, 'text')

        # photo post
        post, status, err_msg = reddit.get_post('r/pics')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/pics')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/pics', post.footer.lower())
        self.assertIsNotNone(post.media_url)
        self.assertEqual(post.type, 'photo')

        # crosspost
        post, status, err_msg = reddit.get_post(post_url='https://www.reddit.com/r/bicycling/comments/aevkgj/finally_know_how_to_crosspost/')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/bicycling')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/bicycling', post.footer.lower())
        self.assertIsNotNone(post.media_url)
        self.assertEqual(post.type, 'photo')
