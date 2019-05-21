import unittest
import helpers


class TestHelpers(unittest.TestCase):
    def test_get_urls_from_text(self):
        text = 'https://redd.it/bqdlxe https://redd.it/bqekoq'
        urls = ['https://www.reddit.com/comments/bqdlxe.json', 
                'https://www.reddit.com/comments/bqekoq.json']
        self.assertListEqual(helpers.get_urls_from_text(text), urls)