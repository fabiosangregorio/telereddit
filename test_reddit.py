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
