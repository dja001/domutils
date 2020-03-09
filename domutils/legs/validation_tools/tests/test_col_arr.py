import unittest
import domutils.legs.col_utils as col_utils
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    def test_col_arr_mixed_list(self):
        with self.assertRaises(TypeError):
            validate.color_arr_and_solid([3,'a'])

    def test_col_arr_default_no__n_col(self):
            ans = [[[255, 255, 255], [0, 0, 0]],'dark_red',1]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid()
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_default_n_col_eq_2(self):
            ans = [[[[223, 215, 208], [ 96, 56,  19]], 
                    [[169, 222, 255], [  0, 81, 237]]], 'black',2]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(n_col=2)
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_numerical_val(self):
            in_col=[[0.1,0,0],[254.7,255,255]]
            ans = [[[0, 0, 0], [254, 255, 255]],'black',1]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col)
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_numerical_val_supplied(self):
            in_col= [[0.1,0,0], [254.7,255,255]]
            ans = [ [[0, 0, 0], [254, 255, 255]],'black',2]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='supplied')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_val(self):
            in_col= ['red','green']
            ans = [ [[[255, 190, 187], [158,   0, 13]], 
                     [[134, 222, 134], [  0, 134,  0]]],'black',2]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col)
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_val_col_light(self):
            in_col= ['red','green']
            ans = [ [[255, 190, 187], [134, 222, 134]],'black',2]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='col_light')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_with_grey(self):
            in_col= ['grey_120','red','gray_250']
            ans = [ [[120,120,120], [255, 190, 187], [250,250,250]],'black',3]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='col_light')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_with_only_one_txt_color(self):
            in_col= 'red'
            ans = [ [[255, 190, 187]],'black',1]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='col_light')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_with_only_grey(self):
            in_col= 'grey_120'
            ans = [ [[120,120,120]],'black',1]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='col_light')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)

    def test_col_arr_txt_val_col_dark(self):
            in_col= ['red']
            ans = [ [[158, 0, 13]],'black',1]
            color_arr_rgb, default_excep_col, n_col = validate.color_arr_and_solid(color_arr=in_col,solid='col_dark')
            returned = [color_arr_rgb.tolist(), default_excep_col, n_col]
            self.assertEqual(ans,returned)


if __name__ == '__main__':
    unittest.main()
