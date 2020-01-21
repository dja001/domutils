from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping

def readFstComposite(fstFile:    str=None, 
                     latlon:     Optional[bool] = False, 
                     noData:     Optional[float]= -9999.,
                     undetect:   Optional[float]= -3333.,
                     verbose:    Optional[int]  = 0  ) :

    """ Read reflectivity from CMC *standard* files
        

    Validity date is obtained via the *datev* attribute of the entry in the standard file being 
    read.
    Quality index is set to 1 wherever data is not missing



    Args:
        fstFile:         /path/to/fst/composite.std .stnd .fst or no 'extention'
        latlon:           When true, will output latitudes and longitudes 
        noData:           Value that will be assigned to missing values 
        undetect:         Value that will be assigned to valid measurement of no precipitation

    Returns:
        None:            If no or invalid file present

        or 

        { 
            'reflectivity':       (ndarray) 2D reflectivity

            'totalQualityIndex':  (ndarray) 2D quality index

            'validDate':          (python datetime object) date of validity

            'latitudes':          (ndarray) 2d latitudes  of data (conditionnal on latlon = True)

            'longitudes':         (ndarray) 2d longitudes of data (conditionnal on latlon = True)
        }

    Example:

           >>> #read fst file
           >>> import os, inspect
           >>> import domutils.radar_tools as radar_tools
           >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
           >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
           >>> outDict = radar_tools.readFstComposite(parentdir + '/test_data/std_radar_mosaics/2019103116_30ref_4.0km.stnd')
           >>> reflectivity      = outDict['reflectivity']         
           >>> totalQualityIndex = outDict['totalQualityIndex']    
           >>> validDate         = outDict['validDate']            
           >>> print(reflectivity.shape)
           (1650, 1500)
           >>> print(validDate)
           2019-10-31 16:30:00+00:00


    """
    import os
    import datetime
    import warnings
    import time
    import numpy as np
    from rpnpy.rpndate import RPNDate
    #import fst_tools from parent module
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import domcmc.fst_tools as fst_tools


    #checks that filename was provided and is valid
    if fstFile is None :
        raise ValueError('fstFile must be provided')
    else :
        if not os.path.isfile(fstFile) :
            #no file present print warning and return None
            warnings.warn('fstFile: '+fstFile+' does not exist')
            if verbose >= 1 :
                print('readFstComposite: non existent file, returning None')
            return None

    varList = ['RDBR', 'L1']
    #attempt to read to following variables stop when one is found
    for thisVar in varList:
        fstDict = fst_tools.getData(fileName=fstFile, 
                                    varName=thisVar, 
                                    latlon=latlon)
        if fstDict is not None:
            break
    #nothing was found
    if fstDict is None:
        if verbose >= 1 :
            print('readFstComposite: did not find reflectivity in file; returning None')
        return None
    reflectivity = fstDict['values']

    #missing and undetect depend on how data was encoded in fst file, this is very annoying...
    if thisVar == 'RDBR':
        missingFst = -999.
        undetectFst = -99.
    if thisVar == 'L1':
        missingFst = -10.
        undetectFst = 0.

    #make datestamp for output
    datev = fstDict['meta']['datev']
    dateObj = RPNDate(datev)
    validDate = dateObj.toDateTime()

    #mark missing data to user defined noData value
    missingPts = np.isclose(reflectivity, missingFst ).nonzero()
    if missingPts[0].size > 0:
        reflectivity[missingPts] = noData

    #construct a fake quality index = 1 wherever we have data or undetect
    totalQualityIndex = np.ones_like(reflectivity)
    if missingPts[0].size > 0:
        totalQualityIndex[missingPts] = 0.

    #mark undetect to user defined undetect
    undetectPts = np.isclose(reflectivity, undetectFst ).nonzero()
    if undetectPts[0].size > 0:
        reflectivity[undetectPts] = undetect

    #constructuct output dictionary
    outDict = {'reflectivity':       reflectivity, 
               'totalQualityIndex':  totalQualityIndex,
               'validDate':          validDate}
    if latlon : 
        outDict['latitudes']  = fstDict['lat']
        outDict['longitudes'] = fstDict['lon']

    return outDict
           
