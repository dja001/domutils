def remap_data(data, window=3, mode='clip', return_flat_inds=False):

    """ Puts 2D data into 3D array for any type of window (boxcar) operations

    In compiled code, median filtering and other types of boxcar filtering 
    is performed with nested loops which are very inefficient in Python.

    This function remaps original data of shape M x N
    to a 3D array of shape M x N x W
    with W being the size of the filtering window. 

    At each point i,j, the values along the 3rd dimension are all the data values
    participating in the window averaging.

    Numpy operations can then be leveraged for fast computation of these filters.


    Args:
        data:   source data, should be 2D ndarray

        window: Size of boxcar window default is 3x3
                Should be an odd integer

        mode:   mode argument to *np.ravel_multi_index*
                Use 'clip' (default) to repeat values found at the edge
                use 'wrap' to wrap around
        
    Returns:

        remapped_data:  a M x N x W remapping of the original data

        if return_flat_inds == True, we return the following:

            remapped_data:  a M x N x W remapping of the original data
            row_inds:       a M x N    array containg i index of output array
            col_inds:       a M x N    array containg j index of output array
            flat_inds:      a M x N x W array containg flat indices toinput data


    Example:

        >>> import numpy as np
        >>> import domutils.radar_tools as radar_tools
        >>> data = np.array([[1,2,3,0],
        ...                  [8,9,4,0],
        ...                  [7,6,5,0]])
        >>> remapped_data = radar_tools.median_filter.remap_data(data, window=3, mode='clip')
        >>> #
        >>> #data points in window for point i=0, j=0
        >>> print(remapped_data[0,0,:])
        [1. 1. 2. 1. 1. 2. 8. 8. 9.]
        >>> #
        >>> print(remapped_data[1,0,:])
        [1. 1. 2. 8. 8. 9. 7. 7. 6.]
        >>> #
        >>> #data points in window for point i=1, j=1
        >>> print(remapped_data[1,1,:])
        [1. 2. 3. 8. 9. 4. 7. 6. 5.]
        >>> #
        >>> #sum of data points in boxcar 
        >>> box_sum = np.sum(remapped_data, axis=2)
        >>> print(box_sum)
        [[33. 33. 23. 10.]
         [49. 45. 29. 12.]
         [65. 57. 35. 14.]]
        >>> #
        >>> #boxcar average
        >>> box_avg = np.mean(remapped_data, axis=2)
        >>> print(box_avg)
        [[3.66666667 3.66666667 2.55555556 1.11111111]
         [5.44444444 5.         3.22222222 1.33333333]
         [7.22222222 6.33333333 3.88888889 1.55555556]]
    """

    import numpy as np 

    dd_flat = data.ravel()

    half_window   = (window -1)/2
    window_square = window**2

    # [ny, ny, n_median_pts]  matrix to store flat indices of pts considered for the median
    # at each (x_i,y_i) 
    flat_inds  = np.zeros((data.shape[0],data.shape[1],window_square), dtype='int64')
    #Data values corresponding to flat_inds
    remapped_data = np.zeros((data.shape[0],data.shape[1],window_square))


    #basis for construction of median indices
    row_inds, col_inds = np.meshgrid(np.arange(data.shape[0]),np.arange(data.shape[1]),indexing='ij')
    #fill sorting matrix for each pixel of the median filterig
    zz=0
    for xx in np.arange(-half_window,half_window+1,1, dtype='int64'):
        for yy in np.arange(-half_window,half_window+1,1, dtype='int64'):
            inds =(row_inds+xx,col_inds+yy)
            flat_inds[:,:,zz]  = np.ravel_multi_index(inds, data.shape, mode=mode)
            #print('x',xx,'y',yy)
            #print(flat_inds[:,:,zz])
            remapped_data[:,:,zz] = dd_flat[flat_inds[:,:,zz]]
            zz += 1
    

    if return_flat_inds:
        return remapped_data, row_inds, col_inds, flat_inds
    else:
        return remapped_data



def get_inds(data, window=3):
    """ Indices for speckle filtering through median filter

    Applying filter is just a matter of "data.ravel()[indices] = filtered" 
    which is performed by the function *apply_inds()* below.


    Data points at the edge are repeated for filtering near the domain border

    Returning indices allows to apply the same median filtering on the quality
    index as on the precipitation data itself.


    Args:
        data:   source data, should be 2D ndarray

        window: Size of boxcar window default is 3x3
                Should be an odd integer
        
    Returns:
        indices for applying speckle filter data[indices] = filtered

    Example:

        >>> import numpy as np
        >>> import domutils.radar_tools as radar_tools
        >>> data = np.array([[1,2,3,0],
        ...                  [8,9,4,0],
        ...                  [7,6,5,0]])
        >>> inds = radar_tools.median_filter.get_inds(data)
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

    #source data should be 2d and at least 3x3
    dd = np.asarray(data)

    #mid value of sample for median filtering
    window_square = window**2
    mid_window    = np.floor(window_square/2).astype('int64')

    #3D array where columns are data located in each window
    remapped_data, row_inds, col_inds, flat_inds = remap_data(dd, window=3, mode='clip', return_flat_inds=True)

    #index of sorted data along the 3rd dimension
    sorted_inds = np.argsort(remapped_data, axis=2)
    #z dimension of index of median pt
    median_inds = sorted_inds[:,:,mid_window]
    #1D index for median filtering
    mapping_inds = flat_inds[row_inds,col_inds,median_inds]

    return mapping_inds


def apply_inds(data, inds):
    """Apply inds computed from speckle_inds

    This is just a shortcut to a 1 line piece 
    of code:

    data.ravel()[indices] = filtered bla

    """

    data_flat = data.ravel()

    return data_flat[inds]

if __name__ == '__main__':
        import doctest
        doctest.testmod(verbose = True)
        #doctest.run_docstring_examples(f, globals())
