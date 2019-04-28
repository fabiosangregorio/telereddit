import unittest
import reddit_linker
import helpers


class TestRedditLinker(unittest.TestCase):
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

    def test_get_post(self):
        # subreddit that doesn't exist
        json, _ = reddit_linker._get_post('r/n_o_t_a_n_a_m_e_i_h_ox_p_e')
        self.assertEqual(json, None)

        # private subreddit
        json, _ = reddit_linker._get_post('r/CenturyClub/')
        self.assertEqual(json, None)

        # valid subreddit
        _, err_msg = reddit_linker._get_post('r/funny')
        self.assertEqual(err_msg, None)
