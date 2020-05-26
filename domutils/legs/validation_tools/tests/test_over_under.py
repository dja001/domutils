import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    def test_over_under_too_many_args(self):
        with self.assertRaises(ValueError):
            validate.over_under(over_under='extend', under_low='exact')

    def test_over_under_no_args(self):
        ans = ['exact',None,'exact',None]
        (high_action,
         high_color,
         low_action,
         low_color) = validate.over_under(over_under=None, under_low=None, over_high=None)
        returned = [high_action, high_color, low_action, low_color]
        self.assertEqual(ans,returned)

    def test_over_under_col(self):
        ans = ['extend',[0,0,0],'extend',[0,0,0]]
        (high_action,
         high_color,
         low_action,
         low_color) = validate.over_under(over_under='black', under_low=None, over_high=None)
        returned = [high_action, high_color.tolist(), low_action, low_color.tolist()]
        self.assertEqual(ans,returned)

    def test_over_under_only_under_low(self):
        ans = ['exact',None,'extend',[27,22,23]]
        (high_action,
         high_color,
         low_action,
         low_color) = validate.over_under(over_under=None, under_low=[27,22,23], over_high=None)
        returned = [high_action, high_color, low_action, low_color.tolist()]
        self.assertEqual(ans,returned)

    def test_over_under_only_over_high(self):
        ans = ['extend',[255,255,255],'exact',None]
        (high_action,
         high_color,
         low_action,
         low_color) = validate.over_under(over_under=None, under_low=None, over_high='white')
        returned = [high_action, high_color.tolist(), low_action, low_color]
        self.assertEqual(ans,returned)

if __name__ == '__main__':
    unittest.main()
