import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #error testing for "n_col" parameter
    def test_n_col_invalid(self):
        with self.assertRaises(TypeError):
            validate.n_col(n_col='s')

    def test_n_col_to_many(self):
        with self.assertRaises(ValueError):
            validate.n_col(n_col=9)

    def test_n_col_valid(self):
        self.assertEqual(validate.n_col(n_col=2.7), int(2))

if __name__ == '__main__':
    unittest.main()
