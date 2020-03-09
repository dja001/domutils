import unittest
import domutils.legs.validation_tools as validate


class TestStringMethods(unittest.TestCase):

    #testing input_data   
    def test_input_data(self):
        with self.assertRaises(TypeError):
            data = ['a']
            validate.input_data(data)

if __name__ == '__main__':
    unittest.main()
