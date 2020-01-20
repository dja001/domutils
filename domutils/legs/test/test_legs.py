import unittest
import numpy as np
import legs


class TestStringMethods(unittest.TestCase):

    #default map is a black and white palette for data values in the interval [0,1]
    def test_legs_no_args(self):
        black_white_mapping = legs.new()
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = black_white_mapping.apply(data)
        #                           data value  color
        ans = [[255, 255, 255],   #    0.00     white    
               [170, 170, 170],   #    0.33     grey     
               [ 86,  86,  86],   #    0.66     grey     
               [  0,   0,   0]]   #    1.00     black    
        self.assertEqual(rgb_img.tolist(),ans)

    #because this is an exact palette, an error is raised if values are found outside of the interval [0,1]
    def test_legs_no_args_above_palette(self):
        with self.assertRaises(RuntimeError):
            black_white_mapping = legs.new()
            data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
            rgb_img = black_white_mapping.apply(data)                       #an error is raised

    #one solution is to adjust range of palette so that is encompasses the data
    def test_legs_range(self):
        black_white_mapping = legs.new(range_arr=[0.,1.1])
        data = [0.000, 0.366, 0.733, 1.100]
        rgb_img = black_white_mapping.apply(data)           
        #                           data value  color
        ans = [[255, 255, 255],    #   0.000    white
               [170, 170, 170],    #   0.366    grey 
               [ 85,  85,  85],    #   0.733    grey
               [  0,   0,   0]]    #   1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    #another possibility is to extend the first and last color of the palette beyond the range of the palette
    #this is done with the "over_under" keyword
    def test_legs_range_over_under(self):
        black_white_mapping = legs.new(range_arr=[0.,1],over_under='extend')
        data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
        rgb_img = black_white_mapping.apply(data)
        #                           data value  color
        ans = [[255, 255, 255],   #    0.000    white
               [161, 161, 161],   #    0.366    grey 
               [ 68,  68,  68],   #    0.733    grey
               [  0,   0,   0]]   #    1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    #end points can be handled separately 
    #this is done with the "over_high" and "under_low" keywords
    def test_legs_range_over_high_under_low(self):
        black_white_mapping = legs.new(range_arr=[0.,1],over_high='extend',under_low='exact')
        data = [0.000, 0.366, 0.733, 1.100] #    1.1 is above [0,1] range of the palette
        rgb_img = black_white_mapping.apply(data) #No error is raised
        #                           data value  color
        ans = [[255, 255, 255],   #    0.000    white 
               [161, 161, 161],   #    0.366    grey 
               [ 68,  68,  68],   #    0.733    grey
               [  0,   0,   0]]   #    1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    #keyword n_col makes for easy semi-continuous palettes
    def test_legs_n_col(self):
        #default color order: ['brown','blue','green','orange','red','pink','purple','yellow']
        two_color_mapping = legs.new(n_col=2)
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = two_color_mapping.apply(data)      
        #                           data value  color
        ans = [[223, 215, 208],   #    0.00     light brown
              [ 139, 110,  83],   #    0.33     dark brown
              [ 114, 176, 249],   #    0.66     light blue
              [   0,  81, 237]]   #    1.00     dark blue
        self.assertEqual(rgb_img.tolist(),ans)

    #if you don't like the default order, colors can be speficied directly
    def test_legs_col_arr_one_col_txt(self):
        #see color dictionary in col_utils for the list of available colors
        orange_mapping = legs.new(color_arr = 'orange')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_mapping.apply(data)      
        #                           data value  color
        ans = [[255,  86,   0],   #    0.00     dark orange
               [255, 122,  41],   #    0.33     
               [255, 158,  82],   #    0.66     
               [255, 194, 124]]   #    1.00     light orange

    #any number of colors can be specified
    def test_legs_col_arr_two_col_txt(self):
        orange_blue_mapping = legs.new(color_arr = ['orange','blue'])
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans = [[255, 194, 124],   #    0.00     light orange
               [255, 122,  42],   #    0.33     dark orange 
               [114, 176, 249],   #    0.66     light blue
               [  0,  81, 237]]   #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    #for exact color control, RGB values can be specified directly
    def test_legs_col_arr_two_col_rgb(self):
        orange_blue_mapping = legs.new(color_arr = [[[255, 194, 124],[255,  86,   0]],      #[light orange],[dark orange]
                                                    [[169, 222, 255],[000,  81, 237]]])     #[light blue]  ,[dark blue  ]
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans = [[255, 194, 124],   #    0.00     light orange
               [255, 122,  42],   #    0.33     dark orange 
               [114, 176, 249],   #    0.66     light blue
               [  0,  81, 237]]   #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    #by default, dark colors are associated to high data values
    #this can be changed for all color legs with the "dark_pos" keyword
    def test_legs_col_arr_two_col_txt_dark_pos(self):
        orange_blue_mapping = legs.new(color_arr = ['orange','blue'], dark_pos='low')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255, 157,  81],  #    0.33     light orange
                [ 54, 126, 242],  #    0.66     dark_blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    #for diverging palette
    #we need dark color to be associated with high and low values 
    #for different color legs
    def test_legs_col_arr_two_col_txt_dark_pos_diff(self):
        orange_blue_mapping = legs.new(color_arr = ['orange','blue'], dark_pos=['low','high'])
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255, 157,  81],  #    0.33     light orange
                [114, 176, 249],  #    0.66     light blue
                [  0,  81, 237]]  #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    #for categorical color palettes we need conly one color per legs
    #this is done with the "solid" keyword
    def test_legs_col_arr_two_col_txt_solid_dark(self):
        orange_blue_mapping = legs.new(color_arr = ['orange','blue'], solid='col_dark')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255,  86,   0],  #    0.33     dark orange
                [  0,  81, 237],  #    0.66     dark blue
                [  0,  81, 237]]  #    1.00     dark blue
        self.assertEqual(rgb_img.tolist(),ans)

    #solid can also be set to col_light
    def test_legs_col_arr_two_col_txt_solid_light(self):
        orange_blue_mapping = legs.new(color_arr = ['orange','blue'], solid='col_light')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans =  [[255, 194, 124],  #    0.00     light orange
                [255, 194, 124],  #    0.33     light orange
                [169, 222, 255],  #    0.66     light blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    #or any color you like by passing RGB values to color_arr
    def test_legs_col_arr_two_col_txt_solid_supplied(self):
        orange_blue_mapping = legs.new(color_arr = [[255, 194, 124],                    #light orange
                                                   [169, 222, 255]], solid='supplied')  #light blue
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.apply(data)      
        #                           data value  color
        ans =  [[255, 194, 124],  #    0.00     light orange
                [255, 194, 124],  #    0.33     light orange
                [169, 222, 255],  #    0.66     light blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    #data value with special meaning (nodata, zero, etc) can be assigned special colors 
    #using exceptions
    def test_legs_col_excep_1(self):
        black_white_mapping = legs.new(range_arr=[1,6],excep_val=-999.) 
        data = [1.,2,3,-999,5,6]
        rgb_img = black_white_mapping.apply(data)      
        #                           data value  color
        ans =  [[255, 255, 255],  #     1       white
                [204, 204, 204],  #     2       grey
                [153, 153, 153],  #     3       grey
                [158,   0,  13],  #     -999 -> special value in red
                [ 51,  51,  51],  #     5       grey
                [  0,   0,   0]]  #     6       black
        self.assertEqual(rgb_img.tolist(),ans)

    #One may choose the value, tolerance and color of exception value
    def test_legs_excep_2(self):
        black_white_mapping = legs.new(range_arr=[1,6],excep_val=[0, -999.],
                                                       excep_tol=[.7, 1e-3],
                                                       excep_col=['dark_blue','dark_red'])
        data = [1,-.5, 0, .5, 2, 3, 4, -999, 5, 6]
        rgb_img = black_white_mapping.apply(data)      
        #                           data value  color
        ans = [[255, 255, 255],   #     1       white
               [  0,  81, 237],   #     .-5  -> special value in dark_blue
               [  0,  81, 237],   #     0    -> special value in dark_blue
               [  0,  81, 237],   #     .5   -> special value in dark_blue
               [204, 204, 204],   #     2       grey
               [153, 153, 153],   #     3       grey
               [102, 102, 102],   #     4       grey
               [158,   0,  13],   #     -999 -> special value in dark_blue
               [ 51,  51,  51],   #     5       grey
               [  0,   0,   0]]   #     6       black
        self.assertEqual(rgb_img.tolist(),ans)



if __name__ == '__main__':
    unittest.main()
