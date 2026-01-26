# to run a single test
#
#  pytest -vs test_radar_tools.py::test_read_odim_vol

import pytest

@pytest.mark.rpnpy
def test_fst_composite(setup_test_paths):
    ''' test funtion that reads a fst file composite

    '''
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    # DOCS:fst_composites_begins
    import os
    import domutils.radar_tools as radar_tools

    fst_file = os.path.join(test_data_dir, 'std_radar_mosaics' , '2019103116_30ref_4.0km.stnd')
    out_dict = radar_tools.read_fst_composite(fst_file)
    reflectivity        = out_dict['reflectivity']
    total_quality_index = out_dict['total_quality_index']
    valid_date          = out_dict['valid_date']

    assert reflectivity.shape == (1650, 1500)
    assert str(valid_date) == '2019-10-31 16:30:00+00:00'

    # DOCS:fst_composites_ends

@pytest.mark.rpnpy
def test_obs_process(setup_test_paths):
    ''' test funtion that writes a fst file from odim h5 mosaic file

    '''

    import os
    import shutil
    import numpy as np
    import datetime
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.pyplot as plt
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools
    import domcmc.fst_tools as fst_tools
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    #setting up directories
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    generated_files_dir  = os.path.join(test_results_dir, 'generated_files',   'test_radar_tools')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_radar_tools')

    py_tools.parallel_mkdir(generated_files_dir)
    py_tools.parallel_mkdir(generated_figure_dir)

    #a small class that mimics the output of argparse
    class FstArgs():
        input_data_dir = os.path.join(test_data_dir, 'odimh5_radar_composites/')
        output_dir = generated_files_dir
        input_t0 = '201910311600'
        input_tf = '201910311600'
        input_dt = 10
        processed_file_struc = '%Y%m%d%H%M_mosaic.fst'
        input_file_struc = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
        h5_latlon_file = os.path.join(test_data_dir, 'radar_continental_2.5km_2882x2032.pickle')
        output_file_format = 'fst'
        sample_pr_file = os.path.join(test_data_dir, 'hrdps_5p1_prp0.fst')
        ncores = 1
        complete_dataset = 'False'
        figure_dir = generated_figure_dir
        figure_format = 'svg'
        log_level = 'INFO'

    args = FstArgs()

    #this command writes a fst file and makes a figure from it 
    radar_tools.obs_process(args)

    #the name of a figure we just generated figure
    generated_figure = os.path.join(generated_figure_dir, 
                                    '20191031_1600.svg')

    #pre saved figure for what the results should be
    reference_figure = os.path.join(test_data_dir, 'reference_figures', 'test_radar_tools',
                                    os.path.basename(generated_figure))

    #compare image with saved reference
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


@pytest.mark.rpnpy
def test_nowcast_time_interpol(setup_test_paths):
    ''' Test temporal interpolation using nowcasts

    '''

    import os
    import shutil
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
    import domutils._py_tools as py_tools

    #setting up directories
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    generated_files_dir  = os.path.join(test_results_dir, 'generated_files',   'test_radar_tools')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_radar_tools')

    py_tools.parallel_mkdir(generated_files_dir)
    py_tools.parallel_mkdir(generated_figure_dir)

    #a small class that mimics the output of argparse
    class FstArgs():
        input_data_dir = os.path.join(test_data_dir, 'odimh5_radar_composites')
        output_dir = generated_files_dir
        input_t0  = '201910311540'
        input_tf  = '201910311610'
        input_dt  = 10
        output_t0 = '201910311603'
        output_tf = '201910311603'
        t_interp_method = 'nowcast'
        processed_file_struc = '%Y%m%d%H%M_mosaic.fst'
        input_file_struc = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
        h5_latlon_file = os.path.join(test_data_dir, 'radar_continental_2.5km_2882x2032.pickle')
        output_file_format = 'fst'
        sample_pr_file = os.path.join(test_data_dir, 'hrdps_5p1_prp0.fst')
        ncores = 1
        complete_dataset = 'True'
        figure_dir = generated_figure_dir
        figure_format = 'svg'
        log_level = 'INFO'

    args = FstArgs()

    #this command writes a fst file and makes a figure from it 
    radar_tools.obs_process(args)

    #the name of a figure we just generated figure
    generated_figure = os.path.join(generated_figure_dir, '20191031_1603.svg')

    #pre saved figure for what the results should be
    reference_figure = os.path.join(test_data_dir, 'reference_figures', 'test_radar_tools',
                                    os.path.basename(generated_figure))

    #compare image with saved reference
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


def test_read_odim_vol(setup_test_paths):
    """ test funtion that reads volume scans in ODIM H5 format
    """
    import os
    import numpy as np
    import domutils
    import domutils.radar_tools as radar_tools
    import datetime

    #setting up directories
    test_data_dir = setup_test_paths['test_data_dir']

    sample_file = os.path.join(test_data_dir, 'odimh5_radar_volume_scans', 
                               '2019071120_24_ODIMH5_PVOL6S_VOL.qc.casbv.h5')

    res = radar_tools.read_h5_vol(odim_file=sample_file, 
                                  elevations=[0.4], 
                                  quantities=['dbzh'],
                                  include_quality=True,
                                  latlon=True)
    #check returned radar dictionary
    expected = set(['radar_height', 'radar_lat', 'radar_lon', 'date_str', '0.4'])
    assert set(res.keys()) == expected

    #check returned ppi dictionary
    ppi_keys = set(res['0.4'].keys())
    expected = set(['dbzh', 'quality_beamblockage', 'quality_att',
                    'quality_broad', 'quality_qi_total', 'nominal_elevation',
                    'azimuths', 'elevations', 'ranges', 'latitudes', 'longitudes', 'm43_heights'])
    assert ppi_keys == expected

    #check returned values
    dbz = res['0.4']['dbzh'][700,300:310]
    expected = np.array([43.,  41.,  42.,  41.5, 41.5, 42.5, 44.5, 42.,  43.,  40.5])
    assert np.allclose(dbz, expected)

    #check returned latitudes
    lats = res['0.4']['latitudes'][700,300:310]
    expected = np.array( [47.03682545, 47.04124917, 47.04567286, 
                           47.05009653, 47.05452016, 47.05894377, 
                           47.06336734, 47.06779089, 47.07221441, 47.07663789])

    assert np.allclose(lats, expected)



def test_read_stageiv(setup_test_paths):
    """ test funtion that reads a stageIV

    Created on Mon Sep 14 20:35:03 2020

    @author: dkh018 Thanks!
    """

    import os
    import numpy as np
    import domutils
    import domutils.radar_tools as radar_tools
    import datetime

    #setting up directories
    test_data_dir = setup_test_paths['test_data_dir']
    stage4_data_dir = os.path.join(test_data_dir, 'stage4_composites')

    #example 1
    # get a 6-h accumulation from a 6-hour accumulation file 
    # stage IV 6h accumulation length;    01, 06 or 24 are possible
    data_recipe      = 'ST4.%Y%m%d%H.06h'

    out_dict_acc_ex1 = radar_tools.get_accumulation(end_date=datetime.datetime(2019,10,31,18),
                                                    duration=360.,  #6h in minutes
                                                    data_path=stage4_data_dir,
                                                    data_recipe=data_recipe,
                                                    desired_quantity="accumulation",
                                                    latlon=True)
    #the accumulation we just read
    accumulation = out_dict_acc_ex1['accumulation']

    #test that sum of precip is the same as expected
    sum_precip = accumulation[np.nonzero(accumulation > 0.)].sum()
    assert np.isclose(sum_precip, 858057.64)
    


    #example 2
    # get a 3-h accumulatation from three 1-hour accumulation files
    # stage IV 1h accumulation length;    01, 06 or 24 are possible
    data_recipe      = 'ST4.%Y%m%d%H.01h'

    out_dict_acc_ex2 = radar_tools.get_accumulation(end_date=datetime.datetime(2019,10,31,23),
                                                    duration=180.,    #3h in minutes
                                                    data_path=stage4_data_dir,
                                                    data_recipe=data_recipe,
                                                    desired_quantity="accumulation",
                                                    latlon=True)
    #the accumulation we just read
    accumulation = out_dict_acc_ex2['accumulation']

    #test that sum of precip is the same as expected
    sum_precip = accumulation[np.nonzero(accumulation > 0.)].sum()
    assert np.isclose(sum_precip, 346221.57)


def test_read_mrms(setup_test_paths):
    """ test funtion that reads mrms data

    """

    import os
    import numpy as np
    import domutils
    import domutils.radar_tools as radar_tools
    import datetime

    #setting up directories
    test_data_dir = setup_test_paths['test_data_dir']
    mrms_data_dir = os.path.join(test_data_dir, 'mrms_grib2')

    #
    #
    #example 1
    # get precipitation rates from mrms file
    data_recipe      = 'PrecipRate_00.00_%Y%m%d-%H%M%S.grib2'

    out_dict_pr = radar_tools.get_instantaneous(valid_date=datetime.datetime(2019,10,31,16,30,0),
                                                data_path=mrms_data_dir,
                                                data_recipe=data_recipe,
                                                desired_quantity="precip_rate",
                                                latlon=True)
    #the accumulation we just read
    precip_rate = out_dict_pr['precip_rate']

    #test that sum of precip is the same as expected
    sum_precip = precip_rate[np.nonzero(precip_rate > 0.)].sum()
    assert np.isclose(sum_precip, 2328047.4)
    
    


    #example 2
    # get a 30 minutes accumulatation from MRMS precip rate file available every two minutes
    data_recipe      = 'PrecipRate_00.00_%Y%m%d-%H%M%S.grib2'

    out_dict_acc_ex2 = radar_tools.get_accumulation(end_date=datetime.datetime(2019,10,31,16,30,0),
                                                    duration=30.,    #minutes
                                                    data_path=mrms_data_dir,
                                                    data_recipe=data_recipe,
                                                    desired_quantity="accumulation",
                                                    latlon=True)
    #the accumulation we just read
    accumulation = out_dict_acc_ex2['accumulation']

    #test that sum of precip is the same as expected
    sum_precip = accumulation[np.nonzero(accumulation > 0.)].sum()
    assert np.isclose(sum_precip, 1186789.0932664848)


def test_coeff_ab(setup_test_paths):
    """ test that coef_a and coefb have an impact when use by get_accumulations

    """

    import os
    import numpy as np
    import domutils
    import domutils.radar_tools as radar_tools
    import datetime

    #setting up directories
    test_data_dir = setup_test_paths['test_data_dir']
    odim_composite_dir = os.path.join(test_data_dir, 'odimh5_radar_composites')

    duration = 60.  #duration of accumulation in minutes
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    dat_dict = radar_tools.get_accumulation(end_date=datetime.datetime(2019, 10, 31, 16, 30, 0),
                                            duration=duration,
                                            data_path=odim_composite_dir,
                                            data_recipe=data_recipe)

    #the accumulation we just read
    accumulation_300_1p4 = dat_dict['accumulation']

    dat_dict = radar_tools.get_accumulation(end_date=datetime.datetime(2019, 10, 31, 16, 30, 0),
                                            duration=duration,
                                            data_path=odim_composite_dir,
                                            data_recipe=data_recipe, 
                                            coef_a=200, coef_b=1.6)

    #the accumulation we just read
    accumulation_200_1p6 = dat_dict['accumulation']

    #test that sum of precip is the same as expected
    sum_precip = np.sum(accumulation_200_1p6 - accumulation_300_1p4)
    assert np.isclose(sum_precip, 35628.67517835721)
    
    
def test_read_sqlite_vol(setup_test_paths):
    """ test funtion that reads volume scans in sqlite format
    """
    import os
    import numpy as np
    import domutils
    import domutils.radar_tools as radar_tools
    import datetime

    #setting up directories
    test_data_dir = setup_test_paths['test_data_dir']
    
    sample_file = os.path.join(test_data_dir, 'sqlite_radar_volume_scans', '2019070206_ra')

    #get everything in file
    this_date = datetime.datetime(2019,7,2,3,6,0)
    res = radar_tools.read_sqlite_vol(sqlite_file=sample_file, 
                                      radars = ['casbv'],
                                      vol_scans = [this_date],
                                      quantities = ['OBSVALUE'],
                                      elevations = [0.4], 
                                      latlon=True)
    #radars in file
    expected = set(['casbv'])
    assert  set(res.keys()) == expected

    #check returned radar dictionary
    keys = set(res['casbv'].keys())
    expected = set(['radar_lat', 'radar_lon', 'radar_height', datetime.datetime(2019, 7, 2, 3, 6)])
    assert keys == expected

    #check returned elevation dictionary
    elev_keys=set(res['casbv'][this_date].keys())
    expected=set(['0.4'])
    assert elev_keys == expected

    #check returned quantities
    qty_keys = set(res['casbv'][this_date]['0.4'].keys())
    expected = set(['azimuths', 'elevations', 'ranges', 'obsvalue', 'id_obs',
                    'range', 'half_delta_range', 'half_delta_azimuth', 'latitudes', 'longitudes', 'm43_heights'])
    assert qty_keys == expected

    #check some returned values for Doppler velocities
    dvel = res['casbv'][this_date]['0.4']['obsvalue'][0,150:160]
    expected = np.array([-9.99900000e+03, -3.01732165e+00, -3.01732165e+00, -9.99900000e+03,
                          -3.39448702e+00, -3.39448702e+00, -3.39448702e+00, -3.39448702e+00,
                          -9.99900000e+03, -3.01732165e+00,])
    assert np.allclose(dvel, expected)

    #check returned latitudes
    lats = res['casbv'][this_date]['0.4']['latitudes'][0,150:160]
    expected = np.array( [46.38282768, 46.38732164, 46.39181559, 46.39630952, 46.40080344, 46.40529735,
                           46.40979124, 46.41428512, 46.41877898, 46.42327284,])

    assert np.allclose(lats,expected)
    
if __name__ == '__main__':


    #test_obs_process()
    test_nowcast_time_interpol()
    
