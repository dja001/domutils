import unittest
import numpy as np
import domutils.legs.col_utils
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing for exception values
    def test_excep_val_wrong_type(self):
        with self.assertRaises(TypeError):
            excep_val='a'
            validate.exceptions(excep_val=excep_val)

    def test_excep_val_one_element(self):
        #exceptions keywords
        (n_excep, 
         excep_val_np, 
         excep_tol_np, 
         excep_col_rgb) = validate.exceptions(excep_val=1.)
        ans = np.array([1.])
        self.assertEqual(ans.tolist(),excep_val_np.tolist())

    def test_excep_tol_wrong_type(self):
        with self.assertRaises(TypeError):
            excep_val=1
            excep_tol='a'
            validate.exceptions(excep_val=excep_val, excep_tol=excep_tol)

    def test_excep_tol_wrong_number_of_elements(self):
        with self.assertRaises(ValueError):
            excep_val=[1,2,3]
            excep_tol=[1,2,3,4]
            validate.exceptions(excep_val=excep_val,excep_tol=excep_tol)

    def test_excep_col_wrong_number_of_elements(self):
        with self.assertRaises(ValueError):
            excep_val=[1,2,3]
            excep_col=['blue','red']
            validate.exceptions(excep_val=excep_val,excep_col=excep_col)

    def test_excep_col_wrong_number_of_elements_2(self):
        with self.assertRaises(ValueError):
            excep_val=[1,2,3]
            excep_col='blue'
            validate.exceptions(excep_val=excep_val,excep_col=excep_col)

    def test_excep_col_wrong_number_of_elements_3(self):
        with self.assertRaises(ValueError):
            excep_val=[1,2,3]
            excep_col=[[23,24,23],[45,46,47]]
            validate.exceptions(excep_val=excep_val,excep_col=excep_col)

    def test_excep_col_wrong_type(self):
        with self.assertRaises(TypeError):
            excep_val=[1,2,3]
            excep_col=['blue','red',3]
            validate.exceptions(excep_val=excep_val,excep_col=excep_col)

    def test_excep_col_wrong_type(self):
        with self.assertRaises(TypeError):
            excep_val=[1,2,3]
            excep_col=1
            validate.exceptions(excep_val=excep_val,excep_col=excep_col)

    def test_exceptions_default_1(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1e-3,1e-3,1e-3]).tolist(), [[0,0,0]]*3]
           excep_val=[1,2,3]
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                           default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_no_exceptions(self):
           ans= [0, None, None, None]
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions()
           returned = [n_excep, excep_val_np, excep_tol_np, excep_col_rgb]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_1_tol(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([10.,10.,10.]).tolist(), [[0,0,0]]*3]
           excep_val=[1,2,3]
           excep_tol=10.
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                 excep_tol=excep_tol,
                                                 default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_3_tol(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1.,10.,100.]).tolist(), [[0,0,0]]*3]
           excep_val=[1,2,3]
           excep_tol=[1,10,100]
           n_excep, excep_val_np, excep_tol_np, excep_col_rgb = validate.exceptions(excep_val=excep_val,
                                                                                    excep_tol=excep_tol,
                                                                                    default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_1_txt_col(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1.,10.,100.]).tolist(), [[255,255,255]]*3]
           excep_val=[1,2,3]
           excep_tol=[1,10,100]
           excep_col='white'
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                 excep_tol=excep_tol,
                                                 excep_col=excep_col,
                                                 default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_3_txt_col(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1.,10.,100.]).tolist(), [[255,255,255],[0,0,0],[255,255,255]] ]
           excep_val=[1,2,3]
           excep_tol=[1,10,100]
           excep_col=['white','black','white']
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                 excep_tol=excep_tol,
                                                 excep_col=excep_col,
                                                 default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_1_rgb_col(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1.,10.,100.]).tolist(), [[255,255,255]]*3]
           excep_val=[1,2,3]
           excep_tol=[1,10,100]
           excep_col=[255,255,255]
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                 excep_tol=excep_tol,
                                                 excep_col=excep_col,
                                                 default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)

    def test_exceptions_passed_3_rgb_col(self):
           ans= [3, np.array([1.,2,3]).tolist(), np.array([1.,10.,100.]).tolist(), [[255,255,255],[0,0,0],[255,255,255]]]
           excep_val=[1,2,3]
           excep_tol=[1,10,100]
           excep_col=[[255,255,255],[0,0,0],[255,255,255]]
           (n_excep, 
            excep_val_np, 
            excep_tol_np, 
            excep_col_rgb) = validate.exceptions(excep_val=excep_val,
                                                 excep_tol=excep_tol,
                                                 excep_col=excep_col,
                                                 default_excep_col='black')
           returned = [n_excep, excep_val_np.tolist(), excep_tol_np.tolist(), excep_col_rgb.tolist()]
           self.assertEqual(ans,returned)


if __name__ == '__main__':
    unittest.main()
