from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping

def readH5Composite( odimFile:   str=None, 
                     latlon:     Optional[bool] = False, 
                     QCed:       Optional[bool] = True, 
                     noData:     Optional[float]= -9999.,
                     undetect:   Optional[float]= -3333.,
                     latlonFile: Optional[str]= None,
                     verbose:    Optional[int]  = 0  ) :

    """ Read reflectivity and quality index from OdimH5 composite
        
    Odim H5 files are a bit annoying in that datasets and quality index are just numbered
    (data1, data2, ...) and not named following what thay contain. Also, one cannot expect that 
    a dataset named 'quality3' will always contain the same quantity. 
    The result is that one has to loop over each item and check that the contents match what we 
    are looking for. 
    This routine does that as well as converting the Byte data found in H5 files to more tangible
    quantities such as reflectivity in dBZ and quality index between 0. and 1. 
    Special values are also assigned to noData and undetect values.
    UTC time zone is assumed for datestamp in H5 file

    Args:
        odimFile:         /path/to/odim/composite.h5
        latlon:           When true, will output latitudes and longitudes of the odim grid
        QCed:             When true (default), Quality Controlled reflectivity (DBZH) will be returned.
                          When false, raw reflectivity (TH) will be returned.
        noData:           Value that will be assigned to missing values 
        undetect:         Value that will be assigned to valid measurement of no precipitation
        latlonFile:       pickle file containing latlon of domain (only used if latlon=True)

    Returns:
        None:                     If no or invalid file present

        or 

        { 
            'reflectivity':       (ndarray) 2D reflectivity

            'totalQualityIndex':  (ndarray) 2D quality index

            'validDate':          (python datetime object) date of validity

            'latitudes':          (ndarray) 2d latitudes  of data (conditionnal on latlon = True)

            'longitudes':         (ndarray) 2d longitudes of data (conditionnal on latlon = True)
        }

    Example:

           >>> #read odim H5 file
           >>> import os, inspect
           >>> import domutils.radar_tools as radar_tools
           >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
           >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
           >>> outDict = radar_tools.readH5Composite(parentdir + '/test_data/odimh5_radar_composites/2019/10/31/qcomp_201910311630.h5')
           >>> h5reflectivity      = outDict['reflectivity']         
           >>> h5totalQualityIndex = outDict['totalQualityIndex']    
           >>> h5validDate         = outDict['validDate']            
           >>> print(h5reflectivity.shape)
           (2882, 2032)
           >>> print(h5validDate)
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
    if odimFile is None :
        raise ValueError('odimFile must be provided')
    else :
        if not os.path.isfile(odimFile) :
            #no file present print warning and return None
            warnings.warn('odimFile: '+odimFile+' does not exist')
            if verbose >= 1 :
                print('readH5Composite: non existent file, returning None')
            return None

    if latlonFile is None :
        #reference standard file which contains RPN domain for composite
        #Should composites one day be generated on a different grid, other files should be added here
        # and use the latlonFile keyword
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        latlonFile = currentdir + '/radar_continental_2.5km_2882x2032.pickle'

    #read latitudes and longitudes if desired
    if latlon :
        ##old way from a standard file
        #llDict = fst_tools.getData(fileName=latlonFile, varName='MSKC', latlon=True)

        ##code to make pickle file
        #pickleDict = {'lat':llDict['lat'], 'lon':llDict['lon']}
        #pickle.dump( pickleDict, open( "/home/ords/mrd/rpndat/dja001/shared_stuff/files/radar_continental_2.5km_2882x2032.pickle", "wb" ) )

        with open( latlonFile, "rb" ) as pfile:
            llDict = pickle.load(pfile)

        latitudes  = llDict['lat']
        longitudes = llDict['lon']
    else :
        latitudes  = None
        longitudes = None

    #which reflectivity entry do we want to read
    #   the b is for Byte strings which is what we find in H5 attributes
    if QCed : 
        wantedQuantity=b'DBZH'
    else:
        wantedQuantity=b'TH'

    if verbose >= 1 :
        print('readH5Composite: reading: '+str(wantedQuantity)+' from: '+odimFile)

    h5Obj = h5py.File(odimFile, 'r')

    #look for name of dataset to read ; there should be one and only one dataset in a composite file
    fullList = list(h5Obj.keys())
    datasetName = None
    for item in fullList :
        if item.startswith('dataset') :
            if datasetName is not None :
                raise RuntimeError('More than one datasets found in odim file')
            else : 
                #retrieve name of dataset to read later
                datasetName = item
                #retrieve date of measurement
                datasetWhatDict = dict(h5Obj[datasetName]['what'].attrs)
                startDate = datasetWhatDict['startdate']
                startTime = datasetWhatDict['starttime']
                
    if datasetName is None :
        raise RuntimeError('No datasets found in odim file')

    #object for the dataset we are interested in
    dset = h5Obj[datasetName]

    #go fish for which 'data' entries contains the variable we are interested in then get data values, metadata and associated quality index
    dataList = list(dset)
    for item in dataList :
        if item.startswith('data') :
            #check attributes for quantity being represented
            attrsDict = dict(dset[item]['what'].attrs)
            if attrsDict['quantity'] == wantedQuantity :
                #we have the quantity we were looking for
                refGain     = attrsDict['gain']
                refNoData   = attrsDict['nodata']
                refOffset   = attrsDict['offset']
                refUndetect = attrsDict['undetect']
                #read byte data for reflectivity
                refByte = np.array(dset[item]['data'])

                #go and find which quality datasets contains total quality
                qualityList = list(dset[item])
                for qitem in qualityList :
                    if qitem.startswith('quality') :
                        qattrsHowDict = dict(dset[item][qitem]['how'].attrs)
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
                        if qattrsHowDict['task'] == b'pl.imgw.quality.qi_total' :
                            qattrsWhatDict = dict(dset[item][qitem]['what'].attrs)
                            totQiGain = qattrsWhatDict['gain']
                            totQiOffset = qattrsWhatDict['offset']
                            
                            totQiByte = np.array(dset[item][qitem]['data'])

    #we are done reading data
    h5Obj.close()

    #make datestamp for output
    yyyy = int(startDate[0:4])
    mo   = int(startDate[4:6])
    dd   = int(startDate[6:8])
    hh   = int(startTime[0:2])
    mi   = int(startTime[2:4])
    ss   = int(startTime[4:6])
    validDate = datetime.datetime(yyyy, mo, dd, hh, mi, ss, tzinfo=datetime.timezone.utc)

    #make reflectivity from Byte data
    reflectivity = refByte * refGain + refOffset
    #assign noData
    reflectivity = np.where(refByte == refNoData,   noData  , reflectivity)
    #assign undetect
    reflectivity = np.where(refByte == refUndetect, undetect, reflectivity)
    #rotate for agreement with latlon
    reflectivity = np.rot90(reflectivity,k=3)

    #make quality index from Byte data
    totalQualityIndex = totQiByte * totQiGain + totQiOffset
    #rotate for agreement with latlon
    totalQualityIndex = np.rot90(totalQualityIndex,k=3)
    
    #constructuct output dictionary
    outDict = {'reflectivity':       reflectivity, 
               'totalQualityIndex':  totalQualityIndex,
               'validDate':          validDate}
    if latlon : 
        #check that dimension of latlon is the same as that of data
        if latitudes.shape != reflectivity.shape :
            raise ValueError('Shape of latitudes not the same as that of reflectivity. Something is going wrong.')
        outDict['latitudes']         = latitudes
        outDict['longitudes']        = longitudes

    #that's it
    return outDict
           
