import unittest
from parameterized import parameterized, param
from unittest.mock import patch

from telereddit.services.services_wrapper import ServicesWrapper
from telereddit.models.content_type import ContentType
from telereddit.services.gfycat_service import Gfycat

from telereddit.exceptions import AuthenticationError, MediaRetrievalError


class TestServices(unittest.TestCase):
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
            ),
            # imgur image
            param(
                url="https://imgur.com/gallery/YfsGJtb",
                expected_url="https://i.imgur.com/wHx7Rd0.jpg",
                expected_type=ContentType.PHOTO,
            ),
        ]
    )
    def test_imgur(self, url, expected_url, expected_type):
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
            ),
            # gfycat 35mb gif
            param(
                url="https://gfycat.com/agitateddimcarp",
                expected_url="https://thumbs.gfycat.com/AgitatedDimCarp-size_restricted.gif",
                expected_type=ContentType.GIF,
            ),
        ]
    )
    def test_gfycat(self, url, expected_url, expected_type):
        media = ServicesWrapper.get_media(url)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)

    @parameterized.expand(
        [
            # v.redd.it video
            param(
                url="https://v.redd.it/w3ywnv3l94a31",
                json={
                    "media": {
                        "reddit_video": {
                            "fallback_url": "https://v.redd.it/w3ywnv3l94a31/DASH_360?source=fallback"
                        }
                    }
                },
                expected_url="https://v.redd.it/w3ywnv3l94a31/DASH_360?source=fallback",
                expected_type=ContentType.GIF,
            ),
            # crossspost v.redd.it gif
            param(
                url="https://v.redd.it/dvx5rzrnp8k41",
                json={
                    "crosspost_parent_list": [
                        {
                            "secure_media": {
                                "reddit_video": {
                                    "fallback_url": "https://v.redd.it/dvx5rzrnp8k41/DASH_720?source=fallback"
                                }
                            }
                        }
                    ]
                },
                expected_url="https://v.redd.it/dvx5rzrnp8k41/DASH_720?source=fallback",
                expected_type=ContentType.GIF,
            ),
        ]
    )
    def test_vreddit(self, url, json, expected_url, expected_type):
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
        media = ServicesWrapper.get_media(url)
        self.assertEqual(media.url, expected_url)
        self.assertEqual(media.type, expected_type)

    @patch("telereddit.services.gfycat_service.requests.post")
    def test_gfycat_authentication_fail(self, mock_post):
        mock_post.return_value.status_code = 401

        with self.assertRaises(AuthenticationError):
            Gfycat()

    @patch("telereddit.services.gfycat_service.requests.get")
    def test_gfycat_post_fail(self, mock_get):
        mock_get.return_value.status_code = 401

        gfycat = Gfycat()
        with self.assertRaises(MediaRetrievalError):
            gfycat.get_media(
                "https://gfycat.com/dimpledsorrowfulalaskajingle", {}
            )
