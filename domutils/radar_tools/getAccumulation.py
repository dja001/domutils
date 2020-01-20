from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def getAccumulation(endDate:         Optional[Any]   = None, 
                    duration:        Optional[Any]   = None,            
                    desiredQuantity: Optional[str]   = None,
                    dataPath:        Optional[str]   = None,
                    dataRecipe:      Optional[str]   = None,
                    medianFilt:      Optional[int]   = None,
                    coefA:           Optional[float] = None, 
                    coefB:           Optional[float] = None,
                    QCed:            Optional[bool]  = True,
                    missing:         Optional[float] = -9999.,
                    latlon:          Optional[bool]  = False,
                    destLon:         Optional[Any]   = None,
                    destLat:         Optional[Any]   = None,
                    average:         Optional[bool]  = False,
                    nearest:         Optional[float] = None,
                    smoothRadius:    Optional[float] = None,
                    verbose:         Optional[int]   = 0):

    """Get accumulated precipitation from instantaneous observations

    This is essentially a wrapper around getInstantaneous. 
    Data is read during the accumulation period and accumulated (in linear units of 
    precipitation rates) taking the quality index into account. 
    If interpolation to a different grid is desired, it is performed after the 
    accumulation procedure. 

    If the desired quantity *reflectivity* or *precipRate* is desired, then the
    returned quantity will reflect the average precipitation rate during the accumulation 
    period.

    With an endTime set to 16:00h and duration to 60 (minutes), 
    data from:
        - 15:10h, 15:20h, 15:30h, 15:40h, 15:50h and 16:00h
    will be accumulated 

    Args:

        endDate:         datetime object representing the time (inclusively) at the end of the accumulation period
        duration:        amount of time (minutes) during which precipitation should be accumulated                 
                            
        dataPath:        path to directory where data is expected
        dataRecipe:      datetime code for constructing the file name  eg: /%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
                         the filename will be obtained with  dataPath + validDate.strftime(dataRecipe)
        desiredQuantity: What quantity is desired in output dictionary. 
                         Supported values are: 
                            - *accumulation*  Default option, the amount of water (in mm) 
                            - *avgPrecipRate* For average precipitation rate (in mm/h) during the accumulation period     
                            - *reflectivity*  For the reflectivity (in dBZ) associated with the average precipitation rate
        medianFilt:      If specified, a median filter will be applied on the data being read and the associated
                         quality index. 
                         eg. *medialFilter=3* will apply a median filter over a 3x3 boxcar
                         If unspecified, no filtering is applied
        coefA:           Coefficient *a* in Z = aR^b
        coefB:           Coefficient *b* in Z = aR^b   
        QCed:            Only for Odim H5 composites
                         When True (default), Quality Controlled reflectivity (DBZH) will be returned.
                         When False, raw reflectivity (TH) will be returned.
        missing:         Value that will be assigned to missing data
        latlon:          Return *latitudes* and *longitudes* grid of the data
        destLon:         Longitudes of destination grid. If not provided data is returned on its original grid
        destLat:         Latitudes  of destination grid. If not provided data is returned on its original grid
        average:         Use the averaging method to interpolate data (see geo_tools documentation), this can be slow
        nearest:         If set, rewind time until a match is found to an integer number of *nearest*
                         For example, with nearest=10, time will be rewinded to the nearest integer of 10 minutes
        smoothRadius:    Use the smoothing radius method to interpolate data, faster (see geo_tools documentation)

    Returns:
        None             If no file matching the desired time is found

        or

        {

        'endDate'               End time for accumulation period

        'duration'              Assumulation length (minutes)

        'reflectivity'          2D reflectivity on destination grid (if requested)

        'precipRate'            2D reflectivity on destination grid (if requested)

        'totalQualityIndex'     Quality index of data with 1 = best and 0 = worse


        'latitudes'             If latlon=True

        'longitudes'            If latlon=True

        }



    """

    import os
    import datetime
    import numpy as np
    from .  import getInstantaneous
    from .  import exponentialZR
    #import geo_tools from parent module
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import domutils.geo_tools as geo_tools

    if verbose >= 1 :
        print('getAccumulation starting')

    #define settings if interpolation to a destination grid is needed
    #for better performance, interpolation will be performed only once
    #data has been acucmulated on its original grid
    interpolate=False
    if destLon is not None and destLat is not None:
        interpolate=True
        latlon=True

    #defaut time is now
    if endDate is None:
        endDate = datetime.datetime()

    #defaut duration is 1h
    if duration is None:
        duration = 60.

    #default coeficients for Z-R
    if coefA is None:
        coefA = 300
    if coefB is None:
        coefB = 1.4

    #defaut value for desired quantity
    if desiredQuantity is None:
        desiredQuantity   = 'accumulation' 
    elif desiredQuantity == 'accumulation':
        pass
    elif desiredQuantity == 'avgPrecipRate':
        pass
    elif desiredQuantity == 'reflectivity':
        pass
    else:
        raise ValueError('Wrong value in desiredQuantity ')

    #start filling out output dictionary
    outDict = {'endDate':    endDate, 
               'duration':   duration }


    #time interval between radar observations
    name, ext = os.path.splitext(dataRecipe)
    if ext == '.h5':
        radarDt = 10.
    else:
        raise ValueError('Filetype: '+ext+' not yet supported')
    

    #
    #
    #get list of times during which observations should be accumulated
    mList = np.arange(0, duration, radarDt)
    dateList = [endDate - datetime.timedelta(minutes=thisMin) for thisMin in mList]


    #
    #
    #read data
    #for 1st time
    kk = 0
    thisDate = dateList[kk]
    datDict = getInstantaneous(desiredQuantity='precipRate',
                               validDate=thisDate, 
                               dataPath=dataPath,
                               dataRecipe=dataRecipe,
                               medianFilt=medianFilt,
                               latlon=latlon,
                               verbose=verbose)
    dataShape = datDict['precipRate'].shape
    if latlon is not None:
        origLat = datDict['latitudes']
        origLon = datDict['longitudes']
    #init accumulation arrays
    accumDat = np.full((dataShape[0], dataShape[1], len(dateList)), missing)
    accumQi  = np.zeros((dataShape[0], dataShape[1], len(dateList)))
    #save data
    accumDat[:,:,kk] = datDict['precipRate']
    accumQi[:,:,kk]  = datDict['totalQualityIndex']
    #
    #read rest of data
    for kk, thisDate in enumerate(dateList):
        #we already did the 1st one, skip it
        if kk == 0 :
            continue

        #fill accumulation arrays with data for this time
        datDict = getInstantaneous(desiredQuantity='precipRate',
                                   validDate=thisDate, 
                                   dataPath=dataPath,
                                   dataRecipe=dataRecipe,
                                   medianFilt=medianFilt,
                                   verbose=verbose)
        if datDict is not None:
            accumDat[:,:,kk] = datDict['precipRate']
            accumQi[:,:,kk]  = datDict['totalQualityIndex']


    #
    #
    #average of precipRate is weighted by quality index
    if verbose >= 1 :
        print('getAccumulation, computing average precip rate in accumulation period')
    sumW  = np.sum(accumQi, axis=2)
    goodPts = np.asarray(sumW > 0.).nonzero()
    #
    #average precipRate
    weightedSum = np.sum(accumDat*accumQi, axis=2)
    avgPR = np.full_like(sumW, missing)
    if goodPts[0].size > 0:
        avgPR[goodPts] = weightedSum[goodPts]/sumW[goodPts]
    #
    #compute average quality index
    weightedSum = np.sum(accumQi*accumQi, axis=2)
    avgQi = np.full_like(sumW, missing)
    if goodPts[0].size > 0:
        avgQi[goodPts] = weightedSum[goodPts]/sumW[goodPts]


    #
    #
    #perform interpolation if necessary
    if interpolate:
        if verbose >= 1 :
            print('getAccumulation, interpolating to destination grid')

        #projection from one grid to another
        projObj = geo_tools.projInds(srcLon=origLon,  srcLat=origLat,
                                     destLon=destLon, destLat=destLat,
                                     average=average, smoothRadius=smoothRadius,
                                     missing=missing)
        if average or smoothRadius is not None:
            #interpolation involving some averaging
            interpolatedPR = projObj.project_data(avgPR, weights=avgQi)
            interpolatedQI = projObj.project_data(avgQi, weights=avgQi)
        else :
            #interpolation by nearest neighbor
            interpolatedPR = projObj.project_data(avgPR)
            interpolatedQI = projObj.project_data(avgQi)

        #fill outDict
        outDict['avgPrecipRate']     = interpolatedPR
        outDict['totalQualityIndex'] = interpolatedQI
        outDict['latitudes']         = destLat
        outDict['longitudes']        = destLon
    else:
        #no Interpolation 
        outDict['avgPrecipRate']     = avgPR
        outDict['totalQualityIndex'] = avgQi
        if latlon:
            outDict['latitudes']     = origLat
            outDict['longitudes']    = origLon


    #
    #
    #convert precip rates to other quantities if desired
    if desiredQuantity == 'accumulation':
        if verbose >= 1 :
            print('getAccumulation computing accumulation from avg precip rate')
        # rate (mm/h) * duration time (h) = accumulation (mm)
        #number of hours of accumulation period
        durationHours = duration/60. 
        outDict['accumulation'] = outDict['avgPrecipRate'] * durationHours
    #
    if desiredQuantity == 'reflectivity':
        if verbose >= 1 :
            print('getAccumulation computing reflectivity from avg precip rate')
        outDict['reflectivity'] = exponentialZR(outDict['avgPrecipRate'], 
                                                coefA=coefA, coefB=coefB, 
                                                RtodBZ=True)

    if verbose >= 1 :
        print('getAccumulation done')
    return outDict





