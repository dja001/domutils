import unittest
import domutils.legs.col_utils as col_utils
import numpy as np


class TestStringMethods(unittest.TestCase):

    #error testing for col_pair
    def test_col_pair_wrong_col(self):
        with self.assertRaises(ValueError):
            col_txt='non_existing_col'
            col_utils.col_pair(col_txt)

    def test_col_pair_b_w(self):
        self.assertEqual(col_utils.col_pair('b_w').tolist(), [[255,255,255],[0,0,0]])

    def test_col_pair_blue(self):
        self.assertEqual(col_utils.col_pair('blue').tolist(), [[169,222,255], [0,81,237]])

    def test_col_pair_good_col_multi(self):
        col_txt=['blue', 'red','b_w']
        self.assertEqual(col_utils.col_pair(col_txt).tolist(), [[[169,222,255],[0,   81,237]],
                                                                [[255,190,187],[158,  0, 13]],
                                                                [[255,255,255],[  0,  0,  0]]])

    def test_col_rgb_wrong_col(self):
        with self.assertRaises(ValueError):
            col_utils.col_rgb('non_existing_col')

    def test_col_rgb_partial_match(self):
        with self.assertRaises(ValueError):
            col_utils.col_rgb('dark_')

    def test_col_rgb_good_col(self):
        self.assertEqual(col_utils.col_rgb('white').tolist(), [255,255,255])

    def test_col_rgb_good_col_multi(self):
        self.assertEqual(col_utils.col_rgb(['white', 'black']).tolist(), [[255,255,255],[0,0,0]])

    def test_col_rgb_bad_col_multi(self):
        with self.assertRaises(ValueError):
            map0 = col_utils.col_rgb(['white', 'bad'])

if __name__ == '__main__':
    unittest.main()
