import unittest
from parameterized import parameterized, param

from telereddit.models.post import Post
from telereddit.models.media import Media
from telereddit.models.content_type import ContentType


class TestPost(unittest.TestCase):
    def test_get_msg(self):
        post = Post("r/subreddit", "https://permalink", "title", "text")
        msg = post.get_msg()

        self.assertIn("r/subreddit", msg)
        self.assertIn("https://permalink", msg)
        self.assertIn("title", msg)
        self.assertIn("text", msg)

    @parameterized.expand(
        [
            param(
                media=Media("", ContentType.VIDEO), expected=ContentType.VIDEO
            ),
            param(
                media=Media("", ContentType.PHOTO), expected=ContentType.PHOTO
            ),
            param(
                media=Media("", ContentType.YOUTUBE),
                expected=ContentType.YOUTUBE,
            ),
            param(media=None, expected=ContentType.TEXT),
        ]
    )
    def test_get_type(self, media, expected):
        post = Post("", "", "", "", media)
        self.assertEqual(post.get_type(), expected)
