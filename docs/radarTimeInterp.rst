
Time interpolation using nowcasting
----------------------------------------------

Sometimes, you need reflectivity or precipitation-rates at moments in time
that do not match exactly with the time at which observational data is
available. 
Simple linear interpolation between two fields at different times will not do 
a goot job because of precipitation displacement. 

As a solution to this, the module `obs_process` provides a nowcast 
interpolation functionality. The basic idea is that data at intermediate timesteps, 
data is estimated as a weighted average of the forward advection of the 
observations before and backward advection of the observations after. 

.. image:: _static/nowcast_time_interpolation.svg
    :align: center
    :width: 800px


Interpolate a batch of observations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This section demonstrates the processing of a batch of observations 
in one call to the **obs_process** function. 
The results are then displayed in the form of a short animation.

Lets start with the required imports and directory setup:

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:setup_begins
   :end-before: DOCS:setup_ends


`obs_process` is a python script callable from the shell such as:

    .. code-block:: bash

       #process data with time interpolation
       python -m domutils.radar_tools.obs_process    \
                 --input_t0         202206150800     \
                 --input_tf         202206160000     \
                 --input_dt         10               \
                 --output_t0        202206150900     \
                 --output_tf        202206160000     \
                 --output_dt        1                \
                 --t_interp_method  'nowcast'        \
                 ...

However, for this example we will be running directly from Python
with arguments provided by the attributes of a simple object. 

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:class_begins
   :end-before: DOCS:class_ends

The processing of observations and time interpolation is done 
in one simple function call.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:process_data_begins
   :end-before: DOCS:process_data_ends

To make an animation showing the time-interpolated dat, we first define a function for plotting 
each individual panels.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:function_definition_begins
   :end-before: DOCS:function_definition_ends
    
We now setup the general characteristics of the figure being generated.
See :ref:`Legs Tutorial` for information on the definition of color mapping objects. 

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:figure_setup_begins
   :end-before: DOCS:figure_setup_ends

Now, we make individual frames of the animation.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:animation_frames_begins
   :end-before: DOCS:animation_frames_ends

Finally, an animated gif is constructed from the frames we just made,

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:animation_frames_begins
   :end-before: DOCS:animation_frames_ends

.. image:: _static/time_interpol_plain_movie.gif
    :align: center


Accumulations from time interpolated data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using nowcasting for time interpolation can be advantageous when computing 
accumulations from source data available at discrete times. 
In the example below, we compare accumulations obtained from the source data 
to accumulations obtained from the time interpolated data. 

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:accumulation_begins
   :end-before: DOCS:accumulation_ends

    The figure below shows 30 minutes precipitation accumulation computed from:
     
    - The source data every 10 minutes
    - The filtered data every 10 minutes
    - The time interpolated data every 1 minute

    In the two panels on the right, the red arrows indicate artefacts 
    that originate from the poor time resolution of the source data 
    compared to the speed at which the bow echo propagates. 

    The accumulation on the left is constructed from the time-interpolated 
    values every minute and does not display the displacement artefacts.

.. image:: _static/time_interpol_demo_accum_plain.svg
    :align: center

