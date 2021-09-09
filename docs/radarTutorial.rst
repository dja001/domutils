
Tutorial setup 
----------------------------------------------

This section defines plotting functions and objects that will be used throughout this 
tutorial. 
You can skip to the next section for the radar related stuff. 

Here we setup a function to display images from the 
data that we will be reading:

    >>> def plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...              colormap, equal_legs=False ):
    ...
    ...     import matplotlib.pyplot as plt
    ...     import cartopy.crs as ccrs
    ...     import cartopy.feature as cfeature
    ...     import domutils.geo_tools as geo_tools
    ... 
    ...     #pixel density of image to plot
    ...     ratio = .8
    ...     hpix = 600.       #number of horizontal pixels
    ...     vpix = ratio*hpix #number of vertical pixels
    ...     img_res = (int(hpix),int(vpix))
    ... 
    ...     #size of image to plot
    ...     fig_w = 7.                     #size of figure
    ...     fig_h = 5.5                     #size of figure
    ...     rec_w = 5.8/fig_w               #size of axes
    ...     rec_h = ratio*(rec_w*fig_w)/fig_h #size of axes
    ...
    ...     #setup cartopy projection
    ...     central_longitude=-94.
    ...     central_latitude=35.
    ...     standard_parallels=(30.,40.)
    ...     proj_aea = ccrs.AlbersEqualArea(central_longitude=central_longitude,
    ...                                     central_latitude=central_latitude,
    ...                                     standard_parallels=standard_parallels)
    ...     map_extent=[-104.8,-75.2,27.8,48.5]
    ...
    ...     #instantiate projection object 
    ...     proj_inds = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
    ...                                    extent=map_extent, dest_crs=proj_aea, image_res=img_res)
    ...     #use it to project data to image space
    ...     projected_data = proj_inds.project_data(data)
    ... 
    ...     #instantiate figure
    ...     fig = plt.figure(figsize=(fig_w,fig_h))
    ... 
    ...     #axes for data
    ...     x0 = 0.01
    ...     y0 = .1
    ...     ax1 = fig.add_axes([x0,y0,rec_w,rec_h], projection=proj_aea)
    ...     ax1.set_extent(map_extent)
    ... 
    ...     #add title 
    ...     dum = ax1.annotate(title, size=20,
    ...                        xy=(.02, .9), xycoords='axes fraction',
    ...                        bbox=dict(boxstyle="round", fc='white', ec='white'))
    ... 
    ...     #plot data & palette
    ...     colormap.plot_data(ax=ax1,data=projected_data,
    ...                        palette='right', pal_units=units, pal_format='{:2.0f}', 
    ...                        equal_legs=equal_legs)   
    ... 
    ...     #add political boundaries
    ...     ax1.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, edgecolor='0.2')
    ... 
    ...     #plot border 
    ...     #proj_inds.plot_border(ax1, linewidth=.5)
    ... 
    ...     #save output
    ...     plt.savefig(fig_name,dpi=400)
    ...     plt.close(fig)

Let's also initialize some color mapping objects for the different 
quantities that will be displayed.
See :ref:`legsTutorial` for details.

    >>> import domutils.legs as legs
    >>>
    >>> #flags
    >>> undetect = -3333.
    >>> missing  = -9999.
    >>>
    >>> #Color mapping object for reflectivity
    >>> ref_color_map = legs.PalObj(range_arr=[0.,60.],
    ...                             n_col=6,
    ...                             over_high='extend', under_low='white',
    ...                             excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    >>>
    >>> #Color mapping object for quality index
    >>> pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
    ...            [[255,185,255],[147, 78,172]],  #pale/dark purple
    ...            [[255,227,215],[205,144, 73]],  #pale/dark brown
    ...            [[210,235,255],[ 58,134,237]],  #pale/dark blue
    ...            [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    >>> #precip Rate
    >>> ranges = [.1,1.,2.,4.,8.,16.,32.]
    >>> pr_color_map = legs.PalObj(range_arr=ranges,
    ...                            n_col=6,
    ...                            over_high='extend', under_low='white',
    ...                            excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    >>> #accumulations
    >>> ranges = [1.,2.,5.,10., 20., 50., 100.]
    >>> acc_color_map = legs.PalObj(range_arr=ranges,
    ...                             n_col=6,
    ...                             over_high='extend', under_low='white',
    ...                             excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])



Get radar mosaics from different sources and file formats
-----------------------------------------------------------------


Baltrad ODIM H5 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Let's read reflectivity fields from an ODIM H5 composite file using the
    *get_instantaneous* method.

    >>> import os, inspect
    >>> import datetime
    >>> import domutils.radar_tools as radar_tools
    >>>
    >>> #when we want data
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>>
    >>> #where is the data
    >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    >>> parentdir  = os.path.dirname(currentdir) #directory where this package lives
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>>
    >>> #how to construct filename. 
    >>> #   See documentation for the *strftime* method in the datetime module
    >>> #   Note the *.h5* extention, this is where we specify that we want ODIM H5 data
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #get reflectivity on native grid
    >>> #with latlon=True, we will also get the data coordinates
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True)
    >>> #show what we just got
    >>> for key in dat_dict.keys():
    ...     if key == 'valid_date':
    ...         print(key,dat_dict[key])
    ...     else:
    ...         print(key,dat_dict[key].shape)
    reflectivity (2882, 2032)
    total_quality_index (2882, 2032)
    valid_date 2019-10-31 16:30:00+00:00
    latitudes (2882, 2032)
    longitudes (2882, 2032)
    >>> 
    >>> #show data
    >>> fig_name ='_static/original_reflectivity.svg'
    >>> title = 'Odim H5 reflectivity on original grid'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>>
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    Dark grey represents missing values, light grey represent the *undetect* value. 

    .. image:: _static/original_reflectivity.svg
        :align: center


MRMS precipitation rates in grib2 format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Reading precipitation rates from MRMS is done in a very similar way with the 
    *get_instantaneous* method.

    >>> import os, inspect
    >>> import datetime
    >>> import domutils.radar_tools as radar_tools
    >>>
    >>> #when we want data
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>>
    >>> #where is the data
    >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    >>> parentdir  = os.path.dirname(currentdir) #directory where this package lives
    >>> data_path = parentdir + '/test_data/mrms_grib2/'
    >>>
    >>> #how to construct filename. 
    >>> #   See documentation for the *strftime* method in the datetime module
    >>> #   Note the *.grib2* extention, this is where we specify that we wants mrms data
    >>> data_recipe = 'PrecipRate_00.00_%Y%m%d-%H%M%S.grib2'
    >>>
    >>> #Notre that the file RadarQualityIndex_00.00_20191031-163000.grib2.gz must be present in the 
    >>> #same directory for the quality index to be defined.
    >>>  
    >>> #get precipitation on native grid
    >>> #with latlon=True, we will also get the data coordinates
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          desired_quantity='precip_rate',
    ...                                          latlon=True)
    >>> #show what we just got
    >>> for key in dat_dict.keys():
    ...     if key == 'valid_date':
    ...         print(key,dat_dict[key])
    ...     else:
    ...         print(key,dat_dict[key].shape)
    precip_rate (3500, 7000)
    total_quality_index (3500, 7000)
    valid_date 2019-10-31 16:30:00
    latitudes (3500, 7000)
    longitudes (3500, 7000)
    >>> 
    >>> #show data
    >>> fig_name ='_static/mrms_precip_rate.svg'
    >>> title = 'MRMS precip rates on original grid'
    >>> units = '[mm/h]'
    >>> data       = dat_dict['precip_rate']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>>
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)

    .. image:: _static/mrms_precip_rate.svg
        :align: center


4-km mosaics from URP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Reading URP reflectivity mosaics is only a matter of 
    changing the file extension to:

        - .fst
        - .std
        - .stnd
        - or no extension at all.

    The script searches for *RDBZ* and *L1* entries in the standard file. 
    The first variable that is found is returned. 
    The quality index is set to 1 wherever the data is not flagged as missing in the standard file. 
    
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> #URP 4km reflectivity mosaics
    >>> data_path = parentdir + '/test_data/std_radar_mosaics/'
    >>> #note the *.stnd* extension specifying that a standard file will be read
    >>> data_recipe = '%Y%m%d%H_%Mref_4.0km.stnd'
    >>> 
    >>> #exactly the same command as before
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True)
    >>> for key in dat_dict.keys():
    ...     if key == 'valid_date':
    ...         print(key,dat_dict[key])
    ...     else:
    ...         print(key,dat_dict[key].shape)
    reflectivity (1650, 1500)
    total_quality_index (1650, 1500)
    valid_date 2019-10-31 16:30:00+00:00
    latitudes (1650, 1500)
    longitudes (1650, 1500)
    >>> 
    >>> #show data
    >>> fig_name ='_static/URP4km_reflectivity.svg'
    >>> title = 'URP 4km reflectivity on original grid'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> 
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    .. image:: _static/URP4km_reflectivity.svg
        :align: center


Get the nearest radar data to a given date and time
-----------------------------------------------------------------

    Getting the nearest radar data to an arbitrary validity time is convenient for comparison
    with model outputs at higher temporal resolutions. 

    By default, *get_instantaneous* returns None if the file does not exist
    at the specified time.
    
    >>> #set time at 16h35 where no mosaic file exists
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 35, 0)
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe)
    >>> print(dat_dict)
    None

    Set the *nearest_time* keyword to the temporal resolution of the data
    to rewind time to the closest available mosaic.

    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          nearest_time=10)
    >>> #note how the valid_date is different from the one that was requested
    >>> #in the function call
    >>> print(dat_dict['valid_date'])
    2019-10-31 16:30:00+00:00


Get precipitation rates (in mm/h) from reflectivity (in dBZ)
---------------------------------------------------------------------

    By default, exponential drop size distributions are assumed 
    with 

        Z = aR^b

    in linear 
    units.
    The default is to use WDSSR's relation with  a=300 and b=1.4.

    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #require precipitation rate in the output
    >>> dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
    ...                                          valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True)
    >>> 
    >>> #show data  
    >>> fig_name ='_static/odimh5_reflectivity_300_1p4.svg'
    >>> title = 'precip rate with a=300, b=1.4 '
    >>> units = '[mm/h]'
    >>> data       = dat_dict['precip_rate']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>>
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)

    .. image:: _static/odimh5_reflectivity_300_1p4.svg
        :align: center

    Different Z-R relationships can be used by specifying the a and b coefficients
    explicitly (for example, for the Marshall-Palmer DSD, a=200 and b=1.6):

    >>> #custom coefficients a and b
    >>> dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
    ...                                          coef_a=200, coef_b=1.6,
    ...                                          valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True)
    >>> 
    >>> #show data
    >>> fig_name ='_static/odimh5_reflectivity_200_1p6.svg'
    >>> title = 'precip rate with a=200, b=1.6 '
    >>> units = '[mm/h]'
    >>> data       = dat_dict['precip_rate']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> 
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)

    .. image:: _static/odimh5_reflectivity_200_1p6.svg
        :align: center


Apply  a median filter to reduce speckle (noise) 
-----------------------------------------------------------------

    Baltrad composites are quite noisy. For some applications, it may be desirable to apply 
    a median filter to reduce speckle. 
    This is done using the *median_filt* keyword.
    The filtering is applied both to the reflectivity or rain rate data and to its accompanying quality index. 

    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #Apply median filter by setting *median_filt=3* meaning that a 3x3 boxcar
    >>> #will be used for the filtering
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True,
    ...                                          median_filt=3)
    >>> 
    >>> #show data
    >>> fig_name ='_static/speckle_filtered_reflectivity.svg'
    >>> title = 'Skpeckle filtered Odim H5 reflectivity'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> 
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    .. image:: _static/speckle_filtered_reflectivity.svg
        :align: center


Interpolation to a different grid
-----------------------------------------------------------------

    Interpolation to a different output grid can be done using the *dest_lat* and
    *dest_lon* keywords.
    
    Three interpolation methods are 
    supported:

        * Nearest neighbor (default)
        * Average all input data points falling within the output grid tile.
          This option tends to be slow.
        * Average all input within a certain radius of the center of the output grid tile. 
          This allows to perform smoothing at the same time as interpolation.

    >>> import pickle
    >>> #let our destination grid be at 10 km resolution in the middle of the US
    >>> #this is a grid where I often perform integration with the GEM atmospheric model
    >>> #recover previously prepared data
    >>> with open(parentdir + '/test_data/pal_demo_data.pickle', 'rb') as f:
    ...     data_dict = pickle.load(f)
    >>> gem_lon = data_dict['longitudes']    #2D longitudes [deg]
    >>> gem_lat = data_dict['latitudes']     #2D latitudes  [deg]


Nearest neighbor 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> #get data on destination grid using nearest neighbor
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True,
    ...                                          dest_lon=gem_lon,
    ...                                          dest_lat=gem_lat)
    >>> 
    >>> #show data
    >>> fig_name ='_static/nearest_interpolation_reflectivity.svg'
    >>> title = 'Nearest Neighbor to 10 km grid'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    .. image:: _static/nearest_interpolation_reflectivity.svg
        :align: center


Average all inputs falling within a destination grid tile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    >>> #get data on destination grid using averaging
    >>> this_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=this_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True,
    ...                                          dest_lon=gem_lon,
    ...                                          dest_lat=gem_lat,
    ...                                          average=True)
    >>> 
    >>> #show data
    >>> fig_name ='_static/average_interpolation_reflectivity.svg'
    >>> title = 'Average to 10 km grid'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    .. image:: _static/average_interpolation_reflectivity.svg
        :align: center


Average all inputs within a radius
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This method allows to smooth the data at the same time
    as it is interpolated. 


    >>> #get data on destination grid averaging all points
    >>> #within a circle of a given radius
    >>> #also apply the median filter on input data
    >>> end_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> dat_dict = radar_tools.get_instantaneous(valid_date=end_date,
    ...                                          data_path=data_path,
    ...                                          data_recipe=data_recipe,
    ...                                          latlon=True,
    ...                                          dest_lon=gem_lon,
    ...                                          dest_lat=gem_lat,
    ...                                          median_filt=3,
    ...                                          smooth_radius=12.)
    >>> 
    >>> #show data
    >>> fig_name ='_static/smooth_radius_interpolation_reflectivity.svg'
    >>> title = 'Average input within a radius of 12 km'
    >>> units = '[dBZ]'
    >>> data       = dat_dict['reflectivity']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          ref_color_map)

    .. image:: _static/smooth_radius_interpolation_reflectivity.svg
        :align: center
           
    

On-the-fly computation of precipitation accumulations 
-----------------------------------------------------------------
    Use the *get_accumulation* method to get accumulations of precipitation.
    Three quantities can be outputted:

        - *accumulation*  The default option; returns the amount of water (in mm);
        - *avg_precip_rate* For average precipitation rate (in mm/h) during the accumulation period;
        - *reflectivity*  For the reflectivity (in dBZ) associated with the average precipitation rate
          during the accumulation period;

    For this example, let's get the accumulated amount of water in mm during a period of one 
    hour.


    >>> #1h accumulations of precipitation
    >>> end_date = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> duration = 60.  #duration of accumulation in minutes
    >>> data_path = parentdir + '/test_data/odimh5_radar_composites/'
    >>> data_recipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> dat_dict = radar_tools.get_accumulation(end_date=end_date,
    ...                                         duration=duration,
    ...                                         data_path=data_path,
    ...                                         data_recipe=data_recipe,
    ...                                         latlon=True)
    >>> 
    >>> #show data
    >>> fig_name ='_static/one_hour_accum_orig_grid.svg'
    >>> title = '1h accumulation original grid'
    >>> units = '[mm]'
    >>> data       = dat_dict['accumulation']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)

    .. image:: _static/one_hour_accum_orig_grid.svg
        :align: center


    The *get_accumulation* method is very similar to *get_instantaneous*.
    All the features presented above also work with this method. 

    For this last  example, we apply a median filter on the original data, we get the total amount of 
    water during a period of one hour and interpolate the result to a different grid using the 
    *smooth_radius* keyword.
    
    >>> dat_dict = radar_tools.get_accumulation(end_date=end_date,
    ...                                         duration=duration,
    ...                                         data_path=data_path,
    ...                                         data_recipe=data_recipe,
    ...                                         dest_lon=gem_lon,
    ...                                         dest_lat=gem_lat,
    ...                                         median_filt=3,
    ...                                         smooth_radius=12.,
    ...                                         latlon=True)
    >>>
    >>> #if you were to look a "INFO" level logs, you would see what is going on under the hood:
    >>>
    >>> #get_accumulation starting
    >>> #get_instantaneous, getting data for:  2019-10-31 16:30:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311630.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_instantaneous, getting data for:  2019-10-31 16:20:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311620.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_instantaneous, getting data for:  2019-10-31 16:10:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311610.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_instantaneous, getting data for:  2019-10-31 16:00:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311600.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_instantaneous, getting data for:  2019-10-31 15:50:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311550.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_instantaneous, getting data for:  2019-10-31 15:40:00
    >>> #read_h5_composite: reading: b'DBZH' from: /fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311540.h5
    >>> #get_instantaneous, applying median filter
    >>> #get_accumulation, computing average precip rate in accumulation period
    >>> #get_accumulation, interpolating to destination grid
    >>> #get_accumulation computing accumulation from avg precip rate
    >>> #get_accumulation done
    >>> 
    >>> #show data
    >>> fig_name ='_static/one_hour_accum_interpolated.svg'
    >>> title = '1h accum, filtered and interpolated'
    >>> units = '[mm]'
    >>> data       = dat_dict['accumulation']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)

    .. image:: _static/one_hour_accum_interpolated.svg
        :align: center



Reading in stage IV accumulations
-----------------------------------------------------------------
    The *get_accumulation* method can also be used to read and manipulate 
    "stage IV" Quantitative Precipitation Estimates.


    The data can be obtained from:

    https://data.eol.ucar.edu/dataset/21.093

        * Files of the form: *ST4.YYYYMMDDHH.??.h*   are for the North American domain
        * Files of the form: *st4_pr.YYYYMMDDHH.??.h* are for the Caribean domain 

Read one file and get lat/lon of the data grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    For this example, we get a 6-h accumulation of precipitation in mm from a 
    6-hour accumulation file. This is basically just reading one file.
    
    >>> #6h accumulations of precipitation
    >>> end_date = datetime.datetime(2019, 10, 31, 18, 0)
    >>> duration = 360.  #duration of accumulation in minutes here 6h
    >>> data_path = parentdir + '/test_data/stage4_composites/'
    >>> data_recipe = 'ST4.%Y%m%d%H.06h' #note the '06h' for a 6h accumulation file
    >>> dat_dict = radar_tools.get_accumulation(end_date=end_date,
    ...                                         duration=duration,
    ...                                         data_path=data_path,
    ...                                         data_recipe=data_recipe,
    ...                                         latlon=True)
    >>> 
    >>> #show data
    >>> fig_name ='_static/stageIV_six_hour_accum_orig_grid.svg'
    >>> title = '6h accumulation original grid'
    >>> units = '[mm]'
    >>> data       = dat_dict['accumulation']
    >>> latitudes  = dat_dict['latitudes']
    >>> longitudes = dat_dict['longitudes']
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          acc_color_map, equal_legs=True)


    .. image:: _static/stageIV_six_hour_accum_orig_grid.svg
        :align: center

Read one file, interpolate to a different grid, convert to average precipitation rate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    The *get_accumulation* method becomes more usefull if you want to  interpolate the data at the 
    same time that it is read and/or if you want to compute derived quantities.

    In this next example, we read the same 6h accumulation file but this time, we will
    get the average precipitation rate over the 10km grid used in the previous example. 

    >>> #6h average precipitation rate on 10km grid
    >>> end_date = datetime.datetime(2019, 10, 31, 18, 0)
    >>> duration = 360.  #duration of accumulation in minutes here 6h
    >>> data_path = parentdir + '/test_data/stage4_composites/'
    >>> data_recipe = 'ST4.%Y%m%d%H.06h' #note the '06h' for a 6h accumulation file
    >>> dat_dict = radar_tools.get_accumulation(desired_quantity='avg_precip_rate', #what quantity want
    ...                                         end_date=end_date,
    ...                                         duration=duration,
    ...                                         data_path=data_path,
    ...                                         data_recipe=data_recipe,
    ...                                         dest_lon=gem_lon,       #lat/lon of 10km grid
    ...                                         dest_lat=gem_lat,
    ...                                         smooth_radius=12.)  #use smoothing radius of 12km for the interpolation
    >>> 
    >>> #show data
    >>> fig_name ='_static/stageIV_six_hour_pr_10km_grid.svg'
    >>> title = '6h average precip rate on 10km grid'
    >>> units = '[mm/h]'
    >>> data       = dat_dict['avg_precip_rate']
    >>> latitudes  = gem_lat
    >>> longitudes = gem_lon
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          pr_color_map, equal_legs=True)


    .. image:: _static/stageIV_six_hour_pr_10km_grid.svg
        :align: center

Construct accumulation from several files 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


    Finally, use the *get_accumulation* method to construct accumulations of arbitrary length
    from stage IV accumulations. 

    Here, we construct a 3h accumulation from three consecutive 1h accumulations. 
    As before, the data is interpolated to a 10 km grid. 

    >>> #3h accumulation from three 1h accumulations file
    >>> end_date = datetime.datetime(2019, 10, 31, 23, 0)
    >>> duration = 180.  #duration of accumulation in minutes here 3h
    >>> data_path = parentdir + '/test_data/stage4_composites/'
    >>> data_recipe = 'ST4.%Y%m%d%H.01h' #note the '01h' for a 1h accumulation file
    >>> dat_dict = radar_tools.get_accumulation(end_date=end_date,
    ...                                         duration=duration,
    ...                                         data_path=data_path,
    ...                                         data_recipe=data_recipe,
    ...                                         dest_lon=gem_lon,   #lat/lon of 10km grid
    ...                                         dest_lat=gem_lat,
    ...                                         smooth_radius=5.)  #use smoothing radius of 5km for the interpolation
    >>> 
    >>> #show data
    >>> fig_name ='_static/stageIV_3h_accum_10km_grid.svg'
    >>> title = '3h accumulation on 10km grid'
    >>> units = '[mm]'
    >>> data       = dat_dict['accumulation']
    >>> latitudes  = gem_lat
    >>> longitudes = gem_lon
    >>> plot_img(fig_name, title, units, data, latitudes, longitudes,
    ...          acc_color_map, equal_legs=True)


    .. image:: _static/stageIV_3h_accum_10km_grid.svg
        :align: center



