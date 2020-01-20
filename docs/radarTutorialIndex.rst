domradar
====================================

The module radar_tools allows to access radar mosaics in various formats
and process the data in different ways. 
Data from different sources is obtained transparently and various 
interpolation and filtering options are provided.

The radar mosaics are accessed via two
functions:
    * *getInstantaneous* for instantaneous reflectivity or precipitation rates
    * *getAccumulations* for precipitation accumulations 

These two functions are very similar, *getAccumulations* itself calling
*getInstantaeous* repeatedly in order to construct accumulations on the fly.

This tutorial demonstrates the different operations that can be performed.

.. toctree::
   :maxdepth: 3

   radarTutorial

.. include:: radarTutorial
