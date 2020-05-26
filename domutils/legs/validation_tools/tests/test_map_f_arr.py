import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #map_f_arr parameter
    def test_map_f_arr_mixed_type(self):
        with self.assertRaises(TypeError):
            validate.map_f_arr(map_f_arr=['bla',3],n_col=2)

    def test_map_f_arr_wrong_number(self):
        with self.assertRaises(ValueError):
            validate.map_f_arr(map_f_arr=['bla','blo'],n_col=1)

    def test_map_f_arr_wrong_type(self):
        with self.assertRaises(TypeError):
            validate.map_f_arr(map_f_arr=3)

    def test_map_f_arr_default(self):
        ans = ['linmap','linmap','linmap']
        map_f_arr = validate.map_f_arr(n_col=3)
        self.assertEqual(ans,map_f_arr)

    def test_map_f_arr_default_solid(self):
        ans = ['within','within','within']
        map_f_arr = validate.map_f_arr(n_col=3,solid='supplied')
        self.assertEqual(ans,map_f_arr)

    def test_map_f_arr_default_custom(self):
        ans = ['linmap','within','custom']
        map_f_arr = validate.map_f_arr(map_f_arr = ans, n_col=3)
        self.assertEqual(ans,map_f_arr)

    def test_map_f_arr_custom_auto(self):
        ans = ['custom','custom','custom']
        map_f_arr = validate.map_f_arr(map_f_arr = 'custom', n_col=3)
        self.assertEqual(ans,map_f_arr)

if __name__ == '__main__':
    unittest.main()
