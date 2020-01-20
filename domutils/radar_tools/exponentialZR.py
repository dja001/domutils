from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def exponentialZR(data:        Any, 
                  coefA:       Optional[float]=None, 
                  coefB:       Optional[float]=None,
                  dBZtoR:      Optional[bool]=False, 
                  RtodBZ:      Optional[bool]=False, 
                  missing:     Optional[float]=-9999., 
                  undetect:    Optional[float]=-3333.):

    """ Conversion between dBZ and precip rate (R) using exponential Z-R

    The relation being used is
    Z = aR^b

    When no coefficients are provided, use WSR-88D Z-R 
    coefficients.
             a=300, b=1.4

    Use      a=200, b=1.6  for original Marshall-Palmer
        


    To get dBZ from R we have:

    dBZ = 10*log10(Z) = 10*log10(a) + 10*b*log10(R)

    dBZ =                   U       + V   *log10(R)



    To get R from dBZ:

    R = 10^(dBZ/(10*b)) / 10^(log10(a)/b)

    R = 10^(dBZ/W) / X
            
    Args:
       data:    (array-Like) data to be converted
       coefA:   Coefficient *a* in Z = aR^b
       coefB:   Coefficient *b* in Z = aR^b   
       dBZtoR:  When True  input data is assumed in dBZ and output is R in mm/h
       RtodBZ:  When True, input data is assumed in mm/h and is converted to dBZ
                One of dBZtoR or RtodBZ must be set to True
    Returns:
       A numpy array of the size of input data containing the converted data. 
    
    Example:
        >>> import domutils.radar_tools as radar_tools
        >>> import numpy as np
        >>> #reflectivity values
        >>> ref_dBZ  = np.array([-10., -5., 0., 5, 10, 20, 30, 40, 50, 60])
        >>> #convert to precip rate im mm/h
        >>> rate_mmh = radar_tools.exponentialZR(ref_dBZ, dBZtoR=True)
        >>> with np.printoptions(precision=3, suppress=True):
        ...     print(rate_mmh)
        [  0.003   0.007   0.017   0.039   0.088   0.456   2.363  12.24   63.395
         328.354]
        >>>
        >>> #convert back to dBZ
        >>> recovered_dbz= radar_tools.exponentialZR(rate_mmh, RtodBZ=True)
        >>> print(recovered_dbz)
        [-10.  -5.   0.   5.  10.  20.  30.  40.  50.  60.]

        
    """

    import numpy as np

    #defaults
    if coefA is None:
        coefA = 300

    if coefB is None:
        coefB = 1.4



    if dBZtoR:
        #conversion from dBZ to R

        W = 10.*coefB
        X = 10.**(np.log10(coefA)/coefB)

        output = np.full_like(data, missing)
        undetectPts = np.abs(data - undetect) < 1e-3
        #where data is not missing or undetect, convert to dBZ
        validPts = np.logical_and( (np.abs(data - missing) > 1e-3) , np.logical_not(undetectPts) ).nonzero()
        if validPts[0].size > 0 :
            output[validPts] = 10.**(data[validPts] / W) * (1./X)

        #where data is undetect, precip rate is 0.
        output = np.where(undetectPts, 0., output)

    elif RtodBZ : 

        U = 10.*np.log10(coefA)
        V = 10.*coefB

        #conversion from R to dBZ
        output = np.full_like(data, missing)
        undetectPts = np.abs(data - 0.) < 1e-3  #min precip id 0.001 mm/h and below 
        #where data is not missing or undetect, convert to R
        validPts = np.logical_and( (np.abs(data - missing) > 1e-3) , np.logical_not(undetectPts) ).nonzero()
        if validPts[0].size > 0 :
            output[validPts] = U + V*np.log10(data[validPts])

        #where data is undetect, precip rate is 0.
        output = np.where(undetectPts, undetect, output)
    else:
        raise ValueError('One of dBZtoR or RtodBZ must be set to True')

        
    return output 

