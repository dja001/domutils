
import pytest
import os
import numpy as np

# -----------------------------------------------------------------------------
# Tutorial setup
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def plot_img():
    # DOCS:plot_img_begins
    def _plot_img(generated_figure, title, units, data, latitudes, longitudes,
                  colormap, equal_legs=False ):
    
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import domutils.geo_tools as geo_tools
        import domutils._py_tools as py_tools

        # matplotlib global settings
        dpi = 400             # density of pixel for figure
        mpl.rcParams.update({
            'font.family': 'Latin Modern Roman',
            'font.size': 24,
            'axes.titlesize': 24,
            'axes.labelsize': 24,
            'xtick.labelsize': 20,
            'ytick.labelsize': 20,
            'legend.fontsize': 20,
            'figure.dpi': dpi,
            'savefig.dpi': dpi,
            })

        #pixel density of image to plot
        ratio = .8
        hpix = 600.       #number of horizontal pixels
        vpix = ratio*hpix #number of vertical pixels
        img_res = (int(hpix),int(vpix))
    
        #size of image to plot
        fig_w = 7.                     #size of figure
        fig_h = 5.5                     #size of figure
        rec_w = 5.8/fig_w               #size of axes
        rec_h = ratio*(rec_w*fig_w)/fig_h #size of axes
    
        #setup cartopy projection
        central_longitude=-94.
        central_latitude=35.
        standard_parallels=(30.,40.)
        proj_aea = ccrs.AlbersEqualArea(central_longitude=central_longitude,
                                        central_latitude=central_latitude,
                                        standard_parallels=standard_parallels)
        map_extent=[-104.8,-75.2,27.8,48.5]
    
        #instantiate projection object 
        proj_inds = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
                                       extent=map_extent, dest_crs=proj_aea, image_res=img_res)
        #use it to project data to image space
        projected_data = proj_inds.project_data(data)
    
        #instantiate figure
        fig = plt.figure(figsize=(fig_w,fig_h))
    
        #axes for data
        x0 = 0.01
        y0 = .1
        ax1 = fig.add_axes([x0,y0,rec_w,rec_h], projection=proj_aea)
        ax1.set_extent(proj_inds.rotated_extent, crs=proj_aea)
    
        #add title 
        dum = ax1.annotate(title, size=20,
                           xy=(.02, .9), xycoords='axes fraction',
                           bbox=dict(boxstyle="round", fc='white', ec='white'))
    
        #plot data & palette
        colormap.plot_data(ax=ax1,data=projected_data,
                           palette='right', pal_units=units, pal_format='{:2.0f}', 
                           equal_legs=equal_legs)   
    
        #add political boundaries
        ax1.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, edgecolor='0.2')
    
        #plot border 
        #proj_inds.plot_border(ax1, linewidth=.5)
    
        # make sure output directory exists
        py_tools.parallel_mkdir(os.path.dirname(generated_figure))

        #save output
        plt.savefig(generated_figure)
        plt.close(fig)
    
       # DOCS:plot_img_ends

    return _plot_img

@pytest.fixture(scope="module")
def setup_values_and_palettes(setup_test_paths):

    # DOCS:values_and_palette_begins
    import os 
    import domutils
    import domutils.legs as legs
    import domutils._py_tools as py_tools

    # where is the data
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    reference_figure_dir = os.path.join(test_data_dir,    'reference_figures', 'test_radar_tutorial')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_radar_tutorial')

    py_tools.parallel_mkdir(generated_figure_dir)
    
    # flags
    undetect = -3333.
    missing  = -9999.
    
    # Color mapping object for reflectivity
    ref_color_map = legs.PalObj(range_arr=[0.,60.],
                                n_col=6,
                                over_high='extend', under_low='white',
                                excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    
    # Color mapping object for quality index
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[255,227,215],[205,144, 73]],  #pale/dark brown
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    # precip Rate
    ranges = [.1,1.,2.,4.,8.,16.,32.]
    pr_color_map = legs.PalObj(range_arr=ranges,
                               n_col=6,
                               over_high='extend', under_low='white',
                               excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    # accumulations
    ranges = [1.,2.,5.,10., 20., 50., 100.]
    acc_color_map = legs.PalObj(range_arr=ranges,
                                n_col=6,
                                over_high='extend', under_low='white',
                                excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])

    # DOCS:values_and_palette_ends

    return (undetect, missing, 
            ref_color_map, pr_color_map, acc_color_map, 
            test_data_dir, test_results_dir, 
            generated_figure_dir, reference_figure_dir)

# -----------------------------------------------------------------------------
# Baltrad ODIM H5
# -----------------------------------------------------------------------------
def test_baltrad_odim_h5(setup_values_and_palettes, plot_img):

    # comon test data
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:baltrad_odim_h5_begins
    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools
    
    # when we want data
    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    
    # where is the data
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    
    # how to construct filename. 
    #   See documentation for the *strftime* method in the datetime module
    #   Note the *.h5* extention, this is where we specify that we want ODIM H5 data
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
     
    # get reflectivity on native grid
    # with latlon=True, we will also get the data coordinates
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True)
    # test what we just got
    assert dat_dict['valid_date'] == this_date
    assert dat_dict['reflectivity'].shape == (2882, 2032)
    assert dat_dict['total_quality_index'].shape == (2882, 2032)
    assert dat_dict['latitudes'].shape == (2882, 2032)
    assert dat_dict['longitudes'].shape == (2882, 2032)

    #show data
    generated_figure = os.path.join(generated_figure_dir, 'original_reflectivity.svg')
    title = 'Odim H5 reflectivity on original grid'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:baltrad_odim_h5_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


# -----------------------------------------------------------------------------
# MRMS precipitation rates in grib2 format
# -----------------------------------------------------------------------------
def test_mrms_grib2(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:mrms_grib2_begins

    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools
    
    # when we want data
    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    
    # where is the data
    data_path = os.path.join(test_data_dir, 'mrms_grib2/')
    
    #how to construct filename. 
    #   See documentation for the *strftime* method in the datetime module
    #   Note the *.grib2* extention, this is where we specify that we wants mrms data
    data_recipe = 'PrecipRate_00.00_%Y%m%d-%H%M%S.grib2'
    
    #Note that the file RadarQualityIndex_00.00_20191031-163000.grib2.gz must be present in the 
    #same directory for the quality index to be defined.
     
    #get precipitation on native grid
    #with latlon=True, we will also get the data coordinates
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             desired_quantity='precip_rate',
                                             latlon=True)
    #show what we just got
    # test what we just got
    assert dat_dict['valid_date'] == this_date
    assert dat_dict['precip_rate'].shape == (3500, 7000)
    assert dat_dict['total_quality_index'].shape == (3500, 7000)
    assert dat_dict['latitudes'].shape == (3500, 7000)
    assert dat_dict['longitudes'].shape == (3500, 7000)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'mrms_precip_rate.svg')
    title = 'MRMS precip rates on original grid'
    units = '[mm/h]'
    data       = dat_dict['precip_rate']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:mrms_grib2_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


# -----------------------------------------------------------------------------
# 4-km mosaics from URP
# -----------------------------------------------------------------------------

@pytest.mark.rpnpy
def test_urp_4km(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:urp_4km_begins

    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    # when we want data
    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)

    #URP 4km reflectivity mosaics
    data_path = os.path.join(test_data_dir, 'std_radar_mosaics/')
    #note the *.stnd* extension specifying that a standard file will be read
    data_recipe = '%Y%m%d%H_%Mref_4.0km.stnd'
    
    #exactly the same command as before
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True)
    assert dat_dict['valid_date'] == this_date
    assert dat_dict['reflectivity'].shape == (1650, 1500)
    assert dat_dict['total_quality_index'].shape == (1650, 1500)
    assert dat_dict['latitudes'].shape == (1650, 1500)
    assert dat_dict['longitudes'].shape == (1650, 1500)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'URP4km_reflectivity.svg')
    title = 'URP 4km reflectivity on original grid'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:urp_4km_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


# -----------------------------------------------------------------------------
# None and nearest
# -----------------------------------------------------------------------------
def test_none_and_nearest(setup_values_and_palettes):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:return_none_begins
    import os
    import datetime
    import domutils.radar_tools as radar_tools

    #set time at 16h35 where no mosaic file exists
    this_date = datetime.datetime(2019, 10, 31, 16, 35, 0, tzinfo=datetime.timezone.utc)
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe)
    assert dat_dict is None
    # DOCS:return_none_ends

    # DOCS:nearest_time_begins
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             nearest_time=10)

    # note valid date 16h30 instead of 16h35 in the function call
    assert dat_dict['valid_date'] == datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    # DOCS:nearest_time_ends



# -----------------------------------------------------------------------------
# precip rate from dbz
# -----------------------------------------------------------------------------
def test_precip_rate(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:wdssr_zr_begins
    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
     
    #require precipitation rate in the output
    dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
                                             valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True)
    
    #show data  
    generated_figure = os.path.join(generated_figure_dir, 'odimh5_reflectivity_300_1p4.svg')
    title = 'precip rate with a=300, b=1.4 '
    units = '[mm/h]'
    data       = dat_dict['precip_rate']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:wdssr_zr_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar



# -----------------------------------------------------------------------------
# precip rate from dbz
# -----------------------------------------------------------------------------
def test_zr(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:wdssr_zr_begins
    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
     
    #require precipitation rate in the output
    dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
                                             valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True)
    
    #show data  
    generated_figure = os.path.join(generated_figure_dir, 'odimh5_reflectivity_300_1p4.svg')
    title = 'precip rate with a=300, b=1.4 '
    units = '[mm/h]'
    data       = dat_dict['precip_rate']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:wdssr_zr_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

    # DOCS:200_1.6_begins

    # custom coefficients a and b
    dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
                                             coef_a=200, coef_b=1.6,
                                             valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True)
    
    #show data  
    generated_figure = os.path.join(generated_figure_dir, 'odimh5_reflectivity_200_1p6.svg')
    title = 'precip rate with a=200, b=1.6 '
    units = '[mm/h]'
    data       = dat_dict['precip_rate']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:200_1.6_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

# -----------------------------------------------------------------------------
# Median filter
# -----------------------------------------------------------------------------
def test_median_filter(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:median_filter_begins
    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
     
    #Apply median filter by setting *median_filt=3* meaning that a 3x3 boxcar
    #will be used for the filtering
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True,
                                             median_filt=3)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'speckle_filtered_reflectivity.svg')
    title = 'Speckle filtered Odim H5 reflectivity'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:median_filter_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

# -----------------------------------------------------------------------------
# Interpolation
# -----------------------------------------------------------------------------
def test_interpolation(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:interpolation_setup_begins

    import os
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools
    import pickle

    #let our destination grid be at 10 km resolution in the middle of the US
    #this is a grid where I often perform integration with the GEM atmospheric model
    #recover previously prepared data
    pickle_file = os.path.join(test_data_dir, 'pal_demo_data.pickle')
    with open(pickle_file, 'rb') as f:
        data_dict = pickle.load(f)
    gem_lon = data_dict['longitudes']    #2D longitudes [deg]
    gem_lat = data_dict['latitudes']     #2D latitudes  [deg]

    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    # DOCS:interpolation_setup_ends


    # DOCS:nearest_neighbor_begins
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True,
                                             dest_lon=gem_lon,
                                             dest_lat=gem_lat)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'nearest_interpolation_reflectivity.svg')
    title = 'Nearest Neighbor to 10 km grid'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:nearest_neighbor_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


    # DOCS:average_in_tile_begins

    # get data on destination grid using averaging
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True,
                                             dest_lon=gem_lon,
                                             dest_lat=gem_lat,
                                             average=True)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'average_interpolation_reflectivity.svg')
    title = 'Average to 10 km grid'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:average_in_tile_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar


    # DOCS:average_in_radius_begins

    #get data on destination grid averaging all points
    #within a circle of a given radius
    #also apply the median filter on input data
    dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
                                             data_path=data_path,
                                             data_recipe=data_recipe,
                                             latlon=True,
                                             dest_lon=gem_lon,
                                             dest_lat=gem_lat,
                                             median_filt=3,
                                             smooth_radius=12.)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'smooth_radius_interpolation_reflectivity.svg')
    title = 'Average input within a radius of 12 km'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             ref_color_map)

    # DOCS:average_in_radius_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar



# -----------------------------------------------------------------------------
# On-the-fly accumulation
# -----------------------------------------------------------------------------
def test_accumulation(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes

    # DOCS:compute_accumulation_begins

    import os
    import pickle
    import datetime
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    #1h accumulations of precipitation
    end_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    duration = 60.  #duration of accumulation in minutes

    data_path = os.path.join(test_data_dir, 'odimh5_radar_composites')
    data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            latlon=True)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'one_hour_accum_orig_grid.svg')
    title = '1h accumulation original grid'
    units = '[mm]'
    data       = dat_dict['accumulation']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:compute_accumulation_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

    # DOCS:combine_options_begins

    # destination grid
    pickle_file = os.path.join(test_data_dir, 'pal_demo_data.pickle')
    with open(pickle_file, 'rb') as f:
        data_dict = pickle.load(f)
    gem_lon = data_dict['longitudes']    #2D longitudes [deg]
    gem_lat = data_dict['latitudes']     #2D latitudes  [deg]

    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            dest_lon=gem_lon,
                                            dest_lat=gem_lat,
                                            median_filt=3,
                                            smooth_radius=12.,
                                            latlon=True)
    
    #if you were to look a "INFO" level logs, you would see what is going on under the hood:
    #
    # get_accumulation starting
    # get_instantaneous, getting data for:  2019-10-31 16:30:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311630.h5
    # get_instantaneous, applying median filter
    # get_instantaneous, getting data for:  2019-10-31 16:20:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311620.h5
    # get_instantaneous, applying median filter
    # get_instantaneous, getting data for:  2019-10-31 16:10:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311610.h5
    # get_instantaneous, applying median filter
    # get_instantaneous, getting data for:  2019-10-31 16:00:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311600.h5
    # get_instantaneous, applying median filter
    # get_instantaneous, getting data for:  2019-10-31 15:50:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311550.h5
    # get_instantaneous, applying median filter
    # get_instantaneous, getting data for:  2019-10-31 15:40:00
    # read_h5_composite: reading: b'DBZH' from: .../odimh5_radar_composites/2019/10/31/qcomp_201910311540.h5
    # get_instantaneous, applying median filter
    # get_accumulation, computing average precip rate in accumulation period
    # get_accumulation, interpolating to destination grid
    # get_accumulation computing accumulation from avg precip rate
    # get_accumulation done
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'one_hour_accum_interpolated.svg')
    title = '1h accum, filtered and interpolated'
    units = '[mm]'
    data       = dat_dict['accumulation']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:combine_options_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar



# -----------------------------------------------------------------------------
# Stage IV accumulations
# -----------------------------------------------------------------------------
def test_stage_4(setup_values_and_palettes, plot_img):
    (undetect, missing, 
     ref_color_map, pr_color_map, acc_color_map, 
     test_data_dir, test_results_dir, 
     generated_figure_dir, reference_figure_dir) = setup_values_and_palettes
    # DOCS:stage_4_basic_begins

    import os
    import datetime
    import pickle
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools

    #6h accumulations of precipitation
    end_date = datetime.datetime(2019, 10, 31, 18, 0, tzinfo=datetime.timezone.utc)
    duration = 360.  #duration of accumulation in minutes here 6h

    data_path = os.path.join(test_data_dir, 'stage4_composites')
    data_recipe = 'ST4.%Y%m%d%H.06h' #note the '06h' for a 6h accumulation file
    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            latlon=True)
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'stageIV_six_hour_accum_orig_grid.svg')
    title = '6h accumulation original grid'
    units = '[mm]'
    data       = dat_dict['accumulation']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             acc_color_map, equal_legs=True)

    # DOCS:stage_4_basic_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

    # DOCS:stage_4_manipulate_begins

    #6h average precipitation rate on 10km grid
    # destination grid
    pickle_file = os.path.join(test_data_dir, 'pal_demo_data.pickle')
    with open(pickle_file, 'rb') as f:
        data_dict = pickle.load(f)
    gem_lon = data_dict['longitudes']    #2D longitudes [deg]
    gem_lat = data_dict['latitudes']     #2D latitudes  [deg]

    dat_dict = radar_tools.get_accumulation(desired_quantity='avg_precip_rate', #what quantity want
                                            end_date=end_date,
                                            duration=duration,
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            dest_lon=gem_lon,       #lat/lon of 10km grid
                                            dest_lat=gem_lat,
                                            smooth_radius=12.)  #use smoothing radius of 12km for the interpolation
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'stageIV_six_hour_pr_10km_grid.svg')
    title = '6h average precip rate on 10km grid'
    units = '[mm/h]'
    data       = dat_dict['avg_precip_rate']
    latitudes  = gem_lat
    longitudes = gem_lon
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             pr_color_map, equal_legs=True)

    # DOCS:stage_4_manipulate_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar

    # DOCS:stage_4_build_accum_begins

    #3h accumulation from three 1h accumulations file
    end_date = datetime.datetime(2019, 10, 31, 23, 0)
    duration = 180.  #duration of accumulation in minutes here 3h
    data_recipe = 'ST4.%Y%m%d%H.01h' #note the '01h' for a 1h accumulation file
    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            dest_lon=gem_lon,   #lat/lon of 10km grid
                                            dest_lat=gem_lat,
                                            smooth_radius=5.)  #use smoothing radius of 5km for the interpolation
    
    #show data
    generated_figure = os.path.join(generated_figure_dir, 'stageIV_3h_accum_10km_grid.svg')
    title = '3h accumulation on 10km grid'
    units = '[mm]'
    data       = dat_dict['accumulation']
    latitudes  = gem_lat
    longitudes = gem_lon
    plot_img(generated_figure, title, units, data, latitudes, longitudes,
             acc_color_map, equal_legs=True)

    # DOCS:stage_4_build_accum_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(generated_figure))
    images_are_similar = py_tools.render_similarly(generated_figure, reference_figure,
                                                   output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    assert images_are_similar



if __name__ == '__main__':
    test_baltrad_odim_h5(setup_values_and_palettes, plot_img)
