
import unittest

class TestStringMethods(unittest.TestCase):

    def test_no_extent_in_cartopy_projection(self):
        '''
        make sure ProjInds works with projections requiring no extent
        '''

        import os
        import numpy as np
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt
        import domutils
        import domutils.legs as legs
        import domutils.geo_tools as geo_tools
        import domutils._py_tools as py_tools


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
        proj_rob = ccrs.Robinson()
        
        #instantiate object to handle geographical projection of data
        # onto geoAxes with this specific crs 
        ProjInds = geo_tools.ProjInds(src_lon=regular_lons, src_lat=regular_lats, 
                                      dest_crs=proj_rob,    image_res=image_res,
                                      extend_x=False, extend_y=False)
        
        #geographical projection of data into axes space
        projected_data = ProjInds.project_data(data_vals)

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
        ax.outline_patch.set_linewidth(.3)
        projected_rgb = color_map.to_rgb(projected_data)
        ax.imshow(projected_rgb, interpolation='nearest', aspect='auto', 
                  extent=[x1,x2,y1,y2], origin='upper')
        ax.coastlines(resolution='110m', linewidth=0.3, edgecolor='0.3',zorder=10)
        color_map.plot_palette(data_ax=ax)
        domutils_dir = os.path.dirname(domutils.__file__)
        package_dir  = os.path.dirname(domutils_dir)
        test_results_dir = package_dir+'/test_results/'
        if not os.path.isdir(test_results_dir):
            os.mkdir(test_results_dir)
        svg_name = test_results_dir+'/test_no_extent_in_cartopy_projection.svg'

        plt.savefig(svg_name, dpi=500)
        plt.close(fig)
        print('saved: '+svg_name)

        #compare image with saved reference
        #copy reference image to testdir
        reference_image = package_dir+'/test_data/_static/'+os.path.basename(svg_name)
        images_are_similar = py_tools.render_similarly(svg_name, reference_image)

        #test fails if images are not similar
        self.assertEqual(images_are_similar, True)

        
    def test_general_lam_projection(self):
        import os, inspect
        import pickle
        import numpy as np
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import domutils
        import domutils._py_tools as py_tools
        
        # In your scripts use something like :
        import domutils.legs as legs
        import domutils.geo_tools as geo_tools
        #recover previously prepared data
        domutils_dir = os.path.dirname(domutils.__file__)
        package_dir  = os.path.dirname(domutils_dir)+'/'
        source_file  = package_dir + '/test_data/pal_demo_data.pickle'
        with open(source_file, 'rb') as f:
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
        proj_aea = ccrs.AlbersEqualArea(central_longitude=-94.,
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
        ax.set_extent(map_extent)
        
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
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, edgecolor='0.2',zorder=1)
        
        #plot border and mask everything outside model domain
        proj_inds.plot_border(ax, mask_outside=True, linewidth=.5)
        
        #uncomment to save figure
        output_dir = package_dir+'test_results/'
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        image_name = output_dir+'test_general_lam_projection.svg'
        plt.savefig(image_name)
        plt.close(fig)
        print('saved: '+image_name)

        #compare image with saved reference
        #copy reference image to testdir
        reference_image = package_dir+'/test_data/_static/'+os.path.basename(image_name)
        images_are_similar = py_tools.render_similarly(image_name, reference_image)

        #test fails if images are not similar
        self.assertEqual(images_are_similar, True)

    def test_basic_projection(self):
        '''
        make sure ProjInds projects data correctly for a very simple case
        with provided source and destination grids
        '''

        import os
        import numpy as np
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt
        import domutils
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
        self.assertListEqual(projected_data.tolist(), expected)

        



if __name__ == '__main__':
    unittest.main()
