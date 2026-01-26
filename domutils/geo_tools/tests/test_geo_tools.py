# to run only one test
#
# pytest test_geo_tools.py::test_projinds_simple_example 
# 
# can also be added to __main__ section below




import pytest

@pytest.fixture(scope="module")
def setup_values_and_palettes(setup_test_paths):

    # DOCS:values_and_palette_begins
    import os 
    import domutils.legs as legs
    import domutils._py_tools as py_tools

    # where is the data
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_geo_tools')
    reference_figure_dir = os.path.join(test_data_dir,    'reference_figures', 'test_geo_tools')

    py_tools.parallel_mkdir(generated_figure_dir)

    # DOCS:values_and_palette_ends

    return (test_data_dir, test_results_dir, 
            generated_figure_dir, reference_figure_dir)

def test_projinds_simple_example(setup_values_and_palettes):
    (test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:simple_projinds_example_begins
    import os
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools
    import domutils._py_tools as py_tools
    
    # make mock data and coordinates
    # note that there is some regularity to the grid 
    # but that it does not conform to any particular projection
    regular_lons =     [ [-91. , -91  , -91   ],
                         [-90. , -90  , -90   ],
                         [-89. , -89  , -89   ] ]
    regular_lats =     [ [ 44  ,  45  ,  46   ],
                         [ 44  ,  45  ,  46   ],
                         [ 44  ,  45  ,  46   ] ]
    data_vals =        [ [  6.5,   3.5,    .5 ],
                         [  7.5,   4.5,   1.5 ],
                         [  8.5,   5.5,   2.5 ] ]
    missing = -9999.
    
    #pixel resolution of image that will be shown in the axes
    img_res = (800,600)
    #point density for entire figure
    mpl.rcParams['figure.dpi'] = 800
    
    #projection and extent of map being displayed
    proj_aea = cartopy.crs.AlbersEqualArea(central_longitude=-94.,
                                           central_latitude=35.,
                                           standard_parallels=(30.,40.))
    map_extent=[-94.8,-85.2,43,48.]
    
    #-------------------------------------------------------------------
    #regular lat/lons are boring, lets rotate the coordinate system about
    # the central data point
    
    #use cartopy transforms to get xyz coordinates
    proj_ll = cartopy.crs.Geodetic()
    geo_cent = proj_ll.as_geocentric()
    x, y, z = geo_tools.latlon_to_unit_sphere_xyz(np.asarray(regular_lons),
                                                  np.asarray(regular_lats),
                                                  combined=False)
    
    # rotate points by 45 degrees counter clockwise
    theta = np.pi/4
    rotation_matrix = geo_tools.rotation_matrix([x[1,1],
                                                 y[1,1],
                                                 z[1,1]],
                                                 theta)
    rotated_xyz = np.zeros((3,3,3))
    for ii, (lat_arr, lon_arr) in enumerate(zip(regular_lats, regular_lons)):
        for jj, (this_lat, this_lon) in enumerate(zip(lat_arr, lat_arr)):
            rotated_xyz[ii,jj,:] = np.matmul(rotation_matrix,[x[ii,jj],
                                                              y[ii,jj],
                                                              z[ii,jj]])
    
    #from xyz to lat/lon
    rotatedLons, rotatedLats = geo_tools.unit_sphere_xyz_to_latlon(rotated_xyz[:,:,0],
                                                                   rotated_xyz[:,:,1],
                                                                   rotated_xyz[:,:,2],
                                                                   combined=False)
    # done rotating
    #-------------------------------------------------------------------
    
    #larger characters
    mpl.rcParams.update({'font.size': 15})
    
    #instantiate figure
    fig = plt.figure(figsize=(7.5,6.))
    
    #instantiate object to handle geographical projection of data
    # onto geoAxes with this specific crs and extent
    proj_inds = geo_tools.ProjInds(src_lon=rotatedLons, src_lat=rotatedLats,
                                   extent=map_extent, dest_crs=proj_aea,
                                   image_res=img_res)
    
    #axes for this plot
    ax = fig.add_axes([.01,.1,.8,.8], projection=proj_aea)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_aea)
    
    # Set up colormapping object 
    color_mapping = legs.PalObj(range_arr=[0.,9.],
                                 color_arr=['brown','blue','green','orange',
                                            'red','pink','purple','yellow','b_w'],
                                 solid='col_dark',
                                 excep_val=missing, excep_col='grey_220')
    
    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(data_vals)
    
    #plot data & palette
    color_mapping.plot_data(ax=ax,data=proj_data,
                            palette='right', pal_units='[unitless]', 
                            pal_format='{:4.0f}')   #palette options
    
    #add political boundaries
    dum = ax.add_feature(cartopy.feature.STATES.with_scale('50m'), 
                         linewidth=0.5, edgecolor='0.2',zorder=1)
    
    #plot border and mask everything outside model domain
    proj_inds.plot_border(ax, mask_outside=False, linewidth=2.)

    
    # save figure
    generated_figure = os.path.join(generated_figure_dir, 'test_projinds_simple_example.svg')
    plt.savefig(generated_figure)

    # DOCS:simple_projinds_example_ends

    # the testing needs not be included in docs
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure, 
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar
    
def test_simple_nearest_neighbor_interpolation():

    # DOCS:simple_nearest_neighbor_interpolation_begins
    import numpy as np
    import domutils.geo_tools as geo_tools
    
    # Source data on a very simple grid
    src_lon =     [ [-90.1 , -90.1  ],
                    [-89.1 , -89.1  ] ]
    
    src_lat =     [ [ 44.1  , 45.1  ],
                    [ 44.1  , 45.1  ] ]
    
    data    =     [ [  3    ,  1    ],
                    [  4    ,  2    ] ]
    
    # destination grid where we want data
    # Its larger than the source grid and slightly offset
    dest_lon =     [ [-91., -91, -91, -91  ],
                     [-90., -90, -90, -90  ],
                     [-89., -89, -89, -89  ],
                     [-88., -88, -88, -88  ] ]
    
    dest_lat =     [ [ 43 ,  44,  45,  46 ],
                     [ 43 ,  44,  45,  46 ],
                     [ 43 ,  44,  45,  46 ],
                     [ 43 ,  44,  45,  46 ] ]
    
    #instantiate object to handle interpolation
    proj_inds = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                   dest_lon=dest_lon, dest_lat=dest_lat,
                                   missing=-99.)
    #interpolate data with "project_data"
    interpolated = proj_inds.project_data(data)
    #nearest neighbor output, pts outside the domain are set to missing
    #Interpolation with border detection in all directions
    expected = np.array([[-99., -99., -99., -99.,],
                         [-99.,   3.,   1., -99.,],
                         [-99.,   4.,   2., -99.,],
                         [-99., -99., -99., -99.,]])
    assert np.allclose(interpolated, expected)
    
    
    #on some domain, border detection is not desirable, it can be turned off
    #
    # extend_x here refers to the dimension in data space (longitudes) that are
    # represented along rows of python array.
    
    # for example:
    
    # Border detection in Y direction (latitudes) only
    proj_inds_ext_y = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                         dest_lon=dest_lon, dest_lat=dest_lat,
                                         missing=-99.,
                                         extend_x=False)
    interpolated_ext_y = proj_inds_ext_y.project_data(data)
    expected = np.array([[-99.,  3.,  1.,-99.],
                         [-99.,  3.,  1.,-99.],
                         [-99.,  4.,  2.,-99.],
                         [-99.,  4.,  2.,-99.]])
    assert np.allclose(interpolated_ext_y, expected)
    #
    # Border detection in X direction (longitudes) only
    proj_inds_ext_x = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                         dest_lon=dest_lon, dest_lat=dest_lat,
                                         missing=-99.,
                                         extend_y=False)
    interpolated_ext_x = proj_inds_ext_x.project_data(data)
    expected = np.array([[-99., -99., -99., -99.],
                         [  3.,   3.,   1.,   1.],
                         [  4.,   4.,   2.,   2.],
                         [-99., -99., -99., -99.]])
    assert np.allclose(interpolated_ext_x, expected)
    # 
    # no border detection
    proj_inds_no_b = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                        dest_lon=dest_lon, dest_lat=dest_lat,
                                        missing=-99.,
                                        extend_x=False, extend_y=False)
    interpolated_no_b = proj_inds_no_b.project_data(data)
    expected = np.array([[3., 3., 1., 1.],
                         [3., 3., 1., 1.],
                         [4., 4., 2., 2.],
                         [4., 4., 2., 2.]])

    assert np.allclose(interpolated_no_b, expected)
    # DOCS:simple_nearest_neighbor_interpolation_ends



def test_averaging_interpolation():

    # DOCS:averaging_interpolation_begins

    import numpy as np
    import domutils.geo_tools as geo_tools

    # source data on a very simple grid
    src_lon =     [ [-88.2 , -88.2  ],
                    [-87.5 , -87.5  ] ]
    
    src_lat =     [ [ 43.5  , 44.1  ],
                    [ 43.5  , 44.1  ] ]
    
    data    =     [ [  3    ,  1    ],
                    [  4    ,  2    ] ]
    
    # coarser destination grid where we want data
    dest_lon =     [ [-92. , -92  , -92 , -92  ],
                     [-90. , -90  , -90 , -90  ],
                     [-88. , -88  , -88 , -88  ],
                     [-86. , -86  , -86 , -86  ] ]
    
    dest_lat =     [ [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ] ]
    
    #instantiate object to handle interpolation
    #Note the average keyword set to true
    proj_inds = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                   dest_lon=dest_lon, dest_lat=dest_lat,
                                   average=True, missing=-99.)
    
    #interpolate data with "project_data"
    interpolated = proj_inds.project_data(data)
    
    #Since all high resolution data falls into one of the output 
    #grid tile, they are all aaveraged together:  (1+2+3+4)/4 = 2.5 
    expected = np.array([[-99., -99.  ,-99., -99. ],
                         [-99., -99.  ,-99., -99. ],
                         [-99.,   2.5 ,-99., -99. ],
                         [-99., -99.  ,-99., -99. ]])
    assert np.allclose(interpolated, expected)
    
    #weighted average can be obtained by providing weights for each data pt 
    #being averaged
    weights   =     [ [  0.5   ,  1.    ],
                      [  1.    ,  0.25  ] ]
    
    weighted_avg = proj_inds.project_data(data, weights=weights)
    #result is a weighted average:  
    # (1.*1 + 0.25*2 + 0.5*3 + 1.*4) / (1.+0.25+0.5+1.) = 7.0/2.75 = 2.5454
    expected = np.array([[-99., -99.        , -99., -99. ],
                         [-99., -99.        , -99., -99. ],
                         [-99.,   2.54545455, -99., -99. ],
                         [-99., -99.        , -99., -99. ]])
    assert np.allclose(weighted_avg, expected)

    # DOCS:averaging_interpolation_ends

def test_smooth_radius_interpolation():

    # DOCS:smooth_radius_interpolation_begins
    import numpy as np
    import domutils.geo_tools as geo_tools
    
    # source data on a very simple grid
    src_lon =     [ [-88.2 , -88.2  ],
                    [-87.5 , -87.5  ] ]
    
    src_lat =     [ [ 43.5  , 44.1  ],
                    [ 43.5  , 44.1  ] ]
    
    data    =     [ [  3    ,  1    ],
                    [  4    ,  2    ] ]
    
    # coarser destination grid where we want data
    dest_lon =     [ [-92. , -92  , -92 , -92  ],
                     [-90. , -90  , -90 , -90  ],
                     [-88. , -88  , -88 , -88  ],
                     [-86. , -86  , -86 , -86  ] ]
    
    dest_lat =     [ [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ],
                     [ 42  ,  44  ,  46 ,  48 ] ]
    
    #instantiate object to handle interpolation
    #All source data points found within 300km of each destination 
    #grid tiles will be averaged together
    proj_inds = geo_tools.ProjInds(src_lon=src_lon,    src_lat=src_lat,
                                   dest_lat=dest_lat,  dest_lon=dest_lon,
                                   smooth_radius=300., missing=-99.)
    
    #interpolate and smooth data with "project_data"
    interpolated = proj_inds.project_data(data)
    
    #output is smoother than data source
    expected = np.array([[-99.       ,  -99. , -99.,  -99. ],
                        [ 2.66666667,    2.5,   1.5, -99. ],
                        [ 2.5       ,    2.5,   2.5, -99. ],
                        [ 2.5       ,    2.5,   1.5, -99. ]])
    assert np.allclose(interpolated, expected)


    # DOCS:smooth_radius_interpolation_ends
    

def test_no_extent_in_cartopy_projection(setup_values_and_palettes):
    (test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    '''
    make sure ProjInds works with projections requiring no extent
    '''

    import os
    import numpy as np
    from packaging import version
    import cartopy
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools
    import domutils._py_tools as py_tools


    mpl.rcParams.update({'font.size': 15})

    regular_lons =     [ [-100., -100 , -100  ],
                         [-90. , -90  , -90   ],
                         [-80. , -80  , -80   ] ]
    regular_lats =     [ [ 30  ,  40  ,  50   ],
                         [ 30  ,  40  ,  50   ],
                         [ 30  ,  40  ,  50   ] ]
    data_vals =        [ [  6.5,   3.5,    .5 ],
                         [  7.5,   4.5,   1.5 ],
                         [  8.5,   5.5,   2.5 ] ]
    missing = -9999.
    image_ratio = .5
    rec_w = 6.4     #inches!
    rec_h = image_ratio*rec_w     #inches!
    grid_w_pts = 2000.
    image_res = [grid_w_pts,image_ratio*grid_w_pts] #100 x 50
    
    #cartopy projection with no extent
    proj_rob = cartopy.crs.Robinson()
    
    #instantiate object to handle geographical projection of data
    # onto geoAxes with this specific crs 
    proj_inds = geo_tools.ProjInds(src_lon=regular_lons, src_lat=regular_lats, 
                                   dest_crs=proj_rob,    image_res=image_res,
                                   extend_x=False, extend_y=False)
    
    #geographical projection of data into axes space
    projected_data = proj_inds.project_data(data_vals)

    #plot data to make sure it works
    #the image that is generated can be looked at to insure proper functionning of the test
    #it is not currently tested
    color_map = legs.PalObj(range_arr=[0.,9.],
                            color_arr=['brown','blue','green','orange',
                                       'red','pink','purple','yellow','b_w'],
                            excep_val=missing, excep_col='grey_220')
    fig_w = 9.
    fig_h = image_ratio * fig_w
    fig = plt.figure(figsize=(fig_w, fig_h))
    pos = [.1, .1, rec_w/fig_w, rec_h/fig_h]
    ax = fig.add_axes(pos, projection=proj_rob)
    x1, x2, y1, y2 = ax.get_extent()
    #thinner lines
    if version.parse(cartopy.__version__) >= version.parse("0.18.0"):
        ax.spines['geo'].set_linewidth(0.3)
    else:
        ax.outline_patch.set_linewidth(0.3) 
    projected_rgb = color_map.to_rgb(projected_data)
    ax.imshow(projected_rgb, interpolation='nearest', aspect='auto', 
              extent=[x1,x2,y1,y2], origin='upper')
    ax.coastlines(resolution='110m', linewidth=0.3, edgecolor='0.3',zorder=10)
    color_map.plot_palette(data_ax=ax)

    generated_figure = os.path.join(generated_figure_dir, 'test_no_extent_in_cartopy_projection.svg')

    plt.savefig(generated_figure, dpi=500)
    plt.close(fig)

    # compare with reference figure
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

    
def test_general_lam_projection(setup_values_and_palettes):
    (test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    import os
    import pickle
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy
    import domutils._py_tools as py_tools
    
    # In your scripts use something like :
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools

    pickle_file  = os.path.join(test_data_dir, 'pal_demo_data.pickle')
    with open(pickle_file, 'rb') as f:
        data_dict = pickle.load(f)
    longitudes     = data_dict['longitudes']    #2D longitudes [deg]
    latitudes      = data_dict['latitudes']     #2D latitudes  [deg]
    ground_mask    = data_dict['groundMask']    #2D land fraction [0-1]; 1 = all land
    terrain_height = data_dict['terrainHeight'] #2D terrain height of model [m ASL]
    
    #flag non-terrain (ocean and lakes) as -3333.
    inds = np.asarray( (ground_mask.ravel() <= .01) ).nonzero()
    if inds[0].size != 0:
        terrain_height.flat[inds] = -3333.

    #missing value
    missing = -9999.
    
    #pixel density of image to plot
    ratio = 0.8
    hpix = 600.       #number of horizontal pixels
    vpix = ratio*hpix #number of vertical pixels
    img_res = (int(hpix),int(vpix))
    
    ##define Albers projection and extend of map
    #Obtained through trial and error for good fit of the mdel grid being plotted
    proj_aea = cartopy.crs.AlbersEqualArea(central_longitude=-94.,
                                           central_latitude=35.,
                                           standard_parallels=(30.,40.))
    map_extent=[-104.8,-75.2,27.8,48.5]

    #point density for figure
    mpl.rcParams['figure.dpi'] = 400
    #larger characters
    mpl.rcParams.update({'font.size': 15})

    #instantiate figure
    fig = plt.figure(figsize=(7.5,6.))

    #instantiate object to handle geographical projection of data
    proj_inds = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
                                   extent=map_extent,  dest_crs=proj_aea,
                                   image_res=img_res,  missing=missing)
    
    #axes for this plot
    ax = fig.add_axes([.01,.1,.8,.8], projection=proj_aea)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_aea)
    
    # Set up colormapping object
    #
    # Two color segments for this palette
    red_green = [[[227,209,130],[ 20, 89, 69]],    # bottom color leg : yellow , dark green
                 [[227,209,130],[140, 10, 10]]]    #    top color leg : yellow , dark red

    map_terrain = legs.PalObj(range_arr=[0., 750, 1500.],
                              color_arr=red_green, dark_pos=['low','high'],
                              excep_val=[-3333.       ,missing],
                              excep_col=[[170,200,250],[120,120,120]],  #blue , grey_120
                              over_high='extend')
    
    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(terrain_height)
    
    #plot data & palette
    map_terrain.plot_data(ax=ax,data=proj_data, zorder=0,
                         palette='right', pal_units='[meters]', pal_format='{:4.0f}')   #palette options
    
    #add political boundaries
    ax.add_feature(cartopy.feature.STATES.with_scale('50m'), linewidth=0.5, edgecolor='0.2',zorder=1)
    
    #plot border and mask everything outside model domain
    proj_inds.plot_border(ax, mask_outside=True, linewidth=.5)
    
    #uncomment to save figure
    generated_figure = os.path.join(generated_figure_dir, 'test_general_lam_projection.svg')

    plt.savefig(generated_figure)

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure, 
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

def test_basic_projection():
    '''
    make sure ProjInds projects data correctly for a very simple case
    with provided source and destination grids
    '''

    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools


    #destination grid
    dest_lon =     [ [-100., -100 , -100  ],
                     [-90. , -90  , -90   ],
                     [-80. , -80  , -80   ] ]
    dest_lat =     [ [ 30  ,  40  ,  50   ],
                     [ 30  ,  40  ,  50   ],
                     [ 30  ,  40  ,  50   ] ]

    #source data
    src_lon =      [ [-101., -101 ],
                     [-88. , -88  ] ] 
    src_lat =      [ [ 30  ,  40  ],
                     [ 30  ,  40  ] ]
    src_data =     [ [  1.,  2], 
                     [  3,   4] ]
    
    #instantiate object to handle geographical projection of data
    proj_inds = geo_tools.ProjInds(src_lon = src_lon, src_lat = src_lat, 
                                   dest_lon=dest_lon, dest_lat=dest_lat,
                                   extend_x=False, extend_y=False)
    
    #geographical projection of data into axes space
    projected_data = proj_inds.project_data(src_data)

    #reference data when this works
    expected =     [ [  1., 2., 2.], 
                     [  3., 4., 4.],
                     [  3., 4., 4.] ]

    ##test that sum of projected_data equals some pre-validated value
    assert projected_data.tolist() == expected

def test_1d_inputs():
    '''
    make sure ProjInds accepts 1D inputs for lat/lon and data
    This example is otherwise the same as above
    '''

    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools


    #destination grid
    dest_lon =     [ [-100., -100 , -100  ],
                     [-90. , -90  , -90   ],
                     [-80. , -80  , -80   ] ]
    dest_lat =     [ [ 30  ,  40  ,  50   ],
                     [ 30  ,  40  ,  50   ],
                     [ 30  ,  40  ,  50   ] ]

    #source data
    src_lon =      np.array([ [-101., -101 ],
                              [-88. , -88  ] ]).ravel()
    src_lat =      np.array([ [ 30  ,  40  ],
                              [ 30  ,  40  ] ]).ravel()
    src_data =     np.array([ [  1.,  2], 
                              [  3,   4] ]).ravel()
    
    #instantiate object to handle geographical projection of data
    proj_inds = geo_tools.ProjInds(src_lon = src_lon, src_lat = src_lat, 
                                   dest_lon=dest_lon, dest_lat=dest_lat,
                                   extend_x=False, extend_y=False)
    
    #geographical projection of data into axes space
    projected_data = proj_inds.project_data(src_data)

    #reference data when this works
    expected =     [ [  1., 2., 2.], 
                     [  3., 4., 4.],
                     [  3., 4., 4.] ]

    ##test that sum of projected_data equals some pre-validated value
    assert projected_data.tolist() == expected

    


@pytest.mark.timeout(5, method="thread")
def test_hrdps_projection_in_reasonable_time(setup_values_and_palettes):
    """ Test fails if it takes too long to generate projections
    """
    (test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    import os
    import pickle
    import time
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy
    import domutils._py_tools as py_tools
    
    # In your scripts use something like :
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools

    #recover previously prepared data
    pickle_file  = os.path.join(test_data_dir, 'radar_continental_2.5km_2882x2032.pickle')
    with open(pickle_file, 'rb') as f:
        data_dict = pickle.load(f)
    longitudes     = data_dict['lon']    #2D longitudes [deg]
    latitudes      = data_dict['lat']     #2D latitudes  [deg]
    
    #Setup geographical projection 
    # Full HRDPS grid
    pole_latitude=35.7
    pole_longitude=65.5
    lat_0 = 48.8
    delta_lat = 10.
    lon_0 = 266.00
    delta_lon = 40.
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    proj_aea = cartopy.crs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    t1 = time.time()
    proj_obj = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
                                  extent=map_extent, dest_crs=proj_aea, 
                                  image_res=(800,400))
    t2 = time.time()
    print(f'Making projection object took {t2-t1} seconds')


def test_simple_nn_projection():
    import numpy as np
    import domutils.geo_tools as geo_tools
    
    # Source data on a very simple grid
    src_lon =     [ [-90.1 , -90.1  ],
                    [-89.1 , -89.1  ] ]
    
    src_lat =     [ [ 44.1  , 45.1  ],
                    [ 44.1  , 45.1  ] ]
    
    data    =     [ [  3    ,  1    ],
                    [  4    ,  2    ] ]
    
    # destination grid where we want data
    # Its larger than the source grid and slightly offset
    dest_lon =     [ [-91. , -91  , -91 , -91  ],
                     [-90. , -90  , -90 , -90  ],
                     [-89. , -89  , -89 , -89  ],
                     [-88. , -88  , -88 , -88  ] ]
    
    dest_lat =     [ [ 43  ,  44  ,  45 ,  46 ],
                     [ 43  ,  44  ,  45 ,  46 ],
                     [ 43  ,  44  ,  45 ,  46 ],
                     [ 43  ,  44  ,  45 ,  46 ] ]
    
    #instantiate object to handle interpolation
    proj_inds = geo_tools.ProjInds(src_lon=src_lon,   src_lat=src_lat,
                                  dest_lon=dest_lon, dest_lat=dest_lat,
                                  missing=-99.)
    #interpolate data with "project_data"
    interpolated = proj_inds.project_data(data)
    #nearest neighbor output, pts outside the domain are set to missing
    #Interpolation with border detection in all directions
    expected =  [[-99., -99., -99., -99.],
                 [-99.,   3.,   1., -99.],
                 [-99.,   4.,   2., -99.],
                 [-99., -99., -99., -99.]]

    assert interpolated.tolist() == expected


def test_latlon_to_xyz():
    import numpy as np
    import domutils.geo_tools as geo_tools

    test_points = { "equator_prime":        (0.0,   0.0),
                    "equator_90E":          (90.0,  0.0),
                    "equator_180":          (180.0, 0.0),
                    "equator_180_neg":      (-180.0, 0.0),
                    "north_pole":           (0.0,   90.0),
                    "south_pole":           (0.0,  -90.0),
                    "near_north_pole":      (45.0,  89.999999),
                    "near_south_pole":      (-30.0, -89.999999),
                    "antimeridian_pos":     (179.999999, 10.0),
                    "antimeridian_neg":     (-179.999999, -10.0),
                }

    for name, (lon, lat) in test_points.items():
        xyz = geo_tools.latlon_to_unit_sphere_xyz(lon, lat, combined=True)
        lon2, lat2 = geo_tools.unit_sphere_xyz_to_latlon(xyz, combined=True)

        # results are the same to 6 digits
        assert np.round(lat*1e6) == np.round(lat2*1e6)
        assert np.round(lon*1e6) == np.round(lon2*1e6)

    for name, (lon, lat) in test_points.items():
        x, y, z = geo_tools.latlon_to_unit_sphere_xyz(lon, lat, combined=False)
        lon2, lat2 = geo_tools.unit_sphere_xyz_to_latlon(x, y, z, combined=False)

        # results are the same to 6 digits
        assert np.round(lat*1e6) == np.round(lat2*1e6)
        assert np.round(lon*1e6) == np.round(lon2*1e6)



if __name__ == '__main__':
    import os

    test_projinds_simple_example()
    #test_no_extent_in_cartopy_projection()

    #test_projinds_simple_example()
    #test_hrdps_projection_in_reasonable_time()
