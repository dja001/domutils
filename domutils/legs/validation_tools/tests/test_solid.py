import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing for "solid" parameter
    def test_solid_alone(self):
        with self.assertRaises(ValueError):
            validate.color_arr_and_solid(solid='dum',color_arr=None)

    def test_solid_invalid(self):
        with self.assertRaises(ValueError):
            validate.color_arr_and_solid(solid='invalid_string',color_arr='dummy')

    def test_solid_not_a_string(self):
        with self.assertRaises(TypeError):
            validate.color_arr_and_solid(solid=2,color_arr='dummy')


if __name__ == '__main__':
    unittest.main()
