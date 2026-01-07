import pytest
import os
import numpy as np

# -----------------------------------------------------------------------------
# Tutorial setup
# -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def plot_img():
    # DOCS:plot_img_begins
    def _plot_img(fig_name, title, units, data, latitudes, longitudes,
                  colormap, equal_legs=False ):
    
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import domutils.geo_tools as geo_tools
    
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
    
        #save output
        plt.savefig(fig_name,dpi=400)
        plt.close(fig)
    
       # DOCS:plot_img_ends

    return _plot_img

@pytest.fixture(scope="module")
def setup_values_and_palettes():

    # DOCS:values_and_palette_begins
    import domutils.legs as legs
    
    #flags
    undetect = -3333.
    missing  = -9999.
    
    #Color mapping object for reflectivity
    ref_color_map = legs.PalObj(range_arr=[0.,60.],
                                n_col=6,
                                over_high='extend', under_low='white',
                                excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    
    #Color mapping object for quality index
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[255,227,215],[205,144, 73]],  #pale/dark brown
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    #precip Rate
    ranges = [.1,1.,2.,4.,8.,16.,32.]
    pr_color_map = legs.PalObj(range_arr=ranges,
                               n_col=6,
                               over_high='extend', under_low='white',
                               excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    #accumulations
    ranges = [1.,2.,5.,10., 20., 50., 100.]
    acc_color_map = legs.PalObj(range_arr=ranges,
                                n_col=6,
                                over_high='extend', under_low='white',
                                excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])

    # DOCS:values_and_palette_ends

    return undetect, missing, ref_color_map, pr_color_map, acc_color_map

# -----------------------------------------------------------------------------
# Baltrad ODIM H5
# -----------------------------------------------------------------------------

def test_baltrad_odim_h5(setup_values_and_palettes, plot_img):
    undetect, missing, ref_color_map, pr_color_map, acc_color_map = setup_values_and_palettes

    # DOCS:baltrad_odim_h5_begins
    import os
    import datetime
    import domutils
    import domutils.radar_tools as radar_tools
    import domutils._py_tools as py_tools
    
    # when we want data
    this_date = datetime.datetime(2019, 10, 31, 16, 30, 0, tzinfo=datetime.timezone.utc)
    
    # where is the data
    domutils_dir = os.path.dirname(domutils.__file__)
    package_dir  = os.path.dirname(domutils_dir)
    data_path = os.path.join(package_dir, 'test_data/odimh5_radar_composites/')
    
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
    fig_name = os.path.join(package_dir, 'test_results/radar_tutorial/original_reflectivity.svg')
    py_tools.parallel_mkdir(os.path.dirname(fig_name))
    title = 'Odim H5 reflectivity on original grid'
    units = '[dBZ]'
    data       = dat_dict['reflectivity']
    latitudes  = dat_dict['latitudes']
    longitudes = dat_dict['longitudes']
    
    plot_img(fig_name, title, units, data, latitudes, longitudes,
             ref_color_map)

    #compare image with saved reference
    #copy reference image to testdir
    reference_image = package_dir+'/test_data/_static/'+os.path.basename(fig_name)
    images_are_similar = py_tools.render_similarly(fig_name, reference_image)

    if images_are_similar:
        log_dir = './logs'
        shutil.rmtree(log_dir)

    #test fails if images are not similar
    assert images_are_similar

    if os.environ.get("UPDATE_DOC_ARTIFACTS") == "1":
        copy_to_static(fig_name)


    # DOCS:baltrad_odim_h5_ends


## -----------------------------------------------------------------------------
## MRMS precipitation rates in grib2 format
## -----------------------------------------------------------------------------
#
#def test_mrms_grib2():
#    # DOCS:mrms_grib2_begins
#
#    from domutils.geo_tools import radar_tools
#
#    parentdir = os.path.dirname(__file__)
#    grib_file = os.path.join(parentdir, "test_data/mrms/mrms_rate.grib2")
#
#    mrms = radar_tools.read_mrms_grib2(grib_file)
#
#    # DOCS:mrms_grib2_ends
#
#
## -----------------------------------------------------------------------------
## 4-km mosaics from URP
## -----------------------------------------------------------------------------
#
#def test_urp_4km():
#    # DOCS:urp_4km_begins
#
#    from domutils.geo_tools import radar_tools
#
#    parentdir = os.path.dirname(__file__)
#    urp_file = os.path.join(parentdir, "test_data/urp/urp_4km.nc")
#
#    urp = radar_tools.read_urp_mosaic(urp_file)
#
#    # DOCS:urp_4km_ends
#
#
## -----------------------------------------------------------------------------
## dBZ → precipitation rate
## -----------------------------------------------------------------------------
#
#def test_dbz_to_rr():
#    # DOCS:dbz_to_rr_begins
#
#    from domutils.geo_tools import radar_tools
#    import numpy as np
#
#    dbz = np.array([10., 20., 30.])
#    rr = radar_tools.dbz_to_rr(dbz)
#
#    # DOCS:dbz_to_rr_ends
#
#
## -----------------------------------------------------------------------------
## Median filter
## -----------------------------------------------------------------------------
#
#def test_median_filter():
#    # DOCS:median_filter_begins
#
#    from scipy.ndimage import median_filter
#    import numpy as np
#
#    data = np.random.rand(100, 100)
#    filtered = median_filter(data, size=3)
#
#    # DOCS:median_filter_ends
#
#
## -----------------------------------------------------------------------------
## Interpolation
## -----------------------------------------------------------------------------
#
#def test_interpolation():
#    # DOCS:interpolation_begins
#
#    from domutils.geo_tools import geo_tools
#    import numpy as np
#
#    src = np.random.rand(50, 50)
#    interp = geo_tools.interpolate_to_grid(src)
#
#    # DOCS:interpolation_ends
#
#
## -----------------------------------------------------------------------------
## On-the-fly accumulation
## -----------------------------------------------------------------------------
#
#def test_accumulation_otf():
#    # DOCS:accumulation_otf_begins
#
#    from domutils.geo_tools import radar_tools
#    import numpy as np
#
#    rates = np.random.rand(10, 100, 100)
#    accum = radar_tools.accumulate_rates(rates, dt_minutes=5)
#
#    # DOCS:accumulation_otf_ends
#
#
## -----------------------------------------------------------------------------
## Stage IV accumulations
## -----------------------------------------------------------------------------
#
#def test_stage4():
#    # DOCS:stage4_begins
#
#    from domutils.geo_tools import radar_tools
#
#    parentdir = os.path.dirname(__file__)
#    stage4_file = os.path.join(parentdir, "test_data/stage4/stage4.nc")
#
#    stage4 = radar_tools.read_stage4(stage4_file)
#
#    # DOCS:stage4_ends
#

if __name__ == '__main__':
    test_baltrad_odim_h5(setup_values_and_palettes, plot_img)
