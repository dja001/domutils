
import unittest

class TestStringMethods(unittest.TestCase):

    def test_make_radar_fst(self):
        ''' test funtion that make a fst file from odim h5 mosaic file

        I would need to find a way to test the entire script that parses arguments with argparse
        
        '''

        import os
        import numpy as np
        import datetime
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt
        import domutils
        import domutils.legs as legs
        import domutils.geo_tools as geo_tools
        import domcmc.fst_tools as fst_tools
        import domutils.radar_tools as radar_tools
        import domutils.radar_tools.make_radar_fst as make_radar_fst
        import domutils._py_tools as py_tools

        #setting up directories
        domutils_dir = os.path.dirname(domutils.__file__)
        package_dir  = os.path.dirname(domutils_dir)
        test_data_dir = package_dir+'/test_data/'
        test_results_dir = package_dir+'/test_results/make_radar_fst/'
        if not os.path.isdir(test_results_dir):
            os.mkdir(test_results_dir)

        #a small class that mimics the output of argparse
        class FstArgs():
            radar_data_dir = package_dir+'/test_data/odimh5_radar_composites/'
            output_dir = test_results_dir
            fst_file_struc = '%Y%m%d%H%M_mosaic.fst'
            h5_file_struc = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
            h5_latlon_file = test_data_dir+'radar_continental_2.5km_2882x2032.pickle'
            t0 = datetime.datetime(2019,10,31,16,0)
            tf = datetime.datetime(2019,10,31,16,0)
            fcst_len = None
            accum_len = None
            output_dt = 10
            sample_pr_file = test_data_dir+'hrdps_5p1_prp0.fst'
            ncores = 1
            complete_dataset = False
            median_filt = None
            smooth_radius = None
            figure_dir = test_results_dir
            figure_format = 'svg'

        args = FstArgs()

        #file containing the PR variable
        fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)

        #this command writes a fst file and makes a figure from it 
        make_radar_fst.to_fst(args.t0, fst_template, args)

        #pre saved figure
        new_figure = '/fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_results//make_radar_fst/20191031_1600.svg'

        #pre saved figure for what the results should be
        reference_image = package_dir+'/test_data/_static/'+os.path.basename(new_figure)

        #compare image with saved reference
        #copy reference image to testdir
        images_are_similar = py_tools.render_similarly(new_figure, reference_image)

        #test fails if images are not similar
        self.assertEqual(images_are_similar, True)

if __name__ == '__main__':
    unittest.main()
