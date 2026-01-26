import pytest



@pytest.fixture(scope="module")
def setup_values_and_palettes(setup_test_paths):

    # DOCS:setup_begins

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

    reference_figure_dir = os.path.join(test_data_dir,    'reference_figures', 'test_legs_tutorial')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_legs_tutorial')

    py_tools.parallel_mkdir(generated_figure_dir)
    
    #Gaussian bell mock data
    npts = 1024
    half_npts = int(npts/2)
    x = np.linspace(-1., 1, half_npts+1)
    y = np.linspace(-1., 1, half_npts+1)
    xx, yy = np.meshgrid(x, y)
    gauss_bulge = np.exp(-(xx**2 + yy**2) / .6**2)
    
    #radar looking mock data
    sigma1 = .03
    sigma2 = .25
    np.random.seed(int(3.14159*100000))
    rand = np.random.normal(size=[npts,npts])
    xx, yy = np.meshgrid(np.linspace(-1.,1.,num=half_npts),np.linspace(1.,-1.,num=half_npts))
    kernel1 = np.exp(-1.*np.sqrt(xx**2.+yy**2.)/.02)
    kernel2 = np.exp(-1.*np.sqrt(xx**2.+yy**2.)/.15)
    reflectivity_like = (   scipy.signal.fftconvolve(rand,kernel1,mode='valid')
                          + scipy.signal.fftconvolve(rand,kernel2,mode='valid') )
    reflectivity_like = ( reflectivity_like
                          / np.max(np.absolute(reflectivity_like.max()))
                          * 62. )
    
    # figure properties
    mpl.rcParams.update({'font.size': 18})
    mpl.rcParams.update({'font.family':'Latin Modern Roman'})
    rec_w = 4.           #size of axes
    rec_h = 4.           #size of axes
    sp_w  = 2.           #horizontal space between axes
    sp_h  = 1.           #vertical space between axes
    
    # a function for formatting axes
    def format_axes(ax):
        for axis in ['top','bottom','left','right']:   
            ax.spines[axis].set_linewidth(.3)
        limits = (-1.,1.)           #data extent for axes
        dum = ax.set_xlim(limits)   # "dum =" to avoid printing output
        dum = ax.set_ylim(limits) 
        ticks  = [-1.,0.,1.]        #tick values
        dum = ax.set_xticks(ticks)
        dum = ax.set_yticks(ticks)

    # DOCS:setup_ends
    return (os, np, plt, mpl, legs, py_tools, 
            format_axes, gauss_bulge, reflectivity_like,
            rec_w, rec_h, sp_w, sp_h, 
            test_results_dir, 
            generated_figure_dir, reference_figure_dir)


def test_default_cm(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:default_cm_begins

    fig_w, fig_h = 5.6, 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    x0, y0 = .5/fig_w , .5/fig_h
    ax = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    format_axes(ax)
    
    #instantiate default color mapping
    mapping = legs.PalObj()
    
    #plot data & palette
    mapping.plot_data(ax=ax,data=gauss_bulge,
                      palette='right', 
                      pal_format='{:2.0f}') 
    

    generated_figure = os.path.join(generated_figure_dir, 'default.svg')
    plt.savefig(generated_figure)

    # DOCS:default_cm_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar


    # DOCS:fails_extending_begins
    
    #extend range of data to plot beyond 1.0
    extended_gauss_bulge = 1.4 * gauss_bulge - 0.2 # data range is now [-.2, 1.2]

    with pytest.raises(RuntimeError):
        mapping.plot_data(ax=ax,data=extended_gauss_bulge,
                      palette='right', pal_format='{:2.0f}') 
    # DOCS:fails_extending_ends


def test_extend_demo(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # same as in previous test
    extended_gauss_bulge = 1.4 * gauss_bulge - 0.2 # data range is now [-.2, 1.2]

    #----------------------------------------
    # DOCS:extend_demo_begins
    fig_w, fig_h = 12., 10.
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #mapping which extends the end-point color beyond the palette range
    x0, y0 = (.5+rec_w/2.+sp_w/2.)/fig_w , (.5+rec_h+sp_h)/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('Extend', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    mapping_ext = legs.PalObj(over_under='extend')
    mapping_ext.plot_data(ax=ax1,data=extended_gauss_bulge,
                          palette='right', pal_units='[unitless]',
                          pal_format='{:2.0f}')
    
    
    #mapping where end points are dealt with separately
    x0, y0 = .5/fig_w , .5/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('Extend Named Color', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    mapping_ext_2 = legs.PalObj(over_high='dark_red', under_low='dark_blue')
    mapping_ext_2.plot_data(ax=ax2,data=extended_gauss_bulge,
                            palette='right', pal_units='[unitless]',
                            pal_format='{:2.0f}')
    
    
    #as for all color specification, RBG values also work
    x0, y0 = (.5+rec_w+sp_w)/fig_w , .5/fig_h
    ax3 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax3.annotate('Extend using RGB', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax3)
    
    mapping_ext_3 = legs.PalObj(over_high=[255,198, 51], under_low=[ 13,171, 43])
    mapping_ext_3.plot_data(ax=ax3,data=extended_gauss_bulge,
                            palette='right', pal_units='[unitless]',
                            pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'default_extend.svg')
    plt.savefig(generated_figure)

    # DOCS:extend_demo_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure, 
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_default_exceptions(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:default_exceptions_begins

    fig_w, fig_h = 12., 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #Lets assume that data values in the range [0.2,0.3] are special
    #make a mapping where these values are assigned a special color
    x0, y0 = .5/fig_w , .5/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('1 exceptions inside \npalette range', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    #data values in the range 0.25+-0.05 are assigned the color blue
    mapping_1_except = legs.PalObj(excep_val=[.25],
                                   excep_tol=[.05],
                                   excep_col=[ 71,152,237])
    mapping_1_except.plot_data(ax=ax1,data=gauss_bulge,
                               palette='right', pal_units='[unitless]',
                               pal_format='{:2.0f}')
    
    
    #exceptions are usefull for NoData, missing values, etc
    #lets assing exception values to the Gaussian Bulge data
    gauss_bulge_with_exceptions = np.copy(gauss_bulge)
    gauss_bulge_with_exceptions[388:488, 25:125] = -9999.
    gauss_bulge_with_exceptions[388:488,150:250] = -6666.
    gauss_bulge_with_exceptions[388:488,275:375] = -3333.
    
    x0, y0 = (.5+rec_w+sp_w)/fig_w , .5/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('3 exceptions outside \npalette range', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    #a mapping where 3 exceptions are specified  
    #the defalut tolerance around specified value is 1e-3
    mapping_3_except = legs.PalObj(excep_val=[-9999.,      -6666.,    -3333.],
                                   excep_col=['dark_green','grey_80', 'light_pink'])
    mapping_3_except.plot_data(ax=ax2,data=gauss_bulge_with_exceptions,
                               palette='right', pal_units='[unitless]',
                               pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'default_exceptions.svg')
    plt.savefig(generated_figure)

    # DOCS:default_exceptions_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_default_exceptions(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:nine_legs_begins

    pal_w  = .25     #width of palette
    pal_sp = 1.2     #space between palettes
    fig_w, fig_h = 14., 5.  #size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    supported_colors = ['brown','blue','green','orange',
                        'red','pink','purple','yellow', 'b_w']
    for n, thisCol in enumerate(supported_colors):
        x0, y0 = (.5+n*(pal_w+pal_sp))/fig_w , .5/fig_h
        #color mapping with one color leg
        this_map = legs.PalObj(color_arr=thisCol)
        #plot palette only
        this_map.plot_palette(pal_pos=[x0,y0,pal_w/fig_w,rec_h/fig_h],
                              pal_units=thisCol,
                              pal_format='{:1.0f}')
    generated_figure = os.path.join(generated_figure_dir, 'default_linear_legs.svg')
    plt.savefig(generated_figure)

    # DOCS:nine_legs_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar


def test_n_col(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:n_col_begins

    fig_w, fig_h = 5.6, 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    x0, y0 = .5/fig_w , .5/fig_h
    ax = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    format_axes(ax)
    #mapping with 6 color legs
    mapping_default_6_colors = legs.PalObj(range_arr=[0.,60], n_col=6,
                                           over_high='extend',
                                           under_low='white')
    mapping_default_6_colors.plot_data(ax=ax,data=reflectivity_like,
                                       palette='right', pal_units='[dBZ]',
                                       pal_format='{:2.0f}')
    generated_figure = os.path.join(generated_figure_dir, 'default_6cols.svg')
    plt.savefig(generated_figure)
    # DOCS:n_col_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_color_arr(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:color_arr_begins

    fig_w, fig_h = 12., 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #mapping with 3 of the default color legs
    x0, y0 = .5/fig_w , .5/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('3 of the default \ncolor legs', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    mapping_3_colors = legs.PalObj(range_arr=[0.,60],
                                   color_arr=['brown','orange','red'],
                                   over_high='extend',
                                   under_low='white')
    mapping_3_colors.plot_data(ax=ax1,data=reflectivity_like,
                               palette='right', pal_units='[dBZ]',
                               pal_format='{:2.0f}')
    
    
    #mapping with custom pastel color legs
    x0, y0 = (.5+rec_w+sp_w)/fig_w , .5/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('Custom pastel \ncolor legs', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    #Custom pastel colors 
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    mapping_pastel = legs.PalObj(range_arr=[0.,60],
                                 color_arr=pastel,
                                 over_high='extend',
                                 under_low='white')
    #plot data & palette
    mapping_pastel.plot_data(ax=ax2,data=reflectivity_like,
                             palette='right', pal_units='[dBZ]',
                             pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'col_arr_demo.svg')
    plt.savefig(generated_figure)
    # DOCS:color_arr_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_solid(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:solid_begins

    fig_w, fig_h = 12., 10.
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #mapping with solid dark colors
    x0, y0 = .5/fig_w , (.5+rec_h+sp_h)/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('Using default dark colors', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    mapping_solid_dark = legs.PalObj(range_arr=[0.,60],
                                     color_arr=['brown','orange','red'],
                                     solid='col_dark',
                                     over_high='extend',
                                     under_low='white')
    mapping_solid_dark.plot_data(ax=ax1,data=reflectivity_like,
                                 palette='right', pal_units='[dBZ]',
                                 pal_format='{:2.0f}')
    
    
    #mapping with solid light colors
    x0, y0 = (.5+rec_w+sp_w)/fig_w , (.5+rec_h+sp_h)/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('Using default light colors', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    mapping_solid_light = legs.PalObj(range_arr=[0.,60],
                                      color_arr=['green','orange','purple'],
                                      solid=    'col_light',
                                      over_high='extend',
                                      under_low='white')
    mapping_solid_light.plot_data(ax=ax2,data=reflectivity_like,
                                  palette='right', pal_units='[dBZ]',
                                  pal_format='{:2.0f}')
    
    
    #mapping with custom solid colors
    x0, y0 = (.5+rec_w/2.+sp_w/2.)/fig_w , .5/fig_h
    ax3 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax3.annotate('Using custom solid colors', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax3)
    #colors from www.colorbrewer2.org
    magenta =[ [253, 224, 239],  #pale magenta
               [241, 182, 218],  
               [222, 119, 174],  
               [197,  27, 125],
               [142,   1,  82] ] #dark magenta
    mapping_solid_custom = legs.PalObj(range_arr=[0.,60],
                                       color_arr= magenta,
                                       solid=    'supplied',
                                       over_high='extend',
                                       under_low='white')
    mapping_solid_custom.plot_data(ax=ax3,data=reflectivity_like,
                                   palette='right', pal_units='[dBZ]',
                                   pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'solid_demo.svg')
    plt.savefig(generated_figure)

    # DOCS:solid_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_dark_pos(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:dark_pos_begins

    fig_w, fig_h = 12., 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    # two color divergent mapping
    x0, y0 = .5/fig_w , .5/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('Divergent mapping \nusing defaul colors', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    mapping_div_2_colors = legs.PalObj(range_arr=[-50.,50],
                                       color_arr=['orange','blue'],
                                       dark_pos =['low',   'high'],
                                       over_under='extend')
    mapping_div_2_colors.plot_data(ax=ax1,data=reflectivity_like,
                                   palette='right', pal_units='[dBZ]',
                                   pal_format='{:2.0f}')
    
    
    #Custom pastel colors 
    x0, y0 = (.5+rec_w+sp_w)/fig_w , .5/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('Divergent mapping with \ncustom color ', size=18,
                       xy=(.17/rec_w, 3.35/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    pastel = [ [[255,255,255],[147, 78,172]],  # white, purple
               [[255,255,255],[ 61,189, 63]] ] # white, green
    mapping_pastel = legs.PalObj(range_arr=[-50.,50],
                                 color_arr=pastel,
                                 dark_pos =['low','high'],
                                 over_under='extend')
    mapping_pastel.plot_data(ax=ax2,data=reflectivity_like,
                             palette='right', pal_units='[dBZ]',
                             pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'dark_pos_demo.svg')
    plt.savefig(generated_figure)
    # DOCS:dark_pos_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_solid_divergent(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:solid_divergent_begins

    fig_w, fig_h = 12., 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #mapping with custom colors
    x0, y0 = (.5+rec_w/2.+sp_w/2.)/fig_w , .5/fig_h
    ax = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    format_axes(ax)
    
    # these colors were defined using inkscape. 
    # www.colorbrewer2.org is also a great place for getting such color mappings
    green_purple =[ [114,  30, 179],  #dark purple
                    [172,  61, 255],
                    [210, 159, 255],
                    [255, 215, 255],  #pale purple
                    [255, 255, 255],  #white
                    [218, 255, 207],  #pale green
                    [162, 222, 134],
                    [111, 184,   0],
                    [  0, 129,   0] ] #dark green
    
    mapping_divergent_solid = legs.PalObj(range_arr=[-60.,60],
                                          color_arr= green_purple,
                                          solid=    'supplied',
                                          over_under='extend')
    mapping_divergent_solid.plot_data(ax=ax,data=reflectivity_like,
                                      palette='right', pal_units='[dBZ]',
                                      pal_format='{:2.0f}')
    
    
    generated_figure = os.path.join(generated_figure_dir, 'solid_divergent.svg')
    plt.savefig(generated_figure)
    # DOCS:solid_divergent_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar


def test_unequal_range(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:unequal_range_begins
    
    #ensure strictky +ve reflectivity values
    reflectivity_like_pve = np.where(reflectivity_like <= 0., 0., reflectivity_like)
    #convert reflectivity in dBZ to precipitation rates in mm/h (Marshall-Palmer, 1949)
    precip_rate =  10.**(reflectivity_like_pve/16.) / 27.424818
    
    fig_w, fig_h = 5.8, 5.#size of figure
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    #mapping with color legs spanning different ranges of values
    x0, y0 = .5/fig_w , .5/fig_h
    ax = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    format_axes(ax)
    mapping_diff_ranges = legs.PalObj(range_arr=[.1,3.,6.,12.,25.,50.,100.],
                                      n_col=6,
                                      over_high='extend',
                                      under_low='white')
    # the keyword "equal_legs" makes the legs have equal space in the palette even 
    # when they cover different value ranges
    mapping_diff_ranges.plot_data(ax=ax,data=precip_rate,
                                  palette='right', pal_units='[mm/h]',
                                  pal_format='{:2.0f}',
                                  equal_legs=True)
    generated_figure = os.path.join(generated_figure_dir, 'different_ranges.svg')
    plt.savefig(generated_figure)
    # DOCS:unequal_range_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

def test_separate(setup_values_and_palettes):
    (os, np, plt, mpl, legs, py_tools, 
     format_axes, gauss_bulge, reflectivity_like,
     rec_w, rec_h, sp_w, sp_h, 
     test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:separate_begins

    fig_w, fig_h = 12., 10.
    fig = plt.figure(figsize=(fig_w, fig_h))
    
    
    # black and white mapping 
    # without the **palette** keyword, **plot_data** only plots data. 
    x0, y0 = .5/fig_w , (.5+rec_h+sp_h)/fig_h
    ax1 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax1.annotate('Black & white mapping', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax1)
    mapping_bw = legs.PalObj(range_arr=[0.,1.], color_arr='b_w')
    mapping_bw.plot_data(ax=ax1,data=gauss_bulge)
    
    #get RGB image using the to_rgb method
    gauss_rgb = mapping_bw.to_rgb(gauss_bulge)
    
    
    #color mapping using 6 default linear color segments
    # this time, data is plotted by hand
    x0, y0 = (.5+rec_w+sp_w)/fig_w , (.5+rec_h+sp_h)/fig_h
    ax2 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax2.annotate('6 Colors', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax2)
    mapping_ref = legs.PalObj(range_arr=[0.,60],n_col=6, over_under='extend')
    reflectivity_rgb = mapping_ref.to_rgb(reflectivity_like)
    x1, x2 = ax2.get_xlim()
    y1, y2 = ax2.get_ylim()
    dum = ax2.imshow(reflectivity_rgb, interpolation='nearest',
                     origin='upper', extent=[x1,x2,y1,y2] )
    ax2.set_aspect('auto')  #force matplotlib to respect the axes that was defined
    
    
    #As a third panel, let's combine the two images
    x0, y0 = (.5+rec_w/2.)/fig_w , .5/fig_h
    ax3 = fig.add_axes([x0,y0,rec_w/fig_w,rec_h/fig_h])
    dum = ax3.annotate('combined image', size=18,
                       xy=(.17/rec_w, 3.65/rec_h), xycoords='axes fraction',
                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    format_axes(ax3)
    
    #blend the two images by hand
    #image will be opaque where reflectivity > 0
    alpha = np.where(reflectivity_like >= 0., 1., 0.)
    alpha = np.where(np.logical_and(reflectivity_like >= 0., reflectivity_like < 10.), 0.1*reflectivity_like, alpha)
    combined_rgb = np.zeros(gauss_rgb.shape,dtype='uint8')
    for zz in np.arange(3):
        combined_rgb[:,:,zz] = (1. - alpha)*gauss_rgb[:,:,zz] + alpha*reflectivity_rgb[:,:,zz]
    
    #plot image w/ imshow
    x1, x2 = ax3.get_xlim()
    y1, y2 = ax3.get_ylim()
    dum = ax3.imshow(combined_rgb, interpolation='nearest', 
                     origin='upper', extent=[x1,x2,y1,y2])
    ax3.set_aspect('auto') 
    
    #plot palettes with the plot_palette method
    pal_w  = .25/fig_w   #width of palette
    x0, y0 = x0+rec_w/fig_w+.25/fig_w  , .5/fig_h
    mapping_bw.plot_palette(pal_pos=[x0,y0,pal_w,rec_h/fig_h],
                           pal_units='unitless',
                           pal_format='{:2.0f}') 
    x0, y0 = x0+1.2/fig_w  , .5/fig_h
    mapping_ref.plot_palette(pal_pos=[x0,y0,pal_w,rec_h/fig_h],
                            pal_units='dBZ',
                            pal_format='{:3.0f}') 
    
    
    generated_figure = os.path.join(generated_figure_dir, 'separate_data_palettes.svg')
    plt.savefig(generated_figure)
    # DOCS:separate_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))
    assert images_are_similar

