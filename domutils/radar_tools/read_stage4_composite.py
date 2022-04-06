from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping

def read_stage4_composite(st4_file:   str=None,
                          latlon:     Optional[bool] = False,
                          no_data:    Optional[float]= -9999.,
                          verbose:    Optional[int]  = 0) :

    """ Read Stage IV precipitation accumulations available at:
        
        https://data.eol.ucar.edu/dataset/21.093
        
        Quality index is set to 1 wherever data is not missing



    Args:

        st4_file:        /path/to/st4/ST4.YYYYMMDDHH.06.h or 
                         /path/to/st4/ST4.YYYYMMDDHH.24.h or 
                         /path/to/st4/ST4.YYYYMMDDHH.01.h
        latlon:          When true, will output latitudes and longitudes
        no_data:         Value that will be assigned to missing values

   
    **** 
    WARNING: when downloading stIV files the files: st4_pr.YYYYMMDDHH.06.h 
            is for the Caribean domain while ST4.YYYYMMDDHH.06.h is for 
            the North American domain 
    ***
    
    Returns:
        None:            If no or invalid file present

        or 

        { 
            'accumulation':       (ndarray) 2D accumulation 

            'total_quality_index':  (ndarray) 2D quality index

            'valid_date':          (python datetime object) date of validity

            'latitudes':          (ndarray) 2d latitudes  of data (conditional on latlon = True)

            'longitudes':         (ndarray) 2d longitudes of data (conditional on latlon = True)
        }

    Example:

           >>> #read st4 file
           >>> import os, inspect
           >>> import domutils.radar_tools as radar_tools
           >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
           >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
           >>> dirdata = os.path.dirname(os.path.dirname(parentdir))
           >>> out_dict = radar_tools.read_stage4_composite(parentdir + '/test_data/stage4_composites/ST4.2019082000.06h')
           >>> accumulation        = out_dict['accumulation']
           >>> total_quality_index = out_dict['total_quality_index']
           >>> valid_date          = out_dict['valid_date']
           >>> print(accumulation.shape)
           (1650, 1500)
           >>> print(valid_date)
           2019-08-20 00:00:00+00:00


    """    

    import os
    import datetime
    import logging
    import time
    import numpy as np
    import os, sys, inspect
    import pygrib
    
    
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 

    #logging
    logger = logging.getLogger()

    if verbose > 0:
        logger.warning('verbose keyword is deprecated, \
                       please set logging level in calling handler')

    #checks that filename was provided and is valid
    if st4_file is None :
        raise ValueError('st4_file must be provided')
    else :
        if not os.path.isfile(st4_file) :
            #no file present print warning and return None
            logger.warning('st4_file: ' + st4_file + ' does not exist. \
                           Returning None')
            return None
    
    # first get the accumulation time step: 1, 6 or 24h
    timestep    = st4_file.split(".")[-1]
    timestepval = int(timestep[0:2])
    
    # read the grib file
    gr = pygrib.open(st4_file)
    
    # name of the precipition variable in grib file
    var_list = ["Total Precipitation"]
    
    # grib object
    grb = gr.select(name=var_list)[0]

    # get the precipitation values: format np.ma
    data = grb.values
    np.ma.set_fill_value(data, fill_value=no_data)
    values = data.filled()
    
    #make datestamp for output
    valid_date = grb.analDate + datetime.timedelta(hours=timestepval)
    
    #construct a fake quality index = 1 wherever we have data or undetect
    total_quality_index = np.ones_like(values)
            
    #constructuct output dictionary
    out_dict = {'accumulation':         values,
                'total_quality_index':  total_quality_index,
                'valid_date':           valid_date}
    

    if latlon : 
        lats, lons = grb.latlons() 
        out_dict['latitudes']  = lats
        out_dict['longitudes'] = lons
        

    return(out_dict)
           
