import unittest
from parameterized import parameterized, param

import telereddit.helpers as helpers


class TestHelpers(unittest.TestCase):
    def test_get_random_post_url(self):
        self.assertEqual(
            helpers.get_random_post_url("r/gifs"),
            "https://www.reddit.com/r/gifs/random",
        )

    def test_get_random_post_url_invalid(self):
        with self.assertRaises(Exception):
            helpers.get_random_post_url()

    @parameterized.expand(
        [
            # subreddit in a text
            param(
                text=(
                    "This is a text containing r/valid_subreddit_names."
                    "\nr/start_of_line and /r/CaseSensitive should work. "
                    "r/numb3rs are r/permitted. /r/subreddit should also work. "
                    "Also urls http://containing.com/a_leading_r/shouldnotwork."
                ),
                expected=[
                    "r/valid_subreddit_names",
                    "r/start_of_line",
                    "r/CaseSensitive",
                    "r/numb3rs",
                    "r/permitted",
                    "r/subreddit",
                ],
            ),
            # subreddit in a link
            param(
                text="https://www.reddit.com/r/comics/comments/bia7qy/guess_i_love_dark_humor_oc",
                expected=["r/comics"],
                not_expected=["/r/comics"],
            ),
        ]
    )
    def test_get_subreddit_names_valid(self, text, expected, not_expected=None):
        self.assertEqual(helpers.get_subreddit_names(text), expected)
        self.assertNotEqual(helpers.get_subreddit_names(text), not_expected)

    @parameterized.expand(
        [
            param(
                text=(
                    "r/invalid_subreddit_names (too long), r/spec!ial "
                    "characters and leading r/_underscores should not work."
                )
            )
        ]
    )
    def test_get_subreddit_names_notvalid(self, text):
        self.assertEqual(helpers.get_subreddit_names(text), [])

    @parameterized.expand(
        [
            param(
                text="r/subreddit_one and r/subreddit_two",
                expected="r/subreddit_one",
            ),
            param(
                text="r/subreddit_one and r/subreddit_two",
                expected="r/subreddit_two",
                reverse=True,
            ),
            param(
                text="r/subreddit_one",
                expected="r/subreddit_one",
            ),
            param(
                text="r/subreddit_one", reverse=True, expected="r/subreddit_one"
            ),
        ]
    )
    def test_get_subreddit_name(self, text, expected, reverse=False):
        self.assertEqual(helpers.get_subreddit_name(text, reverse), expected)

    def test_get_subreddit_name_invalid(self):
        with self.assertRaises(Exception):
            helpers.get_subreddit_name("")

    @parameterized.expand(
        [
            param(text="truncate me", length=7, expected="truncat..."),
            param(text="truncate me", length=11, expected="truncate me"),
            param(text="", length=10, expected=""),
        ]
    )
    def test_truncate_text(self, text, length, expected):
        self.assertEqual(helpers.truncate_text(text, length), expected)

    def test_truncate_invalid(self):
        with self.assertRaises(Exception):
            helpers.truncate_text("", 0)

    @parameterized.expand(
        [
            param(text="", expected=""),
            param(text="no newlines", expected="no newlines"),
            param(text="with\nnewlines", expected="with newlines"),
            param(
                text="with \\n escaped newlines",
                expected="with n escaped newlines",
            ),
        ]
    )
    def polish_text(self, text, expected):
        self.assertEqual(helpers.polish_text(text), expected)

    @parameterized.expand(
        [
            param(
                text=(
                    "https://redd.it/bqdlxe "
                    "https://www.reddit.com/comments/bqekoq "
                    "https://reddit.app.link/coCUmdItLX https://google.com"
                ),
                expected=[
                    "https://www.reddit.com/comments/bqdlxe",
                    "https://www.reddit.com/comments/bqekoq",
                    "https://www.reddit.com/r/tumblr/comments/c42tf6/woah",
                ],
            ),
            param(text="https://reddit.app.link/invalid_url", expected=[]),
        ]
    )
    def test_get_urls_from_text(self, text, expected, not_expected=None):
        self.assertListEqual(helpers.get_urls_from_text(text), expected)

    def test_get(self):
        obj = {
            "with_value": "ok",
            "with_true": True,
            "with_false": False,
            "with_obj": {"level_2": "ok"},
            "with_empty_obj": {},
            "with_none": None,
        }

        self.assertEqual(helpers.get(obj, "with_value"), "ok")
        self.assertEqual(helpers.get(obj, "with_true"), True)
        self.assertEqual(helpers.get(obj, "with_false"), False)
        self.assertEqual(helpers.get(obj, "with_obj"), {"level_2": "ok"})
        self.assertEqual(helpers.get(obj, "with_empty_obj"), {})
        self.assertEqual(helpers.get(obj, "with_none"), None)
        self.assertEqual(helpers.get(obj, "with_none", {}), {})
        self.assertEqual(helpers.get(obj, "not_in_obj"), None)

    def test_chained_get(self):
        obj = {
            "l1": {
                "l2_with_value": "ok",
                "l2_with_none": None,
                "l2": {"l3_with_value": "ok"},
            }
        }

        self.assertEqual(
            helpers.chained_get(obj, ["l1", "l2_with_value"]), "ok"
        )
        self.assertEqual(helpers.chained_get(obj, ["l1", "l2_with_none"]), None)
        self.assertEqual(
            helpers.chained_get(obj, ["l1", "l2"]), {"l3_with_value": "ok"}
        )
        self.assertEqual(
            helpers.chained_get(obj, ["l1", "l2", "l3_with_value"]), "ok"
        )
        self.assertEqual(
            helpers.chained_get(obj, ["l1", "l3", "l3_with_value"]), None
        )
        self.assertEqual(
            helpers.chained_get(obj, ["l1", "l3", "l3_with_value"], {}), {}
        )
