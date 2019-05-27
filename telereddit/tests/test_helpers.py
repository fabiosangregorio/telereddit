import unittest
import helpers


class TestHelpers(unittest.TestCase):
    def test_get_subreddit_names(self):
        text = (
            "This is a text containing r/valid_subreddit_names and "
            "r/invalid_subreddit_names (too long).\nr/start_of_line and "
            "/r/CaseSensitive should work, but r/spec!ial characters "
            "r/shouldnotwork. r/numb3rs are r/permitted, r/_underscores too if "
            "they're not r/leading.")

        subreddits = [
            "r/valid_subreddit_names",
            "r/start_of_line",
            "r/CaseSensitive",
            "r/shouldnotwork",
            "r/numb3rs",
            "r/permitted",
            "r/leading"
        ]

        self.assertEqual(helpers.get_subreddit_names(text), subreddits)

        # subreddit in a link
        text = 'https://www.reddit.com/r/comics/comments/bia7qy/guess_i_love_dark_humor_oc'
        self.assertEqual(helpers.get_subreddit_names(text), ['r/comics'])
        self.assertNotEqual(helpers.get_subreddit_names(text), ['/r/comics'])

    def test_get_urls_from_text(self):
        text = 'https://redd.it/bqdlxe https://redd.it/bqekoq'
        urls = ['https://www.reddit.com/comments/bqdlxe.json',
                'https://www.reddit.com/comments/bqekoq.json']
        self.assertListEqual(helpers.get_urls_from_text(text), urls)

    def test_get(self):
        obj = {
            'with_value': 'ok',
            'with_true': True,
            'with_false': False,
            'with_obj': {'level_2': 'ok'},
            'with_empty_obj': {},
            'with_none': None
        }

        self.assertEqual(helpers.get(obj, 'with_value'), 'ok')
        self.assertEqual(helpers.get(obj, 'with_true'), True)
        self.assertEqual(helpers.get(obj, 'with_false'), False)
        self.assertEqual(helpers.get(obj, 'with_obj'), {'level_2': 'ok'})
        self.assertEqual(helpers.get(obj, 'with_empty_obj'), {})
        self.assertEqual(helpers.get(obj, 'with_none'), None)
        self.assertEqual(helpers.get(obj, 'with_none', {}), {})
        self.assertEqual(helpers.get(obj, 'not_in_obj'), None)

    def test_chained_get(self):
        obj = {
            'l1': {
                'l2_with_value': 'ok',
                'l2_with_none': None,
                'l2': {
                    'l3_with_value': 'ok'
                }
            }
        }

        self.assertEqual(helpers.chained_get(obj, ['l1', 'l2_with_value']), 'ok')
        self.assertEqual(helpers.chained_get(obj, ['l1', 'l2_with_none']), None)
        self.assertEqual(helpers.chained_get(obj, ['l1', 'l2']), {'l3_with_value': 'ok'})
        self.assertEqual(helpers.chained_get(obj, ['l1', 'l2', 'l3_with_value']), 'ok')
        self.assertEqual(helpers.chained_get(obj, ['l1', 'l3', 'l3_with_value']), None)
        self.assertEqual(helpers.chained_get(obj, ['l1', 'l3', 'l3_with_value'], {}), {})
