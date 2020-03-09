import unittest
import numpy as np
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing over_under_value
    def test_over_value_under_empty(self):
        ans = ['exact',None]
        (bound_action,bound_color) =  validate.over_under_value()
        returned = [bound_action,bound_color]
        self.assertEqual(ans,returned)

    def test_over_under_value_exact(self):
        ans = ['exact',None]
        (bound_action,
         bound_color) = validate.over_under_value('exact')
        returned = [bound_action, bound_color]
        self.assertEqual(ans,returned)

    def test_over_under_value_named_color(self):
        ans = ['extend',[255,255,255]]
        (bound_action,
         bound_color) = validate.over_under_value('white')
        returned = [bound_action, bound_color.tolist()]
        self.assertEqual(ans,returned)

    def test_over_under_value_color_arr(self):
        ans = ['extend',[255,155,255]]
        (bound_action,
         bound_color) = validate.over_under_value([255,155,255])
        returned = [bound_action, bound_color.tolist()]
        self.assertEqual(ans,returned)


if __name__ == '__main__':
    unittest.main()
