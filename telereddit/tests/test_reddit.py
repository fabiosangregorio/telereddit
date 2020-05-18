import unittest
from unittest.mock import patch
import telereddit.reddit as reddit
import json
import pathlib
from parameterized import parameterized, param

from telereddit.exceptions import (
    SubredditDoesntExistError,
    SubredditPrivateError,
)

from telereddit.models.content_type import ContentType
from telereddit.models.post import Post
from telereddit.models.media import Media


class TestReddit(unittest.TestCase):
    def _get_json(self, filename):
        with open(pathlib.Path(__file__).parent / "json" / filename) as f:
            return json.load(f)

    @patch("telereddit.reddit.requests.get")
    def test_get_json_404(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.json = lambda: {
            "message": "Not Found",
            "error": 404,
        }
        mock_get.return_value.status_code = 404
        self.assertRaises(
            SubredditDoesntExistError,
            reddit._get_json,
            "https://reddit.com/r/n_o_t_a_n_a_m_e_i_h_ox_p_e/random",
        )

    @patch("telereddit.reddit.requests.get")
    def test_get_json_private(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.json = lambda: {
            "reason": "private",
            "message": "Forbidden",
            "error": 403,
        }
        mock_get.return_value.status_code = 403
        self.assertRaises(
            SubredditPrivateError,
            reddit._get_json,
            "https://reddit.com/r/n_o_t_a_n_a_m_e_i_h_ox_p_e/random",
        )

    @patch("telereddit.reddit.requests.get")
    def test_get_json_valid(self, mock_get):
        mock_json = self._get_json(
            "r-funny-my_weather_app_nailed_it_today.json"
        )
        mock_get.return_value.ok = True
        mock_get.return_value.json = lambda: mock_json
        mock_get.return_value.status_code = 200

        json_data = reddit._get_json(
            "https://www.reddit.com/r/funny/comments/fxuefa/my_weather_app_nailed_it_today.json"
        )
        self.assertEqual(json_data, mock_json[0])

    @parameterized.expand(
        [
            # text post
            param(
                subreddit="r/showerthoughts",
                mock_json_filename="showerthoughts-text_post.json",
                expected=Post(
                    subreddit="r/Showerthoughts",
                    permalink="/r/Showerthoughts/comments/gjpq1t/we_will_be_slaves_to_our_dental_health_for_the/",
                    title="We will be slaves to our dental health for the rest of our lives.",
                    text="",
                ),
            ),
            # photo post
            param(
                subreddit="r/pics",
                mock_json_filename="pics-photo_post.json",
                expected=Post(
                    subreddit="r/pics",
                    permalink="/r/pics/comments/gjm3ik/hadnt_drawn_for_10_years_pre_lockdown_this_is_my/",
                    title="Hadn't drawn for 10 years pre lockdown. This is my 2nd piece during lockdown. Pencil on paper.",
                    text="",
                ),
            ),
            # crosspost
            param(
                subreddit="r/bicycling",
                mock_json_filename="bicycling_crosspost.json",
                expected=Post(
                    subreddit="r/bicycling",
                    permalink="/r/bicycling/comments/aevkgj/finally_know_how_to_crosspost/",
                    title="Finally know how to crosspost",
                    text="",
                ),
            ),
        ]
    )
    @patch("telereddit.reddit._get_json")
    @patch("telereddit.services.services_wrapper.ServicesWrapper.get_media")
    def test_get_post(
        self,
        mock_get_media,
        mock_get_json,
        subreddit,
        mock_json_filename,
        expected,
    ):
        mock_get_json.return_value = self._get_json(mock_json_filename)[0]
        mock_get_media.return_value = Media("", ContentType.PHOTO)
        post = reddit.get_post(subreddit)

        # self.assertEqual(post, expected)
        self.assertEqual(post.subreddit, expected.subreddit)
        self.assertEqual(post.permalink, expected.permalink)
        self.assertEqual(post.title, expected.title)
        self.assertEqual(post.text, expected.text)
