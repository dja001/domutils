
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
        image_res = [grid_w_pts,image_ratio*grid_w_pts]
        image_dpi = grid_w_pts / rec_w
        
        #cartopy projection with no extent
        proj_rob = ccrs.Robinson()
        
        #instantiate object to handle geographical projection of data
        # onto geoAxes with this specific crs 
        ProjInds = geo_tools.ProjInds(src_lon=regular_lons, src_lat=regular_lats, 
                                      dest_crs=proj_rob,    image_res=image_res)
        
        #geographical projection of data into axes space
        projected_data = ProjInds.project_data(data_vals)


        #
        #plot data to make sure it works
        #the image that is generated can be looked at to insure proper functionning of the test
        #it is not currently tested
        color_map = legs.PalObj(range_arr=[0.,9.],
                                     color_arr=['brown','blue','green','orange',
                                                'red','pink','purple','yellow','b_w'],
                                     solid='col_dark',
                                     excep_val=missing, excep_col='grey_220')
        fig_w = 8.
        fig_h = image_ratio * fig_w
        fig = plt.figure(figsize=(fig_w, fig_h))
        pos = [.1, .1, rec_w/fig_w, rec_h/fig_h]
        ax = fig.add_axes(pos, projection=proj_rob)
        ax.outline_patch.set_linewidth(.3)
        color_map.plot_data(ax=ax, data=projected_data, zorder=1)
        ax.coastlines(resolution='110m', linewidth=0.3, edgecolor='0.3',zorder=10)
        domutils_dir = os.path.dirname(domutils.__file__)
        test_results_dir = os.path.dirname(domutils_dir)+'/test_results/'
        if not os.path.isdir(test_results_dir):
            os.mkdir(test_results_dir)
        svg_name = test_results_dir+'/no_extent_in_cartopy_projection.svg'

        plt.savefig(svg_name, dpi=image_dpi)
        plt.close(fig)

        
        #test that sum of projected_data equals some pre-validated value
        self.assertAlmostEqual(np.sum(projected_data), -19719338616.0,places=12)


if __name__ == '__main__':
    unittest.main()
