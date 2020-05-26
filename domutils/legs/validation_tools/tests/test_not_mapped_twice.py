import unittest
import numpy as np
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    def test_not_mapped_twice(self):
        with self.assertRaises(RuntimeError):
            data_flat =     np.array([1,2,3,4,5,6,7,8,9])
            action_record = np.array([1,1,2,2,2,2,2,2,1])
            validate.not_mapped_twice(data_flat, action_record)


if __name__ == '__main__':
    unittest.main()
