import pytest
import numpy as np
import domutils.legs as legs



def test_legs_no_args():
    #default map is a black and white palette for data values in the interval [0,1]
    black_white_mapping = legs.PalObj()
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = black_white_mapping.to_rgb(data)
    #                                    data value  color
    ans = np.array([[255, 255, 255],   #    0.00     white    
                    [170, 170, 170],   #    0.33     grey     
                    [ 86,  86,  86],   #    0.66     grey     
                    [  0,   0,   0]])  #    1.00     black    
    assert np.allclose(rgb_img, ans)

def test_legs_no_args_above_palette():
    #because this is an exact palette, an error is raised if values are found outside of the interval [0,1]
    black_white_mapping = legs.PalObj()
    data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
    with pytest.raises(RuntimeError):
        rgb_img = black_white_mapping.to_rgb(data)                       #an error is raised

def test_legs_range():
    #one solution is to adjust range of palette so that is encompasses the data
    black_white_mapping = legs.PalObj(range_arr=[0.,1.1])
    data = [0.000, 0.366, 0.733, 1.100]
    rgb_img = black_white_mapping.to_rgb(data)           
    #                                    data value  color
    ans = np.array([[255, 255, 255],    #   0.000    white
                    [170, 170, 170],    #   0.366    grey 
                    [ 85,  85,  85],    #   0.733    grey
                    [  0,   0,   0]])   #   1.100    black
    assert np.allclose(rgb_img, ans)

def test_legs_range_over_under():
    #another possibility is to extend the first and last color of the palette beyond the range of the palette
    #this is done with the "over_under" keyword
    black_white_mapping = legs.PalObj(range_arr=[0.,1],over_under='extend')
    data = [0.000, 0.366, 0.733, 1.100]#     1.1 is above [0,1] range of the palette
    rgb_img = black_white_mapping.to_rgb(data)
    #                                    data value  color
    ans = np.array([[255, 255, 255],   #    0.000    white
                    [161, 161, 161],   #    0.366    grey 
                    [ 68,  68,  68],   #    0.733    grey
                    [  0,   0,   0]])  #    1.100    black
    assert np.allclose(rgb_img, ans)

def test_legs_range_over_high_under_low():
    #end points can be handled separately 
    #this is done with the "over_high" and "under_low" keywords
    black_white_mapping = legs.PalObj(range_arr=[0.,1],over_high='extend',under_low='exact')
    data = [0.000, 0.366, 0.733, 1.100] #    1.1 is above [0,1] range of the palette
    rgb_img = black_white_mapping.to_rgb(data) #No error is raised
    #                                    data value  color
    ans = np.array([[255, 255, 255],   #    0.000    white 
                    [161, 161, 161],   #    0.366    grey 
                    [ 68,  68,  68],   #    0.733    grey
                    [  0,   0,   0]])  #    1.100    black
    assert np.allclose(rgb_img, ans)

def test_legs_n_col():
    #keyword n_col makes for easy semi-continuous palettes
    #default color order: ['brown','blue','green','orange','red','pink','purple','yellow']
    two_color_mapping = legs.PalObj(n_col=2)
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = two_color_mapping.to_rgb(data)      
    #                                    data value  color
    ans = np.array([[223, 215, 208],   #    0.00     light brown
                   [ 139, 110,  83],   #    0.33     dark brown
                   [ 114, 176, 249],   #    0.66     light blue
                   [   0,  81, 237]])  #    1.00     dark blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_one_col_txt():
    #if you don't like the default order, colors can be speficied directly
    #see color dictionary in col_utils for the list of available colors
    orange_mapping = legs.PalObj(color_arr = 'orange')
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_mapping.to_rgb(data)      
    #                                    data value  color
    ans = np.array([[255, 194, 124],   #    0.00     light orange
                    [255, 158,  83],   #    0.33     
                    [255, 122,  42],   #    0.66     
                    [255,  86,   0]])  #    1.00     dark orange
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt():
    #any number of colors can be specified
    orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'])
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans = np.array([[255, 194, 124],   #    0.00     light orange
                    [255, 122,  42],   #    0.33     dark orange 
                    [114, 176, 249],   #    0.66     light blue
                    [  0,  81, 237]])  #    1.00     dark_blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_rgb():
    #for exact color control, RGB values can be specified directly
    orange_blue_mapping = legs.PalObj(color_arr = [[[255, 194, 124],[255,  86,   0]],      #[light orange],[dark orange]
                                                   [[169, 222, 255],[000,  81, 237]]])     #[light blue]  ,[dark blue  ]
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans = np.array([[255, 194, 124],   #    0.00     light orange
                    [255, 122,  42],   #    0.33     dark orange 
                    [114, 176, 249],   #    0.66     light blue
                    [  0,  81, 237]])  #    1.00     dark_blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_one_col_txt():
    #one color as a text string
    blue_mapping = legs.PalObj(color_arr = 'blue')
    data = [0.00, 1.00]
    rgb_img = blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[169, 222, 255],  #    1.00     light blue
                     [  0,  81, 237]]) #    0.66     dark_blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_one_col_grey_txt():
    #one color as a text string
    blue_mapping = legs.PalObj(color_arr = 'grey_175')
    data = [0.00, 1.00]
    rgb_img = blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[175, 175, 175],  #    1.00     grey 175
                     [175, 175, 175]]) #    0.66     grey 175
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt_dark_pos():
    #by default, dark colors are associated to high data values
    #this can be changed for all color legs with the "dark_pos" keyword
    orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], dark_pos='low')
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255,  86,   0],  #    0.00     dark orange
                     [255, 157,  81],  #    0.33     light orange
                     [ 54, 126, 242],  #    0.66     dark_blue
                     [169, 222, 255]]) #    1.00     light blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt_dark_pos_diff():
    #for diverging palette
    #we need dark color to be associated with high and low values 
    #for different color legs
    orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], dark_pos=['low','high'])
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255,  86,   0],  #    0.00     dark orange
                     [255, 157,  81],  #    0.33     light orange
                     [114, 176, 249],  #    0.66     light blue
                     [  0,  81, 237]]) #    1.00     dark_blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt_solid_dark():
    #for categorical color palettes we need conly one color per legs
    #this is done with the "solid" keyword
    orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], solid='col_dark')
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255,  86,   0],  #    0.00     dark orange
                     [255,  86,   0],  #    0.33     dark orange
                     [  0,  81, 237],  #    0.66     dark blue
                     [  0,  81, 237]]) #    1.00     dark blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt_solid_light():
    #solid can also be set to col_light
    orange_blue_mapping = legs.PalObj(color_arr = ['orange','blue'], solid='col_light')
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255, 194, 124],  #    0.00     light orange
                     [255, 194, 124],  #    0.33     light orange
                     [169, 222, 255],  #    0.66     light blue
                     [169, 222, 255]]) #    1.00     light blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_one_col_txt_solid_supplied():
    #or any color you like by passing RGB values to color_arr
    orange_mapping = legs.PalObj(color_arr = [255, 194, 124], solid='supplied')  #light orange
                                                   
    data = [0.00, 1.00]
    rgb_img = orange_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255, 194, 124],  #    0.00     light orange
                     [255, 194, 124]]) #    1.00     light orange
    assert np.allclose(rgb_img, ans)

def test_legs_col_arr_two_col_txt_solid_supplied():
    #or any color you like by passing RGB values to color_arr
    orange_blue_mapping = legs.PalObj(color_arr = [[255, 194, 124],                    #light orange
                                                   [169, 222, 255]], solid='supplied')  #light blue
    data = [0.00, 0.33, 0.66, 1.00]
    rgb_img = orange_blue_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255, 194, 124],  #    0.00     light orange
                     [255, 194, 124],  #    0.33     light orange
                     [169, 222, 255],  #    0.66     light blue
                     [169, 222, 255]]) #    1.00     light blue
    assert np.allclose(rgb_img, ans)

def test_legs_col_excep_1():
    #data value with special meaning (nodata, zero, etc) can be assigned special colors 
    #using exceptions
    black_white_mapping = legs.PalObj(range_arr=[1,6],excep_val=-999.) 
    data = [1.,2,3,-999,5,6]
    rgb_img = black_white_mapping.to_rgb(data)      
    #                                    data value  color
    ans =  np.array([[255, 255, 255],  #     1       white
                     [204, 204, 204],  #     2       grey
                     [153, 153, 153],  #     3       grey
                     [158,   0,  13],  #     -999 -> special value in red
                     [ 51,  51,  51],  #     5       grey
                     [  0,   0,   0]]) #     6       black
    assert np.allclose(rgb_img, ans)

# One may choose the value, tolerance and color of exception value
def test_legs_excep_2():
    black_white_mapping = legs.PalObj(range_arr=[1,6],excep_val=[0, -999.],
                                                      excep_tol=[.7, 1e-3],
                                                      excep_col=['dark_blue','dark_red'])
    data = [1,-.5, 0, .5, 2, 3, 4, -999, 5, 6]
    rgb_img = black_white_mapping.to_rgb(data)      
    #                                    data value  color
    ans = np.array([[255, 255, 255],   #     1       white
                    [  0,  81, 237],   #     .-5  -> special value in dark_blue
                    [  0,  81, 237],   #     0    -> special value in dark_blue
                    [  0,  81, 237],   #     .5   -> special value in dark_blue
                    [204, 204, 204],   #     2       grey
                    [153, 153, 153],   #     3       grey
                    [102, 102, 102],   #     4       grey
                    [158,   0,  13],   #     -999 -> special value in dark_blue
                    [ 51,  51,  51],   #     5       grey
                    [  0,   0,   0]])  #     6       black
    assert np.allclose(rgb_img, ans)

def test_renders_in_non_geo_plots(setup_test_paths):

    import os
    import numpy as np
    import scipy.signal
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import domutils.legs as legs
    import domutils._py_tools as py_tools

    #setting up directories
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    reference_figure_dir = os.path.join(test_data_dir,    'reference_figures', 'test_legs')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_legs')

    py_tools.parallel_mkdir(generated_figure_dir)
    
    #Gaussian bell mock data
    npts = 1024
    half_npts = int(npts/2)
    x = np.linspace(-1., 1, half_npts+1)
    y = np.linspace(-1., 1, half_npts+1)
    xx, yy = np.meshgrid(x, y)
    gauss_bulge = np.exp(-(xx**2 + yy**2) / .6**2)
    #exceptions are usefull for NoData, missing values, etc
    #lets assing exception values to the Gaussian Bulge data
    gauss_bulge_with_exceptions = np.copy(gauss_bulge)
    gauss_bulge_with_exceptions[388:488, 25:125] = -9999.
    gauss_bulge_with_exceptions[388:488,150:250] = -6666.
    gauss_bulge_with_exceptions[388:488,275:375] = -3333.
    
    # figure properties
    mpl.rcParams.update({'font.size': 18})
    mpl.rcParams.update({'font.family':'Latin Modern Roman'})
    fig_w, fig_h = 5.6, 5. #size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))

    rec_w = 4.           #size of axes
    rec_h = 4.           #size of axes
    sp_w  = 2.           #horizontal space between axes
    sp_h  = 1.           #vertical space between axes
    
    x0 = (.5)/fig_w 
    y0 = .5/fig_h
    ax = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    for axis in ['top','bottom','left','right']:   
        ax.spines[axis].set_linewidth(.3)
    limits = (-1.,1.)           #data extent for axes
    dum = ax.set_xlim(limits)   # "dum =" to avoid printing output
    dum = ax.set_ylim(limits) 
    ticks  = [-1.,0.,1.]        #tick values
    dum = ax.set_xticks(ticks)
    dum = ax.set_yticks(ticks)

    mapping_3_except = legs.PalObj(excep_val=[-9999.,      -6666.,    -3333.],
                                   excep_col=['dark_green','grey_80', 'light_pink'])
    mapping_3_except.plot_data(ax=ax,data=gauss_bulge_with_exceptions,
                               palette='right', pal_units='[unitless]',
                               pal_format='{:2.0f}')
    
    #newly generated figure
    generated_figure = os.path.join(generated_figure_dir, 'three_exceptions.svg')
    plt.savefig(generated_figure)

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar



if __name__ == '__main__':
    renders_in_non_geo_plots()
    #test_legs_no_args()
