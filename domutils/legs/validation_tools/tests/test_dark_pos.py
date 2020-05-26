import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing for dark_pos parameter
    def test_dark_pos_wrong_string(self):
        with self.assertRaises(ValueError):
            validate.dark_pos(dark_pos='hello',n_col=1)

    def test_dark_pos_mixed_list(self):
        with self.assertRaises(TypeError):
            validate.dark_pos(dark_pos=['high',2],n_col=1)

    def test_dark_pos_mixed_list_2(self):
        with self.assertRaises(ValueError):
            validate.dark_pos(dark_pos=['high','blue'],n_col=1)

    def test_dark_pos_too_many_elements(self):
        with self.assertRaises(ValueError):
            validate.dark_pos(dark_pos=['high','low'],n_col=1)

    def test_dark_pos_wrong_type(self):
        with self.assertRaises(TypeError):
            validate.dark_pos(dark_pos=2,n_col=1)

    def test_dark_pos_ind_return(self):
        ans = [False,True,True,False,False]
        dark_flip = validate.dark_pos(dark_pos=['high','low','low','high','high'],n_col=5)
        self.assertEqual(ans,dark_flip)

    def test_dark_pos_ind_return_high(self):
        ans = [False,False,False,False,False]
        dark_flip = validate.dark_pos(dark_pos='high',n_col=5)
        self.assertEqual(ans,dark_flip)

    def test_dark_pos_ind_return_low(self):
        ans = [True,True,True]
        dark_flip = validate.dark_pos(dark_pos='low',n_col=3)
        self.assertEqual(ans,dark_flip)


if __name__ == '__main__':
    unittest.main()
