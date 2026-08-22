
Temporal interpolation using nowcasting
----------------------------------------------

Nowcast-based temporal interpolation was developed to solve the three following
problems simultaneously:

#. Data is often needed at times other than the six minutes at which radar
   mosaics are available.
   For data assimilation purposes, radar data is required at time resolutions
   between 1 and 7.5 minutes, depending on the timestep of the model being used.

#. Prior to assimilation, radar data must be smoothed for its spatial resolution
   to match the effective resolution of the simulated precipitation.
   This avoids assimilating small scales that the model cannot represent.

#. The source data contains many gaps; US radars leave some when they use
   scanning routines (VCPs) longer than six minutes, and Canadian data is
   sometimes missing because of network delays.

The animation below shows the result of the interpolation for a case over
Minnesota and Wisconsin on 29 August 2022.
The top row shows the source data, available every six minutes, together with
its quality index.
The bottom row shows the interpolated precipitation rate and its quality index,
available every minute.
Note how the interpolation bridges the gap when source data is unavailable.

.. image:: _static/test_radar_time_interpolation/202208_movie.gif
    :align: center

The interpolation is performed by the **obs_process** module.
The basic idea is that the temporally interpolated data at intermediate timesteps 
is estimated as a quality-weighted aggregate of advected neighbors.
By selecting :math:`\delta_t^{\text{max}}` such that 4 or 5 neighbors contribute
to each aggregate, data gaps go mostly unnoticed. 

Motion vectors are first estimated from consecutive source mosaics using the
Lucas-Kanade optical flow of `pysteps <https://pysteps.readthedocs.io>`_.
Every source mosaic that is closer in time than :math:`\delta_t^{\text{max}}` 
then contributes to the output; each one is advected to the desired time, 
forward or backward, with a semi-Lagrangian scheme.
The weight of each contribution decreases linearly with the duration of the
advection and reaches zero at :math:`\delta_t^{\text{max}}`.
Because this weight multiplies the quality index of the advected data, an
estimate that had to be advected over a long time interval is given less
importance than one that comes from a nearby time.
The precipitation rate is the average of the advected estimates weighted by
these reduced quality indices.

.. image:: _static/illustrative/nowcast_time_interpolation.png
    :align: center
    :width: 800px


Interpolate a batch of observations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This section demonstrates the processing of a batch of observations
in one call to the **obs_process** function.
The results are then displayed in the form of a short animation.

Let's start with the required imports and directory setup:

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:setup_begins
   :end-before: DOCS:setup_ends


``obs_process`` is a python script callable from the shell such as:

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
   :class: collapse-code
   :start-after: DOCS:class_begins
   :end-before: DOCS:class_ends

We now instantiate this object for the case being demonstrated and define
the domain and the times that will be used for the figures.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:case_setup_begins
   :end-before: DOCS:case_setup_ends

The processing of observations and time interpolation is done
in one simple function call.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :start-after: DOCS:process_data_begins
   :end-before: DOCS:process_data_ends

To make an animation showing the time-interpolated data, we first define a
function for plotting each individual panel.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:function_definition_begins
   :end-before: DOCS:function_definition_ends

then we setup the general characteristics of the figure being generated.
See :ref:`Legs Tutorial` for information on the definition of color mapping objects.

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:figure_setup_begins
   :end-before: DOCS:figure_setup_ends

Individual frames of the animation are made serially or in parallel. 

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:animation_frames_begins
   :end-before: DOCS:animation_frames_ends

Finally, an animated gif is constructed from the frames we just made,

.. literalinclude:: ../domutils/radar_tools/tests/test_radar_time_interpolation.py
   :language: python
   :class: collapse-code
   :start-after: DOCS:animated_gif_begins
   :end-before: DOCS:animated_gif_ends

The animation shown at the top of this page was obtained with the code above.
Running the same code with different dates and a different domain gives the
animation below, for the derecho that crossed southern Quebec on
21 May 2022.

.. image:: _static/test_radar_time_interpolation/202205_movie.gif
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

The figure below shows the 30 minutes precipitation accumulation ending at
21:42 UTC on 21 May 2022, computed from:

- the source data, available every six minutes, on the right
- the time interpolated data, available every minute, on the left

In the panel on the right, the red arrows indicate artefacts that originate
from the coarse time resolution of the source data compared to the speed at
which the bow echo propagates.
The accumulation on the left does not display these displacement artefacts.

.. image:: _static/test_radar_time_interpolation/202205_accumulation.svg
    :align: center
