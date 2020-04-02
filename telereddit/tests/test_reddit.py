import unittest
import reddit

from content_type import ContentType


class TestReddit(unittest.TestCase):
    def test_get_json(self):
        # subreddit that doesn't exist
        json, _ = reddit._get_json('r/n_o_t_a_n_a_m_e_i_h_ox_p_e')
        self.assertEqual(json, None)

        # private subreddit
        json, _ = reddit._get_json('r/CenturyClub/')
        self.assertEqual(json, None)

        # valid subreddit
        json, _ = reddit._get_json('r/funny')
        self.assertNotEqual(json, None)

    def test_get_post(self):
        # text post
        post, status, err_msg = reddit.get_post('r/showerthoughts')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/showerthoughts')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/showerthoughts', post.get_msg().lower())
        self.assertEqual(post.get_type(), ContentType.TEXT)

        # photo post
        post, status, err_msg = reddit.get_post('r/pics')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/pics')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/pics', post.get_msg().lower())
        self.assertIsNotNone(post.media.url)
        self.assertEqual(post.get_type(), ContentType.PHOTO)

        # crosspost
        post, status, err_msg = reddit.get_post(post_url='https://www.reddit.com/r/bicycling/comments/aevkgj/finally_know_how_to_crosspost/')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/bicycling')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/bicycling', post.get_msg().lower())
        self.assertIsNotNone(post.media.url)
        self.assertEqual(post.get_type(), ContentType.PHOTO)
