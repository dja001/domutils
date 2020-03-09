import unittest
import numpy as np
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing for range_arr parameter
    def test_range_arr_one_element(self):
        with self.assertRaises(ValueError):
            validate.range_arr(range_arr=[1.],n_col=1)

    def test_range_arr_incompatible_with_color_arr(self):
        with self.assertRaises(ValueError):
            validate.range_arr(range_arr=[1.,2.,3,4],n_col=2)

    def test_range_arr_unsorted(self):
        with self.assertRaises(ValueError):
            validate.range_arr(range_arr=[1.,3.,2.],n_col=2)

    def test_range_arr_wrong_type(self):
        with self.assertRaises(TypeError):
            validate.range_arr(range_arr=[2.,'a'],n_col=1)

    def test_range_arr_one_col(self):
        ans = np.array([3.,4.])
        range_lh = validate.range_arr(range_arr=[3,4],n_col=1)
        self.assertEqual(ans.tolist(),range_lh.tolist())

    def test_range_arr_four_col_no_range(self):
        ans = np.array([0.,.25,.5,.75,1.])
        range_lh = validate.range_arr(n_col=4)
        self.assertEqual(ans.tolist(),range_lh.tolist())

    def test_range_arr_four_col(self):
        ans = np.array([3.0, 3.25, 3.5, 3.75, 4.0])
        range_lh = validate.range_arr(range_arr=[3,4],n_col=4)
        self.assertEqual(ans.tolist(),range_lh.tolist())

    def test_range_arr_custom(self):
        ans = np.array([0.,1.,10.,100])
        range_lh = validate.range_arr(range_arr=ans,n_col=3)
        self.assertEqual(ans.tolist(),range_lh.tolist())


if __name__ == '__main__':
    unittest.main()
