Legs Tutorial
====================================

A **leg** can 
be `defined <https://www.merriam-webster.com/dictionary/leg/>`_ as:

    * *a portion of a trip* 
    * *one section of a relay race*

Here the race happens in data space and goes from - infinity to + infinity. 

The general idea is to assign a number of distinct color mappings, hereafter 
called legs,  to contiguous portions of this (quite large) range.

.. image:: _static/legs_principle.svg
    :align: center
    :width: 600px

There can be any number of legs and what happens beyond the range of the color mapping must 
be specified explicitly.
A mechanism is also provided for assigning colors to any number of exception values.

By doing so, it becomes easy to create and modify continuous, semi-continuous, categorical 
and divergent color mappings. 

This tutorial demonstrates how to construct custom color mappings. 
Elements covered include:


.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none



Very basic color mapping
----------------------------------------------

For this tutorial, lets start by making data and setting up figure
information.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:setup_begins
   :end-before: DOCS:setup_ends


The default color mapping applies a black and wite gradient in the interval [0,1].

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:default_cm_begins
   :end-before: DOCS:default_cm_ends

.. image:: _static/default.svg
    :align: center

Data values above and below the color palette
----------------------------------------------


The default behavior is to throw an error if data values are found beyond the range of 
of the color palette.
The following code will fail and give you suggestions as to what to do.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:fails_extending_begins
   :end-before: DOCS:fails_extending_ends

:language: python
    Traceback (most recent call last):
      File "/fs/site3/eccc/mrd/rpndat/dja001/python_miniconda3/envs/domutils_dev/lib/python3.7/doctest.py", line 1330, in __run
        compileflags, 1), test.globs)
      File "<doctest legsTutorial.rst[35]>", line 2, in <module>
        palette='right', pal_format='{:2.0f}')
      File "/fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/domutils/legs/legs.py", line 405, in plot_data
        out_rgb = self.to_rgb(rdata)
      File "/fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/domutils/legs/legs.py", line 473, in to_rgb
        validate.no_unmapped(data_flat, action_record, self.lows, self.highs)
      File "/fs/homeu1/eccc/mrd/ords/rpndat/dja001/python/packages/domutils_package/domutils/legs/validation_tools/no_unmapped.py", line 103, in no_unmapped
        raise RuntimeError(err_mess)
    RuntimeError: 
    <BLANKLINE>
    Found data point(s) smaller than the minimum of an exact palette:
      [-0.19458771 -0.19446921 -0.19434859 -0.19434811 -0.19422583]...
    <BLANKLINE>
    <BLANKLINE>
    Found data point(s) larger than the maximum of an exact palette:
      [1.00004429 1.00055305 1.00060393 1.0008584  1.00101111]...
    <BLANKLINE>
    <BLANKLINE>
    One possibility is that the data value(s) exceed the palette
    while they should not.
       For example: correlation coefficients greater than one.
       In this case, fix your data.
    <BLANKLINE>
    Another possibility is that data value(s) is (are) expected  
    above/below the palette.
    In this case:
      1- Use the "over_under","over_high" or "under_low" keywords to explicitly
         assign a color to data values below/above the palette.
      2- Assign a color to exception values using the "excep_val" and "excep_col" keywords.
         For example: excep_val=-9999., excep_col="red".
    <BLANKLINE>


Lets assume that we expected data values to exceed the [0,1] range where the color
palette is defined. 
Then we should use the keywords **over_under** or **under_low** and **over_high** 
to avoid errors.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:extend_demo_begins
   :end-before: DOCS:extend_demo_ends


.. image:: _static/default_extend.svg
    :align: center


Exceptions
--------------

Exception values to a color mapping come in many forms:

    - Missing values from a dataset
    - Points outside of a simulation domain
    - The zero value when showing the difference between two things
    - Water in a topographical map / Land in vertical cross-sections
    - etc.

Being able to easily assign colors values allows for all figures of a given
manuscript/article to show missing data with the same color. 

There can be any number of exceptions associated with a given color mapping.
These exceptions have precedence over the regular color mapping and will show up
in the associated color palette.

Data points that are outside of an exact color mapping but that are covered 
by an exception will not trigger an error. 

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:default_exceptions_begins
   :end-before: DOCS:default_exceptions_ends

.. image:: _static/default_exceptions.svg
    :align: center


Specifying colors
--------------------------

Up to nine legs using linear gradient mapping are specified by default. 
They can be called by name.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:nine_legs_begins
   :end-before: DOCS:nine_legs_ends

.. image:: _static/default_linear_legs.svg
    :align: center


Semi-continuous, semi-quantitative color mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The keyword **n_col** will create a palette from the default legs in
the order in which they appear above.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:n_col_begins
   :end-before: DOCS:n_col_ends

.. image:: _static/default_6cols.svg
    :align: center


The keyword **color_arr** can be used to make a mapping from the default color 
legs in whatever order.
It can also be used to make custom color legs from RGB values. 
By default linear interpolation is used between the provided RGB. 

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:color_arr_begins
   :end-before: DOCS:color_arr_ends

.. image:: _static/col_arr_demo.svg
    :align: center


Categorical, quantitative color mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The keyword **solid** is used for generating categorical palettes.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:solid_begins
   :end-before: DOCS:solid_ends

.. image:: _static/solid_demo.svg
    :align: center


Divergent color mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The keyword **dark_pos** is useful for making divergent palettes.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:dark_pos_begins
   :end-before: DOCS:dark_pos_ends

.. image:: _static/dark_pos_demo.svg
    :align: center

Quantitative divergent color mappings can naturally be made using the **solid** keyword. 

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:solid_divergent_begins
   :end-before: DOCS:solid_divergent_ends

.. image:: _static/solid_divergent.svg
    :align: center


Colors legs covering unequal range intervals
----------------------------------------------

So far, the keyword **range_arr** has been used to determine the range
of the entire color mapping. 
It can also be used to define color legs with different extents.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:unequal_range_begins
   :end-before: DOCS:unequal_range_ends

.. image:: _static/different_ranges.svg
    :align: center


Separate plotting of data and palette
----------------------------------------------

When multiple pannels are plotted, it is often convenient to separate
the display of data form that of the palette. 
In this example, two color mappings are used first separately and then together.

.. literalinclude:: ../domutils/legs/tests/test_legs_tutorial.py
   :language: python
   :start-after: DOCS:separate_begins
   :end-before: DOCS:separate_ends

.. image:: _static/separate_data_palettes.svg
    :align: center
