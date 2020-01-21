from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def _findNearest(sourceLon:  Any,
                 sourceLat:  Any,
                 destLon:    Any=None,
                 destLat:    Any=None,
                 extendX:    Optional[bool]=True,
                 extendY:    Optional[bool]=True,
                 missing:    Optional[Any]=-9999.,
                 smoothRadius: Optional[Any]=None,
                 sourceCrs:  Optional[Any]=None,
                 destCrs:    Optional[Any]=None):
    """ Find indices to perform nearest neighbour interpolation.

        This function returns the indices of the nearest points in a destination grid characterized by 
        destLon and destLat to each point in a source grid characterized by sourceLon and sourceLat.

        It uses the cKDTree routine from the scipy.spatial module.

        If the destination grid is larger than the source grid, it is desirable to mark the uncovered 
        area in the new grid with missing values. To do so, set the extendX and the extendY keywords 
        to True. 
        

        Args:
            sourceLon:  (array like) longitude of source grid on which the data initially is
            sourceLat:  (array like) latitude of source grid on which the data initially is
            destLon:    (array like) longitude of destination grid
            destLat:    (array like) latitude  of destination
            extendX:    (Boolean) If True, the source grid is extended in the X direction
                        (longitudes) to mark the domain limits
            extendY:    (Boolean) If True, the source grid is extended in the y direction
                        (latitudes) to mark the domain limits            
            missing:    Value of the missing data in projInds
            smoothRadius: (number)   When specified build the kdTree only, it will be used in "project_data"
            sourceCrs:  If provided, this projection is used to convert input data to xyz 
            destCrs:    If provided, this projection is used to convert output data to xyz 

        Returns:
            indices:    vector of the same size as the destination grid containing the corresponding indices in
                        the source grid.
            or
            kdtree:     the kdtree of the source grid if the smoothRadius keyword is used
                        

    """

    import numpy as np
    import scipy.spatial
    import cartopy.crs as ccrs

    from .lat_lon_extend   import lat_lon_extend


    #insure numpy arrays
    source_xx=np.asarray(sourceLon)
    source_yy=np.asarray(sourceLat)
    dest_xx=np.asarray(destLon)
    dest_yy=np.asarray(destLat)
    origShape = source_xx.shape
    if source_xx.ndim == 2:
        #extension requires 2D fields
        [nx,ny]   = source_xx.shape
        
        #extend lat/lon of data to handle differences in domain coverage if required by extendX and/or extendY keywords
        if extendX:
            nx += 2
            extended_lon=np.zeros([nx,ny])
            extended_lat=np.zeros([nx,ny])
            extended_lon[1:-1,:] = source_xx
            extended_lat[1:-1,:] = source_yy
            extended_lon[0,:],extended_lat[0,:]=lat_lon_extend(extended_lon[2,:],extended_lat[2,:],extended_lon[1,:],extended_lat[1,:])
            extended_lon[-1,:], extended_lat[-1,:] = lat_lon_extend(extended_lon[-3,:],extended_lat[-3,:],extended_lon[-2,:],extended_lat[-2,:])
            source_xx=extended_lon
            source_yy=extended_lat
        
        if extendY:
            ny += 2
            extended_lon=np.zeros([nx,ny])
            extended_lat=np.zeros([nx,ny])
            extended_lon[:,1:-1] = source_xx
            extended_lat[:,1:-1] = source_yy
            extended_lon[:,0], extended_lat[:,0] = lat_lon_extend(extended_lon[:,2],extended_lat[:,2],extended_lon[:,1],extended_lat[:,1])
            extended_lon[:,-1], extended_lat[:,-1] = lat_lon_extend(extended_lon[:,-3],extended_lat[:,-3],extended_lon[:,-2],extended_lat[:,-2])
            source_xx=extended_lon
            source_yy=extended_lat
    else:
        if extendX or extendY:
            raise ValueError('extension requires 2D fields')
    
    #everything to xyz coords - both source and destination
    proj_ll = ccrs.Geodetic()
    geo_cent = proj_ll.as_geocentric()
    
    #xyz of source grid 
    if sourceCrs is None:
        source_xyz = geo_cent.transform_points(proj_ll,
                                           source_xx.flatten(),
                                           source_yy.flatten())
    else: 
        source_xyz = geo_cent.transform_points(sourceCrs,
                                           source_xx.flatten(),
                                           source_yy.flatten())

    #xyz of destination grid
    if destCrs is None:
        dest_xyz = geo_cent.transform_points(proj_ll,
                                           dest_xx.flatten(),
                                           dest_yy.flatten())
    else: 
        dest_xyz = geo_cent.transform_points(destCrs,
                                           dest_xx.flatten(),
                                           dest_yy.flatten())


    #indices for nearest neighbor of each pt in image grid to data grid
    kdtree = scipy.spatial.cKDTree(source_xyz, balanced_tree=False)


    if smoothRadius is not None :
        #for smooth radius, finding nearest pts is done within
        # the method 'project_data'
        return kdtree, dest_xyz


    #When smoothRadius is not used, find nearest neighbors to destination grid.

    #search neighbors using the tree
    _, indices = kdtree.query(dest_xyz, k=1)

    #from flat indices to 2D indices
    row_aug, col_aug = np.unravel_index(indices, (nx,ny) )

    #flag pts that are inside domain
    in_bool=np.full_like(row_aug, True, dtype='bool')
    if extendX:
        top    = (row_aug != 0)
        bottom = (row_aug != nx-1)
        top_bottom = np.logical_and(top, bottom)
        in_bool=np.logical_and(in_bool, top_bottom)
    
    if extendY:
        left   = (col_aug != 0)
        right  = (col_aug != ny-1)
        left_right = np.logical_and(left, right)
        in_bool=np.logical_and(in_bool, left_right)
    
    #indexes of pts inside domain
    is_inside = np.asarray( in_bool ).nonzero()
    
    #adjust indexes so that they represent non-extended   ie same shape as data lat/lon grid
    if extendX: row_aug -= 1
    if extendY: col_aug -= 1

    #proj_ind is the final result
    proj_ind = np.full_like(row_aug,missing)
    #points inside source domain have non missing values
    if is_inside[0].size != 0:
        proj_ind[is_inside] = np.ravel_multi_index([row_aug[is_inside],col_aug[is_inside]], origShape)
    
    return proj_ind

