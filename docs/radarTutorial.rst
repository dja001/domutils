
Tutorial setup 
----------------------------------------------

This section defines plotting functions and objects that will be used throughout this 
tutorial. 
You can skip to the next section for the radar related stuff. 

Here we setup a function to display images from the 
data that we will be reading:

    >>> def plotImg(figName, title, units, data, latitudes, longitudes,
    ...             colorMap, equal_legs=False ):
    ...
    ...     import matplotlib.pyplot as plt
    ...     import cartopy.crs as ccrs
    ...     import cartopy.feature as cfeature
    ...     import geo_tools
    ... 
    ...     #pixel density of image to plot
    ...     ratio = .8
    ...     hpix = 600.       #number of horizontal pixels
    ...     vpix = ratio*hpix #number of vertical pixels
    ...     imgRes = (int(vpix),int(hpix))
    ... 
    ...     #size of image to plot
    ...     figW = 7.                     #size of figure
    ...     figH = 5.5                     #size of figure
    ...     recW = 5.8/figW               #size of axes
    ...     recH = ratio*(recW*figW)/figH #size of axes
    ...     spW  = 1.5/figW               #horizontal space between axes
    ...     spH  = 1./figH                #vertical space between axes
    ... 
    ...     #setup cartopy projection
    ...     central_longitude=-94.
    ...     central_latitude=35.
    ...     standard_parallels=(30.,40.)
    ...     proj_aea = ccrs.AlbersEqualArea(central_longitude=central_longitude,
    ...                                     central_latitude=central_latitude,
    ...                                     standard_parallels=standard_parallels)
    ...     mapExtent=[-104.8,-75.2,27.8,48.5]  
    ...
    ...     #instantiate projection object 
    ...     projInds = geo_tools.projInds(srcLon=longitudes, srcLat=latitudes,
    ...                                   extent=mapExtent, destCrs=proj_aea, image_res=imgRes)
    ...     #use it to project data to image space
    ...     projectedData = projInds.project_data(data)
    ... 
    ...     #instantiate figure
    ...     fig = plt.figure(figsize=(figW,figH))
    ... 
    ...     #axes for data
    ...     x0 = 0.01
    ...     y0 = .1
    ...     ax1 = fig.add_axes([x0,y0,recW,recH], projection=proj_aea)
    ...     ax1.set_extent(mapExtent)
    ... 
    ...     #add title 
    ...     dum = ax1.annotate(title, size=20,
    ...                        xy=(.02, .9), xycoords='axes fraction',
    ...                        bbox=dict(boxstyle="round", fc='white', ec='white'))
    ... 
    ...     #plot data & palette
    ...     colorMap.plot_data(ax=ax1,data=projectedData, 
    ...                        palette='right', pal_units=units, pal_format='{:2.0f}', 
    ...                        equal_legs=equal_legs)   
    ... 
    ...     #add political boundaries
    ...     ax1.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, edgecolor='0.2')
    ... 
    ...     #plot border 
    ...     #projInds.plotBorder(ax1, linewidth=.5)
    ... 
    ...     #save output
    ...     plt.savefig(figName,dpi=400)
    ...     plt.close(fig)

Let's also initialize some color mapping objects for the different 
quantities that will be displayed.
See :ref:`legsTutorial` for details.

    >>> import legs
    >>>
    >>> #flags
    >>> undetect = -3333.
    >>> missing  = -9999.
    >>>
    >>> #Color mapping object for reflectivity
    >>> refColorMap = legs.pal_obj(range_arr=[0.,60.],
    ...                            n_col=6,
    ...                            over_high='extend', under_low='white',
    ...                            excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    >>>
    >>> #Color mapping object for quality index
    >>> pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
    ...            [[255,185,255],[147, 78,172]],  #pale/dark purple
    ...            [[255,227,215],[205,144, 73]],  #pale/dark brown
    ...            [[210,235,255],[ 58,134,237]],  #pale/dark blue
    ...            [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    >>> #quality index
    >>> qiColorMap = legs.pal_obj(range_arr=[0.,1.],
    ...                            dark_pos='high',
    ...                            color_arr=pastel,
    ...                            excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])
    >>>
    >>> #precip Rate
    >>> ranges = [.1,1.,2.,4.,8.,16.,32.]
    >>> prColorMap = legs.pal_obj(range_arr=ranges,
    ...                          n_col=6,
    ...                          over_high='extend', under_low='white',
    ...                          excep_val=[undetect,missing], excep_col=['grey_200','grey_120'])



Get radar mosaics from different sources and file formats
-----------------------------------------------------------------


Baltrad ODIM H5 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Let's read reflectivity fields from an ODIM H5 composite file using the
    *getInstantaneous* method.

    >>> import datetime
    >>> import radar_tools
    >>>
    >>> #when we want data
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>>
    >>> #where is the data
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>>
    >>> #how to construct filename. 
    >>> #   See documentation for the *strftime* method in the datetime module
    >>> #   Note the *.h5* extention, this is where we specify that we want ODIM H5 data
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #get reflectivity on native grid
    >>> #with latlon=True, we will also get the data coordinates
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True)
    >>> #show what we just got
    >>> for key in datDict.keys():
    ...     if key == 'validDate':
    ...         print(key,datDict[key])
    ...     else:
    ...         print(key,datDict[key].shape)
    reflectivity (2882, 2032)
    totalQualityIndex (2882, 2032)
    validDate 2019-10-31 16:30:00+00:00
    latitudes (2882, 2032)
    longitudes (2882, 2032)
    >>> 
    >>> #show data
    >>> figName ='_static/original_reflectivity.svg' 
    >>> title = 'Odim H5 reflectivity on original grid'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>>
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    Dark grey represents missing values, light grey represent the *undetect* value. 

    .. image:: _static/original_reflectivity.svg
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
    
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> #URP 4km reflectivity mosaics
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/operation.radar.Composite-USACDN-4km.precipet.std-rpn/'
    >>> #note the *.stnd* extension specifying that a standard file will be read
    >>> dataRecipe = '%Y%m%d%H_%Mref_4.0km.stnd'
    >>> 
    >>> #exactly the same command as before
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True)
    >>> for key in datDict.keys():
    ...     if key == 'validDate':
    ...         print(key,datDict[key])
    ...     else:
    ...         print(key,datDict[key].shape)
    reflectivity (1650, 1500)
    totalQualityIndex (1650, 1500)
    validDate 2019-10-31 16:30:00+00:00
    latitudes (1650, 1500)
    longitudes (1650, 1500)
    >>> 
    >>> #show data
    >>> figName ='_static/URP4km_reflectivity.svg' 
    >>> title = 'URP 4km reflectivity on original grid'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> 
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/URP4km_reflectivity.svg
        :align: center

Another 'mosaic' product 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    The *mosaic* product is also supported.

    >>> #2km reflectivity mosaics
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/operation.radar.mosaic/'
    >>> #Note how these files have no extensions
    >>> dataRecipe = '%Y%m%d%H_%Mref_2km_et'
    >>> 
    >>> #exactly the same command as before
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True)
    >>> for key in datDict.keys():
    ...     if key == 'validDate':
    ...         print(key,datDict[key])
    ...     else:
    ...         print(key,datDict[key].shape)
    reflectivity (3130, 2788)
    totalQualityIndex (3130, 2788)
    validDate 2019-10-31 16:30:00+00:00
    latitudes (3130, 2788)
    longitudes (3130, 2788)
    >>> 
    >>> #show data
    >>> figName ='_static/mosaic2km_reflectivity.svg' 
    >>> title = 'operation.mosaic 2km reflectivity'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>>
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/mosaic2km_reflectivity.svg
        :align: center


Get the nearest radar data to a given date and time
-----------------------------------------------------------------

    Getting the nearest radar data to an arbitrary validity time is convenient for comparison
    with model outputs at higher temporal resolutions. 

    By default, *getInstantaneous* returns None if the file does not exist
    at the specified time.
    
    >>> #set time at 16h35 where no mosaic file exists
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 35, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe)
    >>> print(datDict)
    None

    Set the *nearestTime* keyword to the temporal resolution of the data
    to rewind time to the closest available mosaic.

    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        nearestTime=10)
    >>> #note how the validDate is different from the one that was requested 
    >>> #in the function call
    >>> print(datDict['validDate'])
    2019-10-31 16:30:00+00:00


Get precipitation rates (in mm/h) from reflectivity (in dBZ)
---------------------------------------------------------------------

    By default, exponential drop size distributions are assumed 
    with 

        Z = aR^b

    in linear 
    units.
    The default is to use WDSSR's relation with  a=300 and b=1.4.

    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #require precipitation rate in the output
    >>> datDict = radar_tools.getInstantaneous(desiredQuantity='precipRate',
    ...                                        validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True)
    >>> 
    >>> #show data  
    >>> figName ='_static/odimh5_reflectivity_300_1p4.svg' 
    >>> title = 'precip rate with a=300, b=1.4 '
    >>> units = '[mm/h]'
    >>> data       = datDict['precipRate']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>>
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         prColorMap, equal_legs=True)

    .. image:: _static/odimh5_reflectivity_300_1p4.svg
        :align: center

    Different Z-R relationships can be used by specifying the a and b coefficients
    explicitely (for example, for the Marshall-Palmer DSD, a=200 and b=1.6):

    >>> #custom coefficients a and b
    >>> datDict = radar_tools.getInstantaneous(desiredQuantity='precipRate',
    ...                                        coefA=200, coefB=1.6,
    ...                                        validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True)
    >>> 
    >>> #show data
    >>> figName ='_static/odimh5_reflectivity_200_1p6.svg' 
    >>> title = 'precip rate with a=200, b=1.6 '
    >>> units = '[mm/h]'
    >>> data       = datDict['precipRate']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> 
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         prColorMap, equal_legs=True)

    .. image:: _static/odimh5_reflectivity_200_1p6.svg
        :align: center


Apply  a median filter to reduce speckle (noise) 
-----------------------------------------------------------------

    Baltrad composites are quite noisy. For some applications, it may be desirable to apply 
    a median filter to reduce speckle. 
    This is done using the *medianFilt* keyword. 
    The filtering is applied both to the reflectivity or rain rate data and to its accompanying quality index. 

    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>>  
    >>> #Apply median filter by setting *medianFilt=3* meaning that a 3x3 boxcar 
    >>> #will be used for the filtering
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True,
    ...                                        medianFilt=3)
    >>> 
    >>> #show data
    >>> figName ='_static/speckle_filtered_reflectivity.svg' 
    >>> title = 'Skpeckle filtered Odim H5 reflectivity'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> 
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/speckle_filtered_reflectivity.svg
        :align: center


Interpolation to a different grid
-----------------------------------------------------------------

    Interpolation to a different output grid can be done using the *destLat* and 
    *destLon* keywords.
    
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
    >>> with open('/home/dja001/shared_code/python_test_data/pal_demo_data.pickle', 'rb') as f:
    ...     dataDict = pickle.load(f)
    >>> gemLons = dataDict['longitudes']    #2D longitudes [deg]
    >>> gemLats = dataDict['latitudes']     #2D latitudes  [deg]


Nearest neighbor 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> #get data on destination grid using nearest neighbor
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True,
    ...                                        destLon=gemLons, 
    ...                                        destLat=gemLats)
    >>> 
    >>> #show data
    >>> figName ='_static/nearest_interpolation_reflectivity.svg' 
    >>> title = 'Nearest Neighbor to 10 km grid'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/nearest_interpolation_reflectivity.svg
        :align: center


Average all inputs falling within a destination grid tile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    >>> #get data on destination grid using averaging
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True,
    ...                                        destLon=gemLons, 
    ...                                        destLat=gemLats,
    ...                                        average=True)
    >>> 
    >>> #show data
    >>> figName ='_static/average_interpolation_reflectivity.svg' 
    >>> title = 'Average to 10 km grid'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/average_interpolation_reflectivity.svg
        :align: center


Average all inputs within a radius
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This method allows to smooth the data at the same time
    as it is interpolated. 


    >>> #get data on destination grid averaging all points
    >>> #within a circle of a given radius
    >>> #also apply the median filter on input data
    >>> thisDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> datDict = radar_tools.getInstantaneous(validDate=thisDate, 
    ...                                        dataPath=dataPath,
    ...                                        dataRecipe=dataRecipe,
    ...                                        latlon=True,
    ...                                        destLon=gemLons, 
    ...                                        destLat=gemLats,
    ...                                        medianFilt=3,
    ...                                        smoothRadius=12.)
    >>> 
    >>> #show data
    >>> figName ='_static/smooth_radius_interpolation_reflectivity.svg' 
    >>> title = 'Average input within a radius of 12 km'
    >>> units = '[dBZ]'
    >>> data       = datDict['reflectivity']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         refColorMap)

    .. image:: _static/smooth_radius_interpolation_reflectivity.svg
        :align: center
           
    

On-the-fly computation of precipitation accumulations 
-----------------------------------------------------------------
    Use the *getAccumulation* method to get accumulations of precipitation.
    Three quantities can be outputted:
        - *accumulation*  The default option; returns the amount of water (in mm);
        - *avgPrecipRate* For average precipitation rate (in mm/h) during the accumulation period;     
        - *reflectivity*  For the reflectivity (in dBZ) associated with the average precipitation rate
          during the accumulation period;

    For this example, let's get the accumulated amount of water in mm during a period of one 
    hour.


    >>> #1h accumulations of precipitation
    >>> endDate = datetime.datetime(2019, 10, 31, 16, 30, 0)
    >>> duration = 60.  #duration of accumulation in minutes
    >>> dataPath='/home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/'
    >>> dataRecipe = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
    >>> datDict = radar_tools.getAccumulation(endDate=thisDate, 
    ...                                       duration=duration,
    ...                                       dataPath=dataPath,
    ...                                       dataRecipe=dataRecipe,
    ...                                       latlon=True)
    >>> 
    >>> #show data
    >>> figName ='_static/one_hour_accum_orig_grid.svg' 
    >>> title = '1h accumulation original grid'
    >>> units = '[mm]'
    >>> data       = datDict['accumulation']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         prColorMap, equal_legs=True)

    .. image:: _static/one_hour_accum_orig_grid.svg
        :align: center


    The *getAccumulation* method is very similar to *getInstantaneous*. 
    All the features presented above also work with this method. 

    For this last  example, we apply a median filter on the original data, we get the total amount of 
    water during a period of one hour and interpolate the result to a different grid using the 
    *smoothRadius* keyword.
    We also set *verbose=1* to get a description of what is going on under the hood. 

    >>> datDict = radar_tools.getAccumulation(endDate=thisDate, 
    ...                                       duration=duration,
    ...                                       dataPath=dataPath,
    ...                                       dataRecipe=dataRecipe,
    ...                                       destLon=gemLons, 
    ...                                       destLat=gemLats,
    ...                                       medianFilt=3,
    ...                                       smoothRadius=12.,
    ...                                       latlon=True,
    ...                                       verbose=1)
    getAccumulation starting
    getInstantaneous, getting data for:  2019-10-31 16:30:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311630.h5
    getInstantaneous, applying median filter
    getInstantaneous, getting data for:  2019-10-31 16:20:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311620.h5
    getInstantaneous, applying median filter
    getInstantaneous, getting data for:  2019-10-31 16:10:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311610.h5
    getInstantaneous, applying median filter
    getInstantaneous, getting data for:  2019-10-31 16:00:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311600.h5
    getInstantaneous, applying median filter
    getInstantaneous, getting data for:  2019-10-31 15:50:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311550.h5
    getInstantaneous, applying median filter
    getInstantaneous, getting data for:  2019-10-31 15:40:00
    readH5Composite: reading: b'DBZH' from: /home/ords/mrd/rpndat/dja001/shared_code/python_test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311540.h5
    getInstantaneous, applying median filter
    getAccumulation, computing average precip rate in accumulation period
    getAccumulation, interpolating to destination grid
    getAccumulation computing accumulation from avg precip rate
    getAccumulation done
    >>> 
    >>> #show data
    >>> figName ='_static/one_hour_accum_interpolated.svg' 
    >>> title = '1h accum, filtered and interpolated'
    >>> units = '[mm]'
    >>> data       = datDict['accumulation']
    >>> latitudes  = datDict['latitudes']
    >>> longitudes = datDict['longitudes']
    >>> plotImg(figName, title, units, data, latitudes, longitudes,
    ...         prColorMap, equal_legs=True)

    .. image:: _static/one_hour_accum_interpolated.svg
        :align: center




