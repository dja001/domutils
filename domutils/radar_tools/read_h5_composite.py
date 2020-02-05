from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping

def read_h5_composite(odim_file:   str=None,
                      latlon:      Optional[bool] = False,
                      qced:        Optional[bool] = True,
                      no_data:     Optional[float]= -9999.,
                      undetect:    Optional[float]= -3333.,
                      latlon_file: Optional[str]= None,
                      verbose:     Optional[int]  = 0) :

    """ Read reflectivity and quality index from OdimH5 composite
        
    Odim H5 files are a bit annoying in that datasets and quality index are just numbered
    (data1, data2, ...) and not named following what thay contain. Also, one cannot expect that 
    a dataset named 'quality3' will always contain the same quantity. 
    The result is that one has to loop over each item and check that the contents match what we 
    are looking for. 
    This routine does that as well as converting the Byte data found in H5 files to more tangible
    quantities such as reflectivity in dBZ and quality index between 0. and 1. 
    Special values are also assigned to no_data and undetect values.
    UTC time zone is assumed for datestamp in H5 file

    Args:
        odim_file:        /path/to/odim/composite.h5
        latlon:           When true, will output latitudes and longitudes of the odim grid
        qced:             When true (default), Quality Controlled reflectivity (DBZH) will be returned.
                          When false, raw reflectivity (TH) will be returned.
        no_data:          Value that will be assigned to missing values
        undetect:         Value that will be assigned to valid measurement of no precipitation
        latlon_file:      pickle file containing latlon of domain (only used if latlon=True)

    Returns:
        None:             If no or invalid file present

        or 

        { 
            'reflectivity':        (ndarray) 2D reflectivity

            'total_quality_index': (ndarray) 2D quality index

            'valid_date':          (python datetime object) date of validity

            'latitudes':           (ndarray) 2d latitudes  of data (conditionnal on latlon = True)

            'longitudes':          (ndarray) 2d longitudes of data (conditionnal on latlon = True)
        }

    Example:

           >>> #read odim H5 file
           >>> import os, inspect
           >>> import domutils.radar_tools as radar_tools
           >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
           >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
           >>> out_dict = radar_tools.read_h5_composite(parentdir + '/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311630.h5')
           >>> h5_reflectivity        = out_dict['reflectivity']
           >>> h5_total_quality_index = out_dict['total_quality_index']
           >>> h5_valid_date          = out_dict['valid_date']
           >>> print(h5_reflectivity.shape)
           (2882, 2032)
           >>> print(h5_valid_date)
           2019-10-31 16:30:00+00:00


    """
    import os, inspect
    import datetime
    import warnings
    import pickle
    import time
    import numpy as np
    import h5py

    #checks that filename was provided and is valid
    if odim_file is None :
        raise ValueError('odim_file must be provided')
    else :
        if not os.path.isfile(odim_file) :
            #no file present print warning and return None
            warnings.warn('odim_file: ' + odim_file + ' does not exist')
            if verbose >= 1 :
                print('read_h5_composite: non existent file, returning None')
            return None

    if latlon_file is None :
        #reference standard file which contains RPN domain for composite
        #Should composites one day be generated on a different grid, other files should be added here
        # and use the latlon_file keyword
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        #move two dirs up
        parentdir  = os.path.dirname(currentdir) 
        parentdir2 = os.path.dirname(parentdir) 
        latlon_file = parentdir2 + '/test_data/radar_continental_2.5km_2882x2032.pickle'
        if not os.path.isfile(latlon_file) :
            #no file present print warning and return None
            raise ValueError(  'The file containing latlon information for the Odim H5 grid:  '                         + os.linesep 
                             + latlon_file                                                                              + os.linesep
                             + 'is not available.'                                                                      + os.linesep
                             + 'Please indicate an alternative file with the *latlon_file* keyword or download the'     + os.linesep
                             + 'test data (instructions in the *contribute* section of https://domutils.readthedocs.io)'+ os.linesep
                             + 'to get the 2882x2032 file used for North-American domain used at ECCC.')

    #read latitudes and longitudes if desired
    if latlon :
        ##old way from a standard file
        #ll_dict = fst_tools.getData(fileName=latlon_file, varName='MSKC', latlon=True)

        ##code to make pickle file  --> actually takes longer
        #pickleDict = {'lat':ll_dict['lat'], 'lon':ll_dict['lon']}
        #pickle.dump( pickleDict, open( "/home/ords/mrd/rpndat/dja001/shared_stuff/files/radar_continental_2.5km_2882x2032.pickle", "wb" ) )

        with open(latlon_file, "rb") as pfile:
            ll_dict = pickle.load(pfile)

        latitudes  = ll_dict['lat']
        longitudes = ll_dict['lon']
    else :
        latitudes  = None
        longitudes = None

    #which reflectivity entry do we want to read
    #   the b is for Byte strings which is what we find in H5 attributes
    if qced :
        wanted_quantity=b'DBZH'
    else:
        wanted_quantity=b'TH'

    if verbose >= 1 :
        print('read_h5_composite: reading: ' + str(wanted_quantity) +' from: ' + odim_file)

    h5_obj = h5py.File(odim_file, 'r')

    #look for name of dataset to read ; there should be one and only one dataset in a composite file
    full_list = list(h5_obj.keys())
    dataset_name = None
    for item in full_list :
        if item.startswith('dataset') :
            if dataset_name is not None :
                raise RuntimeError('More than one datasets found in odim file')
            else : 
                #retrieve name of dataset to read later
                dataset_name = item
                #retrieve date of measurement
                dataset_what_dict = dict(h5_obj[dataset_name]['what'].attrs)
                start_date = dataset_what_dict['startdate']
                start_time = dataset_what_dict['starttime']
                
    if dataset_name is None :
        raise RuntimeError('No datasets found in odim file')

    #object for the dataset we are interested in
    dset = h5_obj[dataset_name]

    #go fish for which 'data' entries contains the variable we are interested in then get data values, metadata and associated quality index
    data_list = list(dset)
    for item in data_list :
        if item.startswith('data') :
            #check attributes for quantity being represented
            attrs_dict = dict(dset[item]['what'].attrs)
            if attrs_dict['quantity'] == wanted_quantity :
                #we have the quantity we were looking for
                ref_gain     = attrs_dict['gain']
                ref_no_data  = attrs_dict['nodata']
                ref_offset   = attrs_dict['offset']
                ref_undetect = attrs_dict['undetect']
                #read byte data for reflectivity
                ref_byte = np.array(dset[item]['data'])

                #go and find which quality datasets contains total quality
                quality_list = list(dset[item])
                for qitem in quality_list :
                    if qitem.startswith('quality') :
                        qattrs_how_dict = dict(dset[item][qitem]['how'].attrs)
                        ##for later reference, the different quality indexes take the following values:
                        #b'fi.fmi.ropo.detector.classification' stat_filt
                        #b'se.smhi.detector.beamblockage'       block_percent
                        #b'pl.imgw.radvolqc.att'                attenuation
                        #b'pl.imgw.radvolqc.broad'              broadening
                        #b'se.smhi.composite.distance.radar'    distance
                        #b'se.smhi.composite.height.radar'      tot_qi       
                        #b'pl.imgw.quality.qi_total'            hit_acc_clut
                        #b'ca.mcgill.qc.depolarization_ratio'   mcgill depolarization ratio
                        #b'nl.knmi.scansun'                     ??sun scan detection??
                        if qattrs_how_dict['task'] == b'pl.imgw.quality.qi_total' :
                            qattrs_what_dict = dict(dset[item][qitem]['what'].attrs)
                            tot_qi_gain   = qattrs_what_dict['gain']
                            tot_qi_offset = qattrs_what_dict['offset']
                            
                            tot_qi_byte = np.array(dset[item][qitem]['data'])

    #we are done reading data
    h5_obj.close()

    #make datestamp for output
    yyyy = int(start_date[0:4])
    mo   = int(start_date[4:6])
    dd   = int(start_date[6:8])
    hh   = int(start_time[0:2])
    mi   = int(start_time[2:4])
    ss   = int(start_time[4:6])
    valid_date = datetime.datetime(yyyy, mo, dd, hh, mi, ss, tzinfo=datetime.timezone.utc)

    #make reflectivity from Byte data
    reflectivity = ref_byte * ref_gain + ref_offset
    #assign no_data
    reflectivity = np.where(ref_byte == ref_no_data, no_data, reflectivity)
    #assign undetect
    reflectivity = np.where(ref_byte == ref_undetect, undetect, reflectivity)
    #rotate for agreement with latlon
    reflectivity = np.rot90(reflectivity,k=3)

    #make quality index from Byte data
    total_quality_index = tot_qi_byte * tot_qi_gain + tot_qi_offset
    #rotate for agreement with latlon
    total_quality_index = np.rot90(total_quality_index,k=3)
    
    #constructuct output dictionary
    out_dict = {'reflectivity':        reflectivity,
                'total_quality_index': total_quality_index,
                'valid_date':          valid_date}
    if latlon : 
        #check that dimension of latlon is the same as that of data
        if latitudes.shape != reflectivity.shape :
            raise ValueError('Shape of latitudes not the same as that of reflectivity. Something is going wrong.')
        out_dict['latitudes']   = latitudes
        out_dict['longitudes']  = longitudes

    #that's it
    return out_dict
           

if __name__ == "__main__":
    #to run tests, go in domutils and run 
    # python radar_tools/read_h5_composite.py
    import doctest
    doctest.testmod()
