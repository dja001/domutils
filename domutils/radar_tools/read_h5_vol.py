from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def read_h5_vol(odim_file:   str=None,
                latlon:           Optional[bool] = False,
                elevations:       Optional[Any]  = 'all',
                quantities:       Optional[Any]  = 'all',
                include_quality:  Optional[bool] = False,
                no_data:          Optional[float]= -9999.,
                undetect:         Optional[float]= -3333.) :

    """ Read reflectivity and quality index from OdimH5 composite
        
    Odim H5 files are a bit annoying in that datasets and quality index are just numbered
    (data1, data2, ...) and not named following what they contain. Also, one cannot expect that 
    a dataset named 'quality3' will always contain the same quantity. 
    The result is that one has to loop over each item and check that the contents match what we 
    are looking for. 
    This routine does that as well as converting the Byte data found in H5 files to more tangible
    quantities such as reflectivity in dBZ and quality index between 0. and 1. 
    Special values are also assigned to no_data and undetect values.
    UTC time zone is assumed for datestamp in H5 file

    This code is for Volume scans in ODIM format. Reading these files is a bit different from reading
    mosaics so a different reader is necessary

    For more verbose outputs, set logging level in calling handler

    Args:
        odim_file:        /path/to/odim/composite.h5
        latlon:           When true, will output latitudes and longitudes of the returned PPIs
        elevations:       float or list of float for the desired nominal elevation. Set to 'all' to return all elevations in a file
        quantities:       desired quantities ['dbzh', 'th', 'rhohv', 'uphidp', 'wradh', 'phidp', 'zdr', 'kdp', 'sqih', 'vradh', 'dr', etc]
                          set to 'all' to return everything
        include_quality   Quality field will be included along side quantities
        no_data:          Value that will be assigned to missing values
        undetect:         Value that will be assigned to valid measurement of no precipitation

    Returns:

        a dict::

            # a dictionary which roughly mimics the structure of odim h5 files::
            # dict['elevation1']['quantity1'](2D numpy array, PPI) 
            #                   ['quantity2'](2D numpy array, PPI)
            #                      ...
            #                   ['quality_name1'](2D numpy array, PPI)
            #                   ['quality_name2'](2D numpy array, PPI)
            #                      ...
            #                   [nominal_elevation] float
            #                   [elevations] (1D numpy array, rows of values)
            #                   [azimuths]   (1D numpy array, rows of values)
            #                   [ranges]     (1D numpy array, columns of values)
            #                   [latitudes]  (2D numpy array)
            #                   [longitudes] (2D numpy array)
            # dict['elevation2']['quantity1'](2D numpy array)
            #                     ...
        or

        None:             If no or invalid file present, desires elevation or quantities not found.

    Example:

        >>> #read odim H5 file
        >>> import os, inspect
        >>> import domutils.radar_tools as radar_tools
        >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
        >>> odim_file = parentdir+'/test_data//odimh5_radar_volume_scans/2019071120_24_ODIMH5_PVOL6S_VOL.qc.casbv.h5'
        >>> res = radar_tools.read_h5_vol(odim_file=odim_file, 
        ...                               elevations=[0.4], 
        ...                               quantities=['dbzh'],
        ...                               include_quality=True,
        ...                               latlon=True)
        >>> #check returned radar dictionary
        >>> print(res.keys())
        dict_keys(['radar_height', 'radar_lat', 'radar_lon', 'date_str', '0.4'])
        >>> #
        >>> #check returned PPI dictionary
        >>> print(res['0.4'].keys())
        dict_keys(['dbzh', 'quality_beamblockage', 'quality_att', 'quality_broad', 'quality_qi_total', 'nominal_elevation', 'elevations', 'azimuths', 'ranges', 'latitudes', 'longitudes'])



    """
    import os, inspect
    import datetime
    import logging
    import pickle
    import time
    import numpy as np
    import h5py
    import domutils.radar_tools as radar_tools
    import domutils.geo_tools   as geo_tools

    #logging
    logger = logging.getLogger(__name__)

    #checks that filename was provided and is valid
    if odim_file is None :
        raise ValueError('odim_file must be provided')
    else :
        if not os.path.isfile(odim_file) :
            #no file present print warning and return None
            logger.warning('odim_file: ' + odim_file + ' does not exist. Returning None.')
            return None

    logger.info('Reading: ' + str(quantities) +' from: ' + odim_file)

    #quantities to lower caps
    quantities = [qty.lower() for qty in quantities]

    #open odim file for reading
    h5_obj = h5py.File(odim_file, 'r')

    #dictionary as output
    out_dict = {}
    output_is_empty = True

    #in volume scans datasets corresponds to nominal elevations
    full_list = list(h5_obj.keys())

    #radar info 
    file_where_dict = dict(h5_obj['where'].attrs)
    out_dict['radar_height'] = file_where_dict['height']
    out_dict['radar_lat']    = file_where_dict['lat']
    out_dict['radar_lon']    = file_where_dict['lon']
    file_what_dict = dict(h5_obj['what'].attrs)
    date_str = file_what_dict['date'].decode('utf-8')
    time_str = file_what_dict['time'].decode('utf-8')
    out_dict['date_str'] = date_str+time_str

    #iterate over datasets and quality fields
    for l1 in full_list :

        if l1.startswith('dataset') :
            #retrieve name of dataset to read later
            dataset_name = l1
            #retrieve date of measurement
            dataset_where_dict = dict(h5_obj[dataset_name]['where'].attrs)
            this_elevation = dataset_where_dict['elangle']

            elevation_str = '{:02.1f}'.format(this_elevation)

            if elevations == 'all' or np.any(np.isclose(this_elevation, elevations))  :
                #try to get desired quantity 

                #search through data entries for what we want
                found_something = False
                this_dataset = h5_obj[dataset_name]
                for l2 in this_dataset :
                    if l2.startswith('data') :
                        #check attributes for quantity being represented
                        data_what_dict = dict(this_dataset[l2]['what'].attrs)
                        this_quantity = data_what_dict['quantity'].decode('utf-8').lower()
                        if str(this_quantity) in quantities:
                            #we have the quantity we were looking for
                            found_something = True
                            output_is_empty = False

                            #create dict entry if not already there
                            if elevation_str not in out_dict.keys():
                                out_dict[elevation_str] = {}

                            data_gain     = data_what_dict['gain']
                            data_no_data  = data_what_dict['nodata']
                            data_offset   = data_what_dict['offset']
                            data_undetect = data_what_dict['undetect']
                            data_byte = np.asarray(this_dataset[l2]['data'])
                            #
                            #reconstruct values from Byte data
                            data_float = data_byte * data_gain + data_offset
                            #assign no_data
                            data_float = np.where(data_byte == data_no_data,  no_data,  data_float)
                            #assign undetect
                            data_float = np.where(data_byte == data_undetect, undetect, data_float)

                            #data values for output
                            out_dict[elevation_str][this_quantity] = data_float

                    if include_quality and l2.startswith('quality') :
                        data_how_dict = dict(this_dataset[l2]['how'].attrs)
                        quality_name = 'quality_'+data_how_dict['task'].decode('utf-8').split('.')[-1]
                        #
                        data_what_dict = dict(this_dataset[l2]['what'].attrs)
                        data_gain     = data_what_dict['gain']
                        data_offset   = data_what_dict['offset']
                        data_byte = np.asarray(this_dataset[l2]['data'])
                        #
                        #reconstruct values from Byte data
                        data_float = data_byte * data_gain + data_offset
                        #
                        #data values for output
                        out_dict[elevation_str][quality_name] = data_float

                if found_something:
                    #add meta data for the retrieved field(s)
                    #
                    out_dict[elevation_str]['nominal_elevation'] = this_elevation
                    #
                    data_how_dict = dict(this_dataset['how'].attrs)
                    out_dict[elevation_str]['elevations'] = np.asarray(data_how_dict['elangles'])
                    out_dict[elevation_str]['azimuths']   = np.asarray(data_how_dict['azangles'])
                    #
                    data_where_dict = dict(this_dataset['where'].attrs)
                    range_values = data_where_dict['rstart'] + data_where_dict['rscale']/2. + np.arange(0, data_where_dict['nbins'])*data_where_dict['rscale']
                    out_dict[elevation_str]['ranges'] = range_values

                    if latlon:
                        #base info
                        ll_elevations = out_dict[elevation_str]['elevations']
                        ll_ranges     = out_dict[elevation_str]['ranges'] 
                        ll_azimuths   = out_dict[elevation_str]['azimuths'] 
                        radar_lat     = out_dict['radar_lat']
                        radar_lon     = out_dict['radar_lon']
                        radar_height  = out_dict['radar_height'] 
                        #on 2D grid
                        melevs, mranges = np.meshgrid(ll_elevations, ll_ranges, indexing='ij')
                        #distance following curvature of the earth  /1e3 since this function takes km in
                        dist_earth = radar_tools.model_43(elev=melevs, dist_beam=mranges/1e3, hrad=radar_height/1e3, want='dist_earth')
                        #compute the lat/lon values associated with a given PPI
                        longitudes, latitudes = geo_tools.lat_lon_range_az(radar_lon, radar_lat, dist_earth, ll_azimuths[:,np.newaxis])
                        #save output
                        out_dict[elevation_str]['latitudes']  = latitudes
                        out_dict[elevation_str]['longitudes'] = longitudes

    h5_obj.close()


    if output_is_empty:
        return None
    else:
        return out_dict 

           

if __name__ == "__main__":
    import doctest
    doctest.testmod()
