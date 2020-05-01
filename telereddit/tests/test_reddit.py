import unittest
from unittest.mock import patch
import telereddit.reddit as reddit
import json
import pathlib

from telereddit.models.exceptions import (
    SubredditDoesntExistError,
    SubredditPrivateError,
)

from telereddit.content_type import ContentType


class TestReddit(unittest.TestCase):
    """ """
    @patch("telereddit.reddit.requests.get")
    def test_get_json_404(self, mock_get):
        """

        Parameters
        ----------
        mock_get :
            

        Returns
        -------

        """
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
        """

        Parameters
        ----------
        mock_get :
            

        Returns
        -------

        """
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
        """

        Parameters
        ----------
        mock_get :
            

        Returns
        -------

        """
        with open(
            pathlib.Path(__file__).parent
            / "json/r-funny-my_weather_app_nailed_it_today.json"
        ) as f:
            mock_json = json.load(f)
        mock_get.return_value.ok = True
        mock_get.return_value.json = lambda: mock_json
        mock_get.return_value.status_code = 200

        json_data = reddit._get_json(
            "https://www.reddit.com/r/funny/comments/fxuefa/my_weather_app_nailed_it_today.json"
        )
        self.assertEqual(json_data, mock_json[0])

    # def test_get_post(self):
    #     # text post
    #     post, status, err_msg = reddit.get_post('r/showerthoughts')
    #     self.assertEqual(status, 'success')
    #     self.assertIsNone(err_msg)
    #     self.assertEqual(post.subreddit.lower(), 'r/showerthoughts')
    #     self.assertIsNotNone(post.title)
    #     self.assertIn('https://www.reddit.com/r/showerthoughts', post.get_msg().lower())
    #     self.assertEqual(post.get_type(), ContentType.TEXT)

    #     # photo post
    #     post, status, err_msg = reddit.get_post('r/pics')
    #     self.assertEqual(status, 'success')
    #     self.assertIsNone(err_msg)
    #     self.assertEqual(post.subreddit.lower(), 'r/pics')
    #     self.assertIsNotNone(post.title)
    #     self.assertIn('https://www.reddit.com/r/pics', post.get_msg().lower())
    #     self.assertIsNotNone(post.media.url)
    #     self.assertEqual(post.get_type(), ContentType.PHOTO)

    #     # crosspost
    #     post, status, err_msg = reddit.get_post(post_url='https://www.reddit.com/r/bicycling/comments/aevkgj/finally_know_how_to_crosspost/')
    #     self.assertEqual(status, 'success')
    #     self.assertIsNone(err_msg)
    #     self.assertEqual(post.subreddit.lower(), 'r/bicycling')
    #     self.assertIsNotNone(post.title)
    #     self.assertIn('https://www.reddit.com/r/bicycling', post.get_msg().lower())
    #     self.assertIsNotNone(post.media.url)
    #     self.assertEqual(post.get_type(), ContentType.PHOTO)
