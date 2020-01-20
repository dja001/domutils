import unittest
import numpy as np
import col_map_fct as map_fct
import validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing input_data   
    def test_input_data(self):
        with self.assertRaises(TypeError):
            data = ['a']
            validate.input_data(data)

    #testing exact_open_end class
    def test_exact_open_end_gt(self):
        map_obj = map_fct.exact_open_end(1.,'>')
        out_rgb = np.zeros([4,3])
        action_record = np.zeros(4)
        data = np.array([.7, .8, .9, 1.])
        ans =           [[ 0,  0,  0, 0], 0]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(), map_obj.bound_error]
        self.assertEqual(ans, returned)

    def test_exact_open_end_ge(self):
        map_obj = map_fct.exact_open_end(1.,'>=')
        out_rgb = np.zeros([4,3])
        action_record = np.zeros(4)
        data = np.array([.7, .8, .9, 1.])
        ans =           [[ 0,  0,  0, 0], 1]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(), map_obj.bound_error]
        self.assertEqual(ans, returned)

if __name__ == '__main__':
    unittest.main()
