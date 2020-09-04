import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized


from telereddit.linker import Linker
from telereddit.exceptions import (
    TeleredditError,
    PostEqualsMessageError,
)
from pyreddit.pyreddit.exceptions import SubredditError
from pyreddit.pyreddit.models.post import Post
from pyreddit.pyreddit.models.media import Media
from pyreddit.pyreddit.models.content_type import ContentType
from telereddit.config.config import MAX_MEDIA_SIZE


class TestLinker(unittest.TestCase):
    Linker.set_bot(Mock())
    linker = Linker(0)

    def test_bot_not_none(self):
        self.assertIsNotNone(self.linker.bot)

    def test_get_args(self):
        args = self.linker.get_args()
        self.assertIn("chat_id", args)
        self.assertTrue(args["chat_id"] == 0)

    def test_get_args_override(self):
        self.assertIn("test", self.linker.get_args({"test": True}))

    @patch("telereddit.linker.Linker.send_post")
    @patch("telereddit.linker.Linker._send_exception_message")
    def test_send_random_post(self, mock_err_function, mock_send_post):
        self.linker.send_random_post("r/valid")
        mock_err_function.assert_not_called()

    @patch("telereddit.linker.Linker.send_post")
    @patch("telereddit.linker.Linker._send_exception_message")
    def test_send_random_post_invalid(self, mock_err_function, mock_send_post):
        mock_send_post.side_effect = TeleredditError("")
        self.linker.send_random_post("r/invalid")
        mock_err_function.assert_called()

        mock_send_post.side_effect = SubredditError("")
        self.linker.send_random_post("r/invalid")
        mock_err_function.assert_called()

    @patch("telereddit.linker.Linker.send_post")
    @patch("telereddit.linker.Linker._send_exception_message")
    def test_send_post_from_url(self, mock_err_function, mock_send_post):
        self.linker.send_post_from_url("r/valid")
        mock_err_function.assert_not_called()

    @patch("telereddit.linker.Linker.send_post")
    @patch("telereddit.linker.Linker._send_exception_message")
    def test_send_post_from_url_invalid(
        self, mock_err_function, mock_send_post
    ):
        mock_send_post.side_effect = TeleredditError("")
        self.linker.send_post_from_url("")
        mock_err_function.assert_called()

    @parameterized.expand(
        [
            [ContentType.PHOTO],
            [ContentType.GIF],
            [ContentType.VIDEO],
            [ContentType.YOUTUBE],
            [ContentType.TEXT],
        ]
    )
    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post(self, mock_content_type, mock_get_post):
        media = Media("", mock_content_type)
        mock_get_post.return_value = Post("", "", "", "", media)
        self.linker.send_post("")

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post_no_type(self, mock_get_post):
        media = Media("", None)
        mock_get_post.return_value = Post("", "", "", "", media)
        self.linker.send_post("")

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post_from_url_true(self, mock_get_post):
        media = Media("", ContentType.PHOTO)
        mock_get_post.return_value = Post("", "", "", "", media)
        self.linker.send_post("", from_url=True)

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post_invalid(self, mock_get_post):
        mock_get_post.side_effect = TeleredditError("")
        with self.assertRaises(TeleredditError):
            self.linker.send_post("")

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post_media_too_big(self, mock_get_post):
        media = Media("", ContentType.PHOTO, size=MAX_MEDIA_SIZE + 1)
        mock_get_post.return_value = Post("", "", "", "", media)
        with self.assertRaises(TeleredditError):
            self.linker.send_post("")

    @patch("telereddit.linker.Linker.bot.sendMessage")
    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_send_post_err(self, mock_get_post, mock_send_message):
        mock_send_message.side_effect = TeleredditError("")
        media = Media("", ContentType.TEXT)
        mock_get_post.return_value = Post("", "", "", "", media)
        with self.assertRaises(TeleredditError):
            self.linker.send_post("")

    def test_edit_result_none(self):
        mock_msg = Mock()
        mock_msg.text = ""
        mock_msg.caption = ""
        self.linker.edit_result(mock_msg)

    @patch("telereddit.linker.Linker.edit_random_post")
    def test_edit_result(self, mock_edit_random_post):
        mock_msg = Mock()
        mock_msg.text = "r/funny"
        mock_msg.caption = ""
        self.linker.edit_result(mock_msg)

    @patch("telereddit.linker.Linker.edit_random_post")
    def test_edit_result_invalid(self, mock_edit_random_post):
        mock_edit_random_post.side_effect = TeleredditError("")
        mock_msg = Mock()
        mock_msg.text = "r/funny"
        mock_msg.caption = ""
        self.linker.edit_result(mock_msg)

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_edit_random_post_text(self, mock_get_post):
        media = Media("", ContentType.TEXT)
        mock_get_post.return_value = Post("", "", "", "", media)
        mock_msg = Mock()
        mock_msg.text = ""
        mock_msg.caption = None
        self.linker.edit_random_post(mock_msg, "r/test")

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_edit_random_post_invalid(self, mock_get_post):
        media = Media("", ContentType.TEXT)
        mock_get_post.return_value = Post("", "", "", "", media)
        mock_msg = Mock()
        mock_msg.text = None
        mock_msg.caption = ""
        with self.assertRaises(PostEqualsMessageError):
            self.linker.edit_random_post(mock_msg, "r/test")

    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_edit_random_post_youtube(self, mock_get_post):
        media = Media("", ContentType.YOUTUBE)
        mock_get_post.return_value = Post("", "", "", "", media)
        mock_msg = Mock()
        mock_msg.text = ""
        mock_msg.caption = None
        mock_msg.caption_markdown = ""
        self.linker.edit_random_post(mock_msg, "r/test")

    @parameterized.expand(
        [[ContentType.PHOTO], [ContentType.GIF], [ContentType.VIDEO]]
    )
    @patch("pyreddit.pyreddit.reddit.get_post")
    def test_edit_random_post_types(self, mock_type, mock_get_post):
        media = Media("", mock_type)
        mock_get_post.return_value = Post("", "", "", "", media)
        mock_msg = Mock()
        mock_msg.text = None
        mock_msg.caption = ""
        mock_msg.caption_markdown = ""
        self.linker.edit_random_post(mock_msg, "r/test")

    @patch("telereddit.linker.Linker.bot.sendMessage")
    def test_send_exception_message(self, mock_send_message):
        e = Mock()
        self.linker._send_exception_message(e)

    @patch("telereddit.linker.Linker.bot.sendMessage")
    def test_send_exception_message_no_kb(self, mock_send_message):
        e = Mock()
        self.linker._send_exception_message(e, False)
