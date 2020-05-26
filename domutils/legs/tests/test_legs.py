import unittest
import numpy as np
import domutils.legs as legs


class TestStringMethods(unittest.TestCase):

    def test_legs_no_args(self):
        #default map is a black and white palette for data values in the interval [0,1]
        black_white_mapping = legs.PalObj()
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = black_white_mapping.to_rgb(data)
        #                           data value  color
        ans = [[255, 255, 255],   #    0.00     white    
               [170, 170, 170],   #    0.33     grey     
               [ 86,  86,  86],   #    0.66     grey     
               [  0,   0,   0]]   #    1.00     black    
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_no_args_above_palette(self):
        #because this is an exact palette, an error is raised if values are found outside of the interval [0,1]
        black_white_mapping = legs.PalObj()
        data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
        with self.assertRaises(RuntimeError):
            rgb_img = black_white_mapping.to_rgb(data)                       #an error is raised

    def test_legs_range(self):
        #one solution is to adjust range of palette so that is encompasses the data
        black_white_mapping = legs.PalObj(range_arr=[0.,1.1])
        data = [0.000, 0.366, 0.733, 1.100]
        rgb_img = black_white_mapping.to_rgb(data)           
        #                           data value  color
        ans = [[255, 255, 255],    #   0.000    white
               [170, 170, 170],    #   0.366    grey 
               [ 85,  85,  85],    #   0.733    grey
               [  0,   0,   0]]    #   1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_range_over_under(self):
        #another possibility is to extend the first and last color of the palette beyond the range of the palette
        #this is done with the "over_under" keyword
        black_white_mapping = legs.PalObj(range_arr=[0.,1],over_under='extend')
        data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
        rgb_img = black_white_mapping.to_rgb(data)
        #                           data value  color
        ans = [[255, 255, 255],   #    0.000    white
               [161, 161, 161],   #    0.366    grey 
               [ 68,  68,  68],   #    0.733    grey
               [  0,   0,   0]]   #    1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_range_over_high_under_low(self):
        #end points can be handled separately 
        #this is done with the "over_high" and "under_low" keywords
        black_white_mapping = legs.PalObj(range_arr=[0.,1],over_high='extend',under_low='exact')
        data = [0.000, 0.366, 0.733, 1.100] #    1.1 is above [0,1] range of the palette
        rgb_img = black_white_mapping.to_rgb(data) #No error is raised
        #                           data value  color
        ans = [[255, 255, 255],   #    0.000    white 
               [161, 161, 161],   #    0.366    grey 
               [ 68,  68,  68],   #    0.733    grey
               [  0,   0,   0]]   #    1.100    black
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_n_col(self):
        #keyword n_col makes for easy semi-continuous palettes
        #default color order: ['brown','blue','green','orange','red','pink','purple','yellow']
        two_color_mapping = legs.PalObj(n_col=2)
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = two_color_mapping.to_rgb(data)      
        #                           data value  color
        ans = [[223, 215, 208],   #    0.00     light brown
              [ 139, 110,  83],   #    0.33     dark brown
              [ 114, 176, 249],   #    0.66     light blue
              [   0,  81, 237]]   #    1.00     dark blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_one_col_txt(self):
        #if you don't like the default order, colors can be speficied directly
        #see color dictionary in col_utils for the list of available colors
        orange_mapping = legs.PalObj(color_arr = 'orange')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_mapping.to_rgb(data)      
        #                           data value  color
        ans = [[255, 194, 124],   #    0.00     light orange
               [255, 158,  83],   #    0.33     
               [255, 122,  42],   #    0.66     
               [255,  86,   0]]   #    1.00     dark orange
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt(self):
        #any number of colors can be specified
        orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'])
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans = [[255, 194, 124],   #    0.00     light orange
               [255, 122,  42],   #    0.33     dark orange 
               [114, 176, 249],   #    0.66     light blue
               [  0,  81, 237]]   #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_rgb(self):
        #for exact color control, RGB values can be specified directly
        orange_blue_mapping = legs.PalObj(color_arr = [[[255, 194, 124],[255,  86,   0]],      #[light orange],[dark orange]
                                                       [[169, 222, 255],[000,  81, 237]]])     #[light blue]  ,[dark blue  ]
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans = [[255, 194, 124],   #    0.00     light orange
               [255, 122,  42],   #    0.33     dark orange 
               [114, 176, 249],   #    0.66     light blue
               [  0,  81, 237]]   #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_one_col_txt(self):
        #one color as a text string
        blue_mapping = legs.PalObj(color_arr = 'blue')
        data = [0.00, 1.00]
        rgb_img = blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[169, 222, 255],  #    1.00     light blue
                [  0,  81, 237]]  #    0.66     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_one_col_grey_txt(self):
        #one color as a text string
        blue_mapping = legs.PalObj(color_arr = 'grey_175')
        data = [0.00, 1.00]
        rgb_img = blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[175, 175, 175],  #    1.00     grey 175
                [175, 175, 175]]  #    0.66     grey 175
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt_dark_pos(self):
        #by default, dark colors are associated to high data values
        #this can be changed for all color legs with the "dark_pos" keyword
        orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], dark_pos='low')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255, 157,  81],  #    0.33     light orange
                [ 54, 126, 242],  #    0.66     dark_blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt_dark_pos_diff(self):
        #for diverging palette
        #we need dark color to be associated with high and low values 
        #for different color legs
        orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], dark_pos=['low','high'])
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255, 157,  81],  #    0.33     light orange
                [114, 176, 249],  #    0.66     light blue
                [  0,  81, 237]]  #    1.00     dark_blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt_solid_dark(self):
        #for categorical color palettes we need conly one color per legs
        #this is done with the "solid" keyword
        orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], solid='col_dark')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255,  86,   0],  #    0.00     dark orange
                [255,  86,   0],  #    0.33     dark orange
                [  0,  81, 237],  #    0.66     dark blue
                [  0,  81, 237]]  #    1.00     dark blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt_solid_light(self):
        #solid can also be set to col_light
        orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], solid='col_light')
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255, 194, 124],  #    0.00     light orange
                [255, 194, 124],  #    0.33     light orange
                [169, 222, 255],  #    0.66     light blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_one_col_txt_solid_supplied(self):
        #or any color you like by passing RGB values to color_arr
        orange_mapping = legs.PalObj(color_arr = [255, 194, 124], solid='supplied')  #light orange
                                                       
        data = [0.00, 1.00]
        rgb_img = orange_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255, 194, 124],  #    0.00     light orange
                [255, 194, 124]]  #    1.00     light orange
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_arr_two_col_txt_solid_supplied(self):
        #or any color you like by passing RGB values to color_arr
        orange_blue_mapping = legs.PalObj(color_arr = [[255, 194, 124],                    #light orange
                                                       [169, 222, 255]], solid='supplied')  #light blue
        data = [0.00, 0.33, 0.66, 1.00]
        rgb_img = orange_blue_mapping.to_rgb(data)      
        #                           data value  color
        ans =  [[255, 194, 124],  #    0.00     light orange
                [255, 194, 124],  #    0.33     light orange
                [169, 222, 255],  #    0.66     light blue
                [169, 222, 255]]  #    1.00     light blue
        self.assertEqual(rgb_img.tolist(),ans)

    def test_legs_col_excep_1(self):
        #data value with special meaning (nodata, zero, etc) can be assigned special colors 
        #using exceptions
        black_white_mapping = legs.PalObj(range_arr=[1,6],excep_val=-999.) 
        data = [1.,2,3,-999,5,6]
        rgb_img = black_white_mapping.to_rgb(data)      
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
        black_white_mapping = legs.PalObj(range_arr=[1,6],excep_val=[0, -999.],
                                                          excep_tol=[.7, 1e-3],
                                                          excep_col=['dark_blue','dark_red'])
        data = [1,-.5, 0, .5, 2, 3, 4, -999, 5, 6]
        rgb_img = black_white_mapping.to_rgb(data)      
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
