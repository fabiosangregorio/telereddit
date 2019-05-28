import unittest
import reddit


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

    def test_get_media(self):
        # i.redd.it image
        type, url = reddit._get_media("https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(url, "https://i.redd.it/72tqh40xqr031.jpg")
        self.assertEqual(type, 'photo')

        # v.redd.it video
        type, url = reddit._get_media("https://v.redd.it/4phan5t9wq031",
                                      "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback")
        self.assertEqual(url, "https://v.redd.it/4phan5t9wq031/DASH_1080?source=fallback")
        self.assertEqual(type, 'gif')

        # i.redd.it gif
        type, url = reddit._get_media("https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(url, "https://i.redd.it/ao5s72l50r031.gif")
        self.assertEqual(type, 'gif')

        # imgur gif
        type, url = reddit._get_media("https://i.imgur.com/2WNMUqO.gifv")
        self.assertEqual(url, "https://imgur.com/download/2WNMUqO")
        self.assertEqual(type, 'gif')

        # gfycat gif
        type, url = reddit._get_media("https://gfycat.com/HeartfeltHollowIberianchiffchaff")
        self.assertEqual(url, "https://thumbs.gfycat.com/HeartfeltHollowIberianchiffchaff-size_restricted.gif")
        self.assertEqual(type, 'gif')

    def test_get_post(self):
        # text post
        post, status, err_msg = reddit.get_post('r/showerthoughts')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/showerthoughts')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/showerthoughts', post.footer)
        self.assertEqual(post.type, 'text')

        # photo post
        post, status, err_msg = reddit.get_post('r/pics')
        self.assertEqual(status, 'success')
        self.assertIsNone(err_msg)
        self.assertEqual(post.subreddit.lower(), 'r/pics')
        self.assertIsNotNone(post.title)
        self.assertIn('https://www.reddit.com/r/pics', post.footer)
        self.assertIsNotNone(post.media_url)
        self.assertEqual(post.type, 'photo')
