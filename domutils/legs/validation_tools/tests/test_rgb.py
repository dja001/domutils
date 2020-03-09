import unittest
import domutils.legs.validation_tools as validate
import numpy as np


class TestStringMethods(unittest.TestCase):

    #testing rgb validation
    def test_rgb_not_number(self):
        with self.assertRaises(TypeError):
            validate.rgb([['a',81.0,237], [169,222,255]])
    
    def test_rgb_wrong_number(self):
        with self.assertRaises(ValueError):
            validate.rgb([[400,81.0,237], [169,222,255]])
    
    def test_rgb_impossible_RGB(self):
        with self.assertRaises(ValueError):
            validate.rgb([400,81.0,237,23])
    
    def test_rgb_good_number(self):
        ans = np.array([0,81,255],dtype='uint8')
        val = validate.rgb([0.0,81.27,255])
        self.assertEqual(val.tolist(),ans.tolist())

if __name__ == '__main__':
    unittest.main()
