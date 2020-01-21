from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def getInstantaneous(validDate:       Optional[Any]   = None, 
                     dataPath:        Optional[str]   = None,
                     dataRecipe:      Optional[str]   = None,
                     desiredQuantity: Optional[str]   = None,
                     medianFilt:      Optional[int]   = None,
                     coefA:           Optional[float] = None, 
                     coefB:           Optional[float] = None,
                     QCed:            Optional[bool]  = True,
                     missing:         Optional[float] = -9999.,
                     latlon:          Optional[bool]  = False,
                     destLon:         Optional[Any]   = None,
                     destLat:         Optional[Any]   = None,
                     average:         Optional[bool]  = False,
                     nearestTime:     Optional[float] = None,
                     smoothRadius:    Optional[float] = None,
                     verbose:         Optional[int]   = 0     ):
    """ Get instantaneous precipitation from various sources

    Provides one interface 
    for:
        - support of Odim h5 composites and URP composites in the standard format
        - output to an arbitrary output grid
        - Consistent median filter on precip observations and the accompanying quality index
        - Various types of averaging 
        - Find the nearest time where observations are available


    The file extension present in *dataRecipe* determines the file type of the source data
    Files having no extension are assumed to be in the 'standard' file format

    Args:

        validDate:       datetime object with the validity date of the precip field
        dataPath:        path to directory where data is expected
        dataRecipe:      datetime code for constructing the file name  eg: /%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
                         the filename will be obtained with  dataPath + validDate.strftime(dataRecipe)
        desiredQuantity: What quantity is desired in output dictionary
                         *precipRate* in [mm/h] and *reflectivity* in [dBZ]
                         are supported
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
        nearestTime:     If set, rewind time until a match is found to an integer number of *nearestTime*
                         For example, with nearestTime=10, time will be rewinded to the nearest integer of 10 minutes
        smoothRadius:    Use the smoothing radius method to interpolate data, faster (see geo_tools documentation)
        verbose:         Set >=1 to print info on execution steps

    Returns:

        None             If no file matching the desired time is found

        or

        {

        'reflectivity'          2D reflectivity on destination grid (if requested)

        'precipRate'            2D reflectivity on destination grid (if requested)

        'totalQualityIndex'     Quality index of data with 1 = best and 0 = worse

        'validDate'             Actual validity date of data 

        'latitudes'             If latlon=True

        'longitudes'            If latlon=True

        }



    """

    import os
    import datetime
    import copy
    import numpy as np
    from . import readH5Composite
    from . import readFstComposite
    from . import exponentialZR
    from . import median_filter
    #import geo_tools from parent module
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import domutils.geo_tools as geo_tools


    #defaut time is now
    if validDate is None:
        validDate = datetime.datetime()

    if verbose >= 1 :
        print('getInstantaneous, getting data for: ',validDate)

    #default coeficients for Z-R
    if coefA is None:
        coefA = 300
    if coefB is None:
        coefB = 1.4

    #default data path and recipe point to operational h5 outputs
    if dataPath is None:
        dataPath = '/space/hall2/sitestore/eccc/cmod/prod/hubs/radar/BALTRAD/Outcoming/Composites'
    if dataRecipe is None:
        dataRecipe = '/%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'

    #defaut value for desired quantity
    if desiredQuantity is None:
        desiredQuantity = 'reflectivity' 
    elif desiredQuantity == 'reflectivity':
        pass
    elif desiredQuantity == 'precipRate':
        pass
    else:
        raise ValueError('Wrong value in desiredQuantity ')

    #define settings if interpolation to a destination grid is needed
    interpolate=False
    requirePrecipRate = False
    if destLon is not None and destLat is not None:
        interpolate=True
        latlon=True

        #if any kind of averaging is to be done we need precipitation rates
        if average or smoothRadius is not None:
            requirePrecipRate = True


    #
    #
    #rewind clock if nearest time is required
    thisTime = copy.deepcopy(validDate)
    #rewind time if necessary 
    if nearestTime is not None:
        try : 
            minutes = thisTime.minute
        except :
            raise ValueError('Could get minute from datetime object *validDate*')

        for tt in np.arange(0, np.float(nearestTime)):
            thisTime = validDate - datetime.timedelta(minutes=tt)
            minutes = thisTime.minute
            remainder = np.mod(minutes,nearestTime)
            if np.isclose(remainder, 0.):
                break


    #
    #
    #make filename from recipe
    try : 
        thisFileName = thisTime.strftime(dataRecipe)
    except :
        raise ValueError('Could not build filename from datetime object')
    #complete filename of data file to read
    dataFile = dataPath + thisFileName


    #
    #
    #read data based on extension
    name, ext = os.path.splitext(dataRecipe)
    if ext == '.h5':
        #
        #
        #ODIM H5 format



        outDict = readH5Composite(dataFile, 
                                  QCed=QCed,
                                  latlon=latlon,
                                  verbose=verbose)
    elif (ext == '.std'  or 
          ext == '.stnd'  or
          ext == '.fst'   or
          ext == '') :

        #
        #
        #CMC *standard* format
        outDict = readFstComposite(dataFile, 
                                   latlon=latlon,
                                   verbose=verbose)

    else:
        raise ValueError('Filetype: '+ext+' not yet supported')

    #return None if nothing was returned by reader
    if outDict is None:
        return None


    #
    #
    #perform conversion if necessary
    if desiredQuantity == 'reflectivity' :
        if 'reflectivity' not in outDict:
            #conversion from R to dBZ
            try: 
                outDict['reflectivity'] = exponentialZR(outDict['precipRate'], 
                                                        coefA=coefA, coefB=coefB, 
                                                        RtodBZ=True)
            except:
                raise ValueError('Could not convert precip rate to reflectivity')

    if desiredQuantity == 'precipRate' or requirePrecipRate :
        if 'precipRate' not in outDict:
            #conversion from R to dBZ
            try: 
                outDict['precipRate'] = exponentialZR(outDict['reflectivity'], 
                                                        coefA=coefA, coefB=coefB, 
                                                        dBZtoR=True)
            except:
                raise ValueError('Could not convert precip rate to reflectivity')


    #
    #
    #remove speckle with median filter if desired
    if medianFilt is not None:
        #speckle filter will be applied from precipRate or reflectivity
        #the same pixel selection is applied to quality indexes 

        if verbose >= 1 :
            print('getInstantaneous, applying median filter')

        if 'reflectivity' in outDict:
            medianInds = median_filter.getInds(  outDict['reflectivity'],  window=medianFilt)
            outDict['reflectivity'] = median_filter.applyInds(outDict['reflectivity'], medianInds)
            if 'precipRate' in outDict:
                outDict['precipRate'] = median_filter.applyInds(outDict['precipRate'], medianInds)

        elif 'precipRate' in outDict:
             medianInds = median_filter.getInds(  outDict['precipRate'], window=medianFilt)
             filteredPR = median_filter.applyInds(outDict['precipRate'], medianInds)
             outDict['precipRate']        = filteredPR
        else:
            raise ValueError('One of reflectivity or precipRate must be present for filtering')

        #quality index should always be in dict
        outDict['totalQualityIndex'] = median_filter.applyInds(outDict['totalQualityIndex'], medianInds)


    #
    #
    #perform interpolation if necessary
    if interpolate:

        if verbose >= 1 :
            print('getInstantaneous, interpolating to destination grid')

        #projection from one grid to another
        projObj = geo_tools.projInds(srcLon=outDict['longitudes'], srcLat=outDict['latitudes'],
                                     destLon=destLon, destLat=destLat,
                                     average=average, smoothRadius=smoothRadius,
                                     missing=missing)
        interpolatedPR = None
        interpolatedREF = None
        if average or smoothRadius is not None:
            #interpolation involving some averaging
            interpolatedPR = projObj.project_data(outDict['precipRate'],        weights=outDict['totalQualityIndex'])
            interpolatedQI = projObj.project_data(outDict['totalQualityIndex'], weights=outDict['totalQualityIndex'])
            #if reflectivity is present get it from interpolated precip Rate
            if 'reflectivity' in outDict:
                interpolatedREF = exponentialZR(interpolatedPR, 
                                                coefA=coefA, coefB=coefB, 
                                                RtodBZ=True)
        else :
            #interpolation by nearest neighbor
            interpolatedQI = projObj.project_data(outDict['totalQualityIndex'])
            if 'precipRate' in outDict:
                interpolatedPR =  projObj.project_data(outDict['precipRate'])
            if 'reflectivity' in outDict:
                interpolatedREF = projObj.project_data(outDict['reflectivity'])

        #update outdict
        outDict['totalQualityIndex'] = interpolatedQI
        outDict['latitudes']  = destLat
        outDict['longitudes'] = destLon
        if interpolatedPR is not None: 
            outDict['precipRate'] = interpolatedPR
        if interpolatedREF is not None: 
            outDict['reflectivity'] = interpolatedREF

        if verbose >= 1 :
            print('getInstantaneous, interpolation done')




    return outDict



    def main():
        pass

    if __name__ == "__main__":
        main()
