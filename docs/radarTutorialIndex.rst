radar_tools demo
====================================

The module radar_tools allows to access radar mosaics in various formats
and process the data in different ways. 
Data from different sources is obtained transparently and various 
interpolation and filtering options are provided.

The radar mosaics are accessed via two
functions:
    * *get_instantaneous* for instantaneous reflectivity or precipitation rates
    * *get_accumulations* for precipitation accumulations 

These two functions are very similar, *get_accumulations* itself calling
*get_instantaeous* repeatedly in order to construct accumulations on the fly.

This tutorial demonstrates the different operations that can be performed.

.. toctree::
   :maxdepth: 3

   radarTutorial

