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

..
    
    MRMS precipitation rates in grib2 format
    ----------------------------------------------
    
    Reading MRMS precipitation rates provided in grib2 format.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:mrms_grib2_begins
       :end-before: DOCS:mrms_grib2_ends
    
    
    4-km mosaics from URP
    ----------------------------------------------
    
    Working with 4-km radar mosaics from URP.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:urp_4km_begins
       :end-before: DOCS:urp_4km_ends
    
    
    Get precipitation rates (in mm/h) from reflectivity (in dBZ)
    ------------------------------------------------------------
    
    Conversion from reflectivity to precipitation rate.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:dbz_to_rr_begins
       :end-before: DOCS:dbz_to_rr_ends
    
    
    Apply a median filter to reduce speckle (noise)
    ------------------------------------------------------------
    
    Noise reduction using a median filter.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:median_filter_begins
       :end-before: DOCS:median_filter_ends
    
    
    Interpolation to a different grid
    ------------------------------------------------------------
    
    Three interpolation use cases are demonstrated.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:interpolation_begins
       :end-before: DOCS:interpolation_ends
    
    
    On-the-fly computation of precipitation accumulations
    ------------------------------------------------------------
    
    Accumulation computed during processing.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:accumulation_otf_begins
       :end-before: DOCS:accumulation_otf_ends
    
    
    Reading in stage IV accumulations
    ------------------------------------------------------------
    
    Each Stage-IV sub-case is handled separately.
    
    .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
       :language: python
       :start-after: DOCS:stage4_begins
       :end-before: DOCS:stage4_ends
    
