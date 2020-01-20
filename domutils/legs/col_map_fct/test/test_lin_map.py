import unittest
import numpy as np
import col_map_fct as map_fct
import validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing lin_map class
    def test_lin_map_inc(self):
        map_obj = map_fct.lin_map(1.0,0.8,'<=','>=',[255,255,255],[10,10,10])
        out_rgb = np.zeros([7,3],dtype='uint8')
        action_record = np.zeros(7)
        data =   np.array([.6, .7, .8, .9, 1., 1.1, 1.2])
        ans =  [ np.array([ 0., 0,  1,  1, 1,  0,   0]).tolist(),
                 [[  0,   0,   0],
                  [  0,   0,   0],
                  [ 10,  10,  10],
                  [132, 132, 132],
                  [255, 255, 255],
                  [  0,   0,   0],
                  [  0,   0,   0]] ]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(),
                    out_rgb.tolist()]
        self.assertEqual(ans, returned)

    def test_lin_map_noinc(self):
        map_obj = map_fct.lin_map(1.0,0.8,'<','>',[255,255,255],[10,10,10])
        out_rgb = np.zeros([7,3],dtype='uint8')
        action_record = np.zeros(7)
        data =   np.array([.6, .7, .8, .9, 1., 1.1, 1.2])
        ans =  [ np.array([ 0., 0,  0,  1, 0,  0,   0]).tolist(),
                 [[  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [132, 132, 132],
                  [  0,   0,   0],
                  [  0,   0,   0],
                  [  0,   0,   0]] ]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(),
                    out_rgb.tolist()]
        self.assertEqual(ans, returned)

if __name__ == '__main__':
    unittest.main()
