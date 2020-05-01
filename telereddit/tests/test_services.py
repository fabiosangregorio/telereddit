import unittest
from parameterized import parameterized, param

from telereddit.services.services_wrapper import ServicesWrapper
from telereddit.content_type import ContentType


class TestServices(unittest.TestCase):
    """ """
    @parameterized.expand(
        [
            # youtube link (attribution link)
            param(
                url="https://www.youtube.com/attribution_link?a=o3Cq80oOnoc&u=%2Fwatch%3Fv%3D3OSc_psp4k0%26feature%3Dshare",
                json={
                    "media": {
                        "oembed": {
                            "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                        }
                    }
                },
                expected_url="https://www.youtube.com/watch?v=DJxchZ7qAzE",
            ),
            # youtube link (youtube.com)
            param(
                url="https://www.youtube.com/watch?v=DJxchZ7qAzE",
                json={"media": {"oembed": {}}},
                expected_url="https://www.youtube.com/watch?v=DJxchZ7qAzE",
            ),
            # youtube link (youtube.com)
            param(
                url="https://www.youtube.com/watch?v=DJxchZ7qAzE",
                json={
                    "media": {
                        "oembed": {
                            "url": "https://www.youtube.com/watch?v=DJxchZ7qAzE"
                        }
                    }
                },
                expected_url="https://www.youtube.com/watch?v=DJxchZ7qAzE",
            ),
        ]
    )
    def test_youtube(self, url, json, expected_url):
        """

        Parameters
        ----------
        url :
            
        json :
            
        expected_url :
            

        Returns
        -------

        """
        media = ServicesWrapper.get_media(url, json)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, ContentType.YOUTUBE)

    @parameterized.expand(
        [
            # imgur gif
            param(
                url="https://i.imgur.com/2WNMUqO.gifv",
                expected_url="https://i.imgur.com/2WNMUqO.mp4",
                expected_type=ContentType.VIDEO,
            )
        ]
    )
    def test_imgur(self, url, expected_url, expected_type):
        """

        Parameters
        ----------
        url :
            
        expected_url :
            
        expected_type :
            

        Returns
        -------

        """
        media = ServicesWrapper.get_media(url)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)

    @parameterized.expand(
        [
            # gfycat gif
            param(
                url="https://gfycat.com/HeartfeltHollowIberianchiffchaff",
                expected_url="https://giant.gfycat.com/HeartfeltHollowIberianchiffchaff.mp4",
                expected_type=ContentType.VIDEO,
            )
        ]
    )
    def test_gfycat(self, url, expected_url, expected_type):
        """

        Parameters
        ----------
        url :
            
        expected_url :
            
        expected_type :
            

        Returns
        -------

        """
        media = ServicesWrapper.get_media(url)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)

    @parameterized.expand(
        [
            # v.redd.it video
            param(
                url="https://v.redd.it/4phan5t9wq031",
                json={
                    "media": {
                        "reddit_video": {
                            "fallback_url": "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback"
                        }
                    }
                },
                expected_url="https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback",
                expected_type=ContentType.GIF,
            )
        ]
    )
    def test_vreddit(self, url, json, expected_url, expected_type):
        """

        Parameters
        ----------
        url :
            
        json :
            
        expected_url :
            
        expected_type :
            

        Returns
        -------

        """
        media = ServicesWrapper.get_media(url, json)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)

    @parameterized.expand(
        [
            # i.redd.it image
            param(
                url="https://i.redd.it/72tqh40xqr031.jpg",
                expected_url="https://i.redd.it/72tqh40xqr031.jpg",
                expected_type=ContentType.PHOTO,
            ),
            # i.redd.it gif
            param(
                url="https://i.redd.it/ao5s72l50r031.gif",
                expected_url="https://i.redd.it/ao5s72l50r031.gif",
                expected_type=ContentType.GIF,
            ),
        ]
    )
    def test_generic(self, url, expected_url, expected_type):
        """

        Parameters
        ----------
        url :
            
        expected_url :
            
        expected_type :
            

        Returns
        -------

        """
        media = ServicesWrapper.get_media(url)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)
