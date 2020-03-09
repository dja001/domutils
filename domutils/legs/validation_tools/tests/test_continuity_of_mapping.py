import unittest
import domutils.legs as legs
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing apply method 
    def test_apply_wrong_low_oper(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.lows.oper = '='
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_discontinuous_lows(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(n_col=2)   
            map_obj.lows.val = -0.1
            validate.continuity_of_mapping(map_obj)
            
    def test_apply_wrong_value_discontinuous_low_oper1(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.lows.oper = '<='
            map_obj.cols[0].oper_low = '>='
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_discontinuous_low_oper2(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.lows.oper = '<'
            map_obj.cols[0].oper_low = '>'
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_discontinuous_col_leg(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(color_arr=['red','blue'])
            map_obj.cols[0].oper_high = '<'
            map_obj.cols[1].oper_low  = '>'
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_oper_high(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(color_arr=['red','blue','green'])
            map_obj.cols[1].oper_high = '+'
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_oper_low(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(color_arr=['red','blue'])
            map_obj.cols[1].oper_low = '<'
            validate.continuity_of_mapping(map_obj)

    def test_apply_bounds_mismatch(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(color_arr=['red','blue','green'])
            map_obj.cols[1].val_high = 1.0
            map_obj.cols[2].val_low  = 1.1
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_high_oper(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.highs.oper = '='
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_discontinuous_high(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj(n_col=2)   
            map_obj.highs.val = 0.1
            validate.continuity_of_mapping(map_obj)
            
    def test_apply_wrong_value_discontinuous_high_oper1(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.highs.oper = '>='
            map_obj.cols[-1].oper_high = '<='
            validate.continuity_of_mapping(map_obj)

    def test_apply_wrong_value_discontinuous_high_oper2(self):
        with self.assertRaises(ValueError):
            map_obj = legs.PalObj()   
            map_obj.lows.oper = '>'
            map_obj.cols[0].oper_low = '<'
            validate.continuity_of_mapping(map_obj)

if __name__ == '__main__':
    unittest.main()
