import unittest
import numpy as np
import domutils.legs.col_map_fct as col_map_fct
import domutils.legs.validation_tools as validation_tools


class TestStringMethods(unittest.TestCase):

    def test_input_data(self):
        with self.assertRaises(TypeError):
            data = ['a']
            validation_tools.input_data(data)

    def test_exact_open_end_gt(self):
        map_obj = col_map_fct.exact_open_end(1.,'>')
        out_rgb = np.zeros([4,3])
        action_record = np.zeros(4)
        data = np.array([.7, .8, .9, 1.])
        ans =           [[ 0,  0,  0, 0], 0]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(), map_obj.bound_error]
        self.assertEqual(ans, returned)

    def test_exact_open_end_ge(self):
        map_obj = col_map_fct.exact_open_end(1.,'>=')
        out_rgb = np.zeros([4,3])
        action_record = np.zeros(4)
        data = np.array([.7, .8, .9, 1.])
        ans =           [[ 0,  0,  0, 0], 1]
        map_obj.map(data, out_rgb, action_record)
        returned = [action_record.tolist(), map_obj.bound_error]
        self.assertEqual(ans, returned)

    def test_extend_open_end_gt(self):
        map_obj = col_map_fct.extend_open_end(1.,'>',[237,123,42])
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

    def test_lin_map_inc(self):
        map_obj = col_map_fct.lin_map(1.0,0.8,'<=','>=',[255,255,255],[10,10,10])
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
        map_obj = col_map_fct.lin_map(1.0,0.8,'<','>',[255,255,255],[10,10,10])
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

    def test_solid_map_inc(self):
        map_obj = col_map_fct.solid_map(1.0,0.8,'<=','>=',[123,45,6])
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
        map_obj = col_map_fct.solid_map(1.0,0.8,'<','>',[123,45,6])
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
