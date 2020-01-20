import unittest
import col_utils
import numpy as np


class TestStringMethods(unittest.TestCase):

    #error testing for col_rgb
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
