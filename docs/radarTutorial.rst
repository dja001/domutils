Tutorial setup
----------------------------------------------

This section defines plotting functions and objects that will be used throughout this
tutorial. You can skip to the next section for the radar related stuff.

Here we setup a function to display images from the 
data that we will be reading:

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
   :language: python
   :start-after: DOCS:plot_img_begins
   :end-before: DOCS:plot_img_ends

Let's also initialize some color mapping objects for the different 
quantities that will be displayed (see :ref:`legs Tutorial` for details).

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
   :language: python
   :start-after: DOCS:values_and_palette_begins
   :end-before: DOCS:values_and_palette_ends

Get radar mosaics from different sources and file formats
-----------------------------------------------------------------


Baltrad ODIM H5 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Let's read reflectivity fields from an ODIM H5 composite file using the
    *get_instantaneous* method.

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:baltrad_odim_h5_begins
       :end-before: DOCS:baltrad_odim_h5_ends

    Dark grey represents missing values, light grey represent the *undetect* value. 

    .. image:: _static/original_reflectivity.svg
        :align: center

    
MRMS precipitation rates in grib2 format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Reading precipitation rates from MRMS is done in a very similar way with the 
    *get_instantaneous* method.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:mrms_grib2_begins
       :end-before: DOCS:mrms_grib2_ends

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
    
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:urp_4km_begins
       :end-before: DOCS:urp_4km_ends

    .. image:: _static/URP4km_reflectivity.svg
        :align: center
    
    
Get the nearest radar data to a given date and time
-----------------------------------------------------------------

    Getting the nearest radar data to an arbitrary validity time is convenient for comparison
    with model outputs at higher temporal resolutions. 

    By default, *get_instantaneous* returns None if the file does not exist
    at the specified time.

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:return_none_begins
       :end-before: DOCS:return_none_ends
    
    Set the *nearest_time* keyword to the temporal resolution of the data
    to rewind time to the closest available mosaic.

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:nearest_time_begins
       :end-before: DOCS:nearest_time_ends


Get precipitation rates (in mm/h) from reflectivity (in dBZ)
---------------------------------------------------------------------

    By default, exponential drop size distributions are assumed 
    with 

        Z = aR^b

    in linear 
    units.
    The default is to use WDSSR's relation with  a=300 and b=1.4.

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:wdssr_zr_begins
       :end-before: DOCS:wdssr_zr_ends

    .. image:: _static/odimh5_reflectivity_300_1p4.svg
        :align: center

    Different Z-R relationships can be used by specifying the a and b coefficients
    explicitly (for example, for the Marshall-Palmer DSD, a=200 and b=1.6):

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:200_1.6_begins
       :end-before: DOCS:200_1.6_ends

    .. image:: _static/odimh5_reflectivity_200_1p6.svg
        :align: center


Apply  a median filter to reduce speckle (noise) 
-----------------------------------------------------------------

    Baltrad composites are quite noisy. For some applications, it may be desirable to apply 
    a median filter to reduce speckle. 
    This is done using the *median_filt* keyword.
    The filtering is applied both to the reflectivity or rain rate data and to its accompanying quality index. 

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:median_filter_begins
       :end-before: DOCS:median_filter_ends

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
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:interpolation_setup_begins
       :end-before:  DOCS:interpolation_setup_ends


Nearest neighbor 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:nearest_neighbor_begins
       :end-before: DOCS:nearest_neighbor_ends

    .. image:: _static/nearest_interpolation_reflectivity.svg
        :align: center


Average all inputs falling within a destination grid tile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:average_in_tile_begins
       :end-before: DOCS:average_in_tile_ends

    .. image:: _static/average_interpolation_reflectivity.svg
        :align: center


Average all inputs within a radius
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This method allows to smooth the data at the same time
    as it is interpolated. 

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:average_in_radius_begins
       :end-before: DOCS:average_in_radius_ends
        
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

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:compute_accumulation_begins
       :end-before: DOCS:compute_accumulation_ends

    .. image:: _static/one_hour_accum_orig_grid.svg
        :align: center

    The *get_accumulation* method is very similar to *get_instantaneous*.
    All the features presented above also work with this method. 

    For this last  example, we apply a median filter on the original data, we get the total amount of 
    water during a period of one hour and interpolate the result to a different grid using the 
    *smooth_radius* keyword.

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:combine_options_begins
       :end-before: DOCS:combine_options_ends

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
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:stage_4_basic_begins
       :end-before: DOCS:stage_4_basic_ends

    .. image:: _static/stageIV_six_hour_accum_orig_grid.svg
        :align: center

Read one file, interpolate to a different grid, convert to average precipitation rate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    The *get_accumulation* method becomes more usefull if you want to  interpolate the data at the 
    same time that it is read and/or if you want to compute derived quantities.

    In this next example, we read the same 6h accumulation file but this time, we will
    get the average precipitation rate over the 10km grid used in the previous example. 

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:stage_4_manipulate_begins
       :end-before: DOCS:stage_4_manipulate_ends

    .. image:: _static/stageIV_six_hour_pr_10km_grid.svg
        :align: center


Construct accumulation from several files 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Finally, use the *get_accumulation* method to construct accumulations of arbitrary length
    from stage IV accumulations. 

    Here, we construct a 3h accumulation from three consecutive 1h accumulations. 
    As before, the data is interpolated to a 10 km grid. 

    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:stage_4_build_accum_begins
       :end-before: DOCS:stage_4_build_accum_ends

    .. image:: _static/stageIV_3h_accum_10km_grid.svg
        :align: center




        


