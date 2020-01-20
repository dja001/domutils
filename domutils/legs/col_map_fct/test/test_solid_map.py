import unittest
import numpy as np
import col_map_fct as map_fct


class TestStringMethods(unittest.TestCase):

    #testing solid_map class
    def test_solid_map_inc(self):
        map_obj = map_fct.solid_map(1.0,0.8,'<=','>=',[123,45,6])
        out_rgb = np.zeros([7,3],dtype='uint8')
        action_record = np.zeros(7)
        data =   np.array([.6, .7, .8, .9, 1., 1.1, 1.2])
        ans =  [ np.array([ 0., 0,  1,  1, 1,  0,   0]).tolist(),
                 [[  0,   0,   0],
                  [  0,   0,   0],
                  [123,  45,   6],
                  [123,  45,   6],
                  [123,  45,   6],
                  [  0,   0,   0],
                  [  0,   0,   0]] ]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(),
                    out_rgb.tolist()]
        self.assertEqual(ans, returned)

    def test_solid_map_noinc(self):
        map_obj = map_fct.solid_map(1.0,0.8,'<','>',[123,45,6])
        out_rgb = np.zeros([7,3],dtype='uint8')
        action_record = np.zeros(7)
        data =   np.array([.6, .7, .8, .9, 1., 1.1, 1.2])
        ans =  [ np.array([ 0., 0,  0,  1, 0,  0,   0]).tolist(),
                 [[  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [123,  45,   6],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0]] ]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(),
                    out_rgb.tolist()]
        self.assertEqual(ans, returned)


if __name__ == '__main__':
    unittest.main()
