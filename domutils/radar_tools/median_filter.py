def getInds(data, window=None ):
    """ Indices for speckle filtering through median filter

    Applying filter is just a matter of
    data.ravel()[indices] = filtered

    Data points at the edge are repeated for filtering near the domain border

    Returning indices allows to apply the same median filtering on the quality
    index as on the precipitation data itself.


    Args:
        data:   source data, should be 2D ndarray

        window: Size of boxcar window for median window default is 3x3
                Should be an odd integer
        
    Returns:
        indices for applying speckle filter data[indices] = filtered

    Example:

        >>> import numpy as np
        >>> import domutils.radar_tools as radar_tools
        >>> data = np.array([[1,2,3,0],
        ...                  [8,9,4,0],
        ...                  [7,6,5,0]])
        >>> inds = radar_tools.median_filter.getInds(data)
        >>> print(inds)
        [[ 1  2  1  7]
         [ 8 10  2 11]
         [ 8  9 10 11]]
        >>> #median filtered data on a 3x3 window
        >>> print(data.ravel()[inds])
        [[2 3 2 0]
         [7 5 3 0]
         [7 6 5 0]]


    """

    import numpy as np

    #default window is 3x3
    if window is None:
        window = 3
    else:
        window = int(window)

    #source data should be 2d and at least 3x3
    dd = np.asarray(data)
    ddFlat = dd.ravel()

    halfWindow = (window -1)/2
    windowSquare = window**2
    midWindow = np.floor(windowSquare/2).astype('int64')

    # [ny, ny, nMedianPts]  matrix to store flat indices of pts considered for the median
    # at each (x_i,y_i) 
    flatInds  = np.zeros((dd.shape[0],dd.shape[1],windowSquare), dtype='int64')
    #Data values corresponding to flatInds
    remappedData = np.zeros((dd.shape[0],dd.shape[1],windowSquare))

    #basis for construction of median indices
    rowInds, colInds = np.meshgrid(np.arange(dd.shape[0]),np.arange(dd.shape[1]),indexing='ij')
    #fill sorting matrix for each pixel of the median filterig
    zz=0
    for xx in np.arange(-halfWindow,halfWindow+1,1, dtype='int64'):
        for yy in np.arange(-halfWindow,halfWindow+1,1, dtype='int64'):
            inds =(rowInds+xx,colInds+yy)
            flatInds[:,:,zz]  = np.ravel_multi_index(inds, dd.shape, mode='clip')
            #print('x',xx,'y',yy)
            #print(flatInds[:,:,zz])
            remappedData[:,:,zz] = ddFlat[flatInds[:,:,zz]] 
            zz += 1
    #indez of sorted data along the 3rd dimension
    sortedInds = np.argsort(remappedData, axis=2)
    #z dimension of index of median pt
    medianInds = sortedInds[:,:,midWindow]
    #1D index for median filtering
    mappingInds = flatInds[rowInds,colInds,medianInds]

    return mappingInds


def applyInds(data, inds):
    """Apply inds computed from speckle_inds

    This is just a shortcut to a 1 line piece 
    of code:

    data.ravel()[indices] = filtered bla

    """

    dataFlat = data.ravel()

    return dataFlat[inds]

