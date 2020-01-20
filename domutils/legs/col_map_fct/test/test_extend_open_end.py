import unittest
import numpy as np
import col_map_fct as map_fct


class TestStringMethods(unittest.TestCase):

    #testing extend_open_end class
    def test_extend_open_end_gt(self):
        map_obj = map_fct.extend_open_end(1.,'>',[237,123,42])
        out_rgb = np.zeros([6,3])
        action_record = np.zeros(6)
        data =   np.array([.7, .8, .9, 1., 1.1, 1.2])
        ans =  [ np.array([ 0., 0,  0, 0,  1,   1]).tolist(),
                 [[  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [237, 123,  42],
                  [237, 123,  42]] ]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(),
                    out_rgb.tolist()]
        self.assertEqual(ans, returned)

if __name__ == '__main__':
    unittest.main()
