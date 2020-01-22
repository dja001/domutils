
from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def lat_lon_range_az( lon1_in:      Any, 
                      lat1_in:      Any,
                      range_in:     Any,
                      azimuth_in:   Any,
                      crs:          Optional[Any]=None, 
                      earth_radius: Optional[Any]=None ):

    """ Computes lat/lon of a point at a given range and azimuth (meteorological angles)

       Given points (pt1) on a sphere, this function returns a second point (pt2) 
       at a given range and azimuth from pt1.
       Same altitude is assumed. 
       Range is a distance following curvature of the earth 

       The diagram below hopefully make the purpose of this function clearer::
           #                                              #
           #       N                                      #
           #                                              #
           #       ^  -                                   #
           #       |      -                               #
           #       |        -    azimuth (deg)            #
           #       |         -                            #
           #       |          -                           #
           #      pt1         -  E                        #
           #        \         -                           #
           #  range  \       -                            #
           #          \     -                             #
           #           \  -                               #
           #           pt2    output is lat lon of pt2    #


       Internally, two rotations on the sphere are conducted
            - 1st rotation shifts pt1 toward the North and is dictated by range
            - 2nd rotation is around point pt1 and is determined by azimuth

       Args:
            lon1_in:      (array like) longitude of point 1
            lat1_in:      (array like) latitude  of point 1
            range_in:     (array like) [km] range (distance) at which pt2 is located from pt1
            azimuth_in:   (array like) [degrees]  direction (meteorological angle) in thich pt2 is located 
            crs:          Instance of Cartopy geoAxes in which pt coordinates are defined 
                          (default is Geodesic for lat/lon specifications)
            earth_radius: (km) radius of the earth (default 6371 km)

       Returns:
            longitude, latitude    (array like) of pt2

       Examples:

           Extend one point.

           >>> import numpy as np
           >>> import domutils.geo_tools as geo_tools
           >>> # coordinates of pt1 
           >>> lat1 = 0.
           >>> lon1 = 0.
           >>> # range and azimuth  
           >>> C = 2.*np.pi*6371.  #circumference of the earth
           >>> range_km = C/8. 
           >>> azimuth_deg = 0.
           >>> # coordinates of extended point
           >>> lon2, lat2 = geo_tools.lat_lon_range_az(lon1,lat1,range_km,azimuth_deg)
           >>> print(lon2, lat2)
           0.0 45.192099833854435
           >>> 
           >>> 
           >>> #also works for inputs in arrays
           >>> lat1        = [[0.,     0],
           ...                [0.,     0]]
           >>> lon1        = [[0.,     0],
           ...                [0.,     0]]
           >>> range_km    = [[C/8.,  C/8.],
           ...                [C/8.,  C/8.]]
           >>> azimuth_deg = [[0.,     90.],
           ...                [-90.,   180]]
           >>> lon2, lat2 = geo_tools.lat_lon_range_az(lon1,lat1,range_km,azimuth_deg)
           >>> print(lon2)
           [[ 0.0000000e+00  4.5000000e+01]
            [-4.5000000e+01  7.0167093e-15]]
           >>> print(lat2)
           [[ 4.51920998e+01  9.05659542e-15]
            [ 9.05659542e-15 -4.51920998e+01]]

           get lat/lon of a circle 50km from a reference point

           >>> #reference point
           >>> lat0 =  37.
           >>> lon0 = -88.
           >>> #prep data, note how only azimuth varies
           >>> azimuths  = np.arange(180, dtype='float')
           >>> ranges  = np.full_like(azimuths, 50.)
           >>> lats    = np.full_like(azimuths, lat0)
           >>> lons    = np.full_like(azimuths, lon0)
           >>> #longitudes and latitudes along the circle
           clons, clats = geo_tools.lat_lon_range_az(lons, lats, rgs, azs)



    """

    import numpy as np
    import cartopy.crs as ccrs
    from .rotation_matrix  import rotation_matrix


    #ensure numpy type
    lon1       = np.array(lon1_in, copy=True)
    orig_shape = lon1.shape
    lat1       = np.array(lat1_in, copy=True)
    range_km   = np.array(range_in, copy=True)
    azimuth    = np.array(azimuth_in, copy=True)

    #all input should have the same shape
    if not ((orig_shape == lat1.shape)     and
            (orig_shape == range_km.shape) and
            (orig_shape == azimuth.shape)):
        raise ValueError('All inputs should have same shape')
    
    #as flat arrays
    lon1     = lon1.ravel()
    lat1     = lat1.ravel()
    range_km = range_km.ravel()
    azimuth  = azimuth.ravel()  

    #tmp storage vectors for xyz
    xyz_arr = np.zeros([lon1.size,3])

    #convert lat_lon to xyz
    if crs is None:
        crs = ccrs.Geodetic()
    geo_cent = crs.as_geocentric()
    xyz_pt1 = geo_cent.transform_points(crs, lon1, lat1)

    #xyz of north pole
    [xyz_hohoho] = geo_cent.transform_points(crs, np.array([0.]), np.array([90.]))

    #radius of the earth
    if earth_radius is None:
        earth_radius = 6371.    #[km]

    #get pt2 for each pt1
    for ind, xyz_v1 in enumerate(xyz_pt1):

        this_range_km = range_km[ind]
        # -1 since rotation matrix does counterclockwise rotation
        # while this routine uses meteorological angles with clockwise rotation
        this_az_r = -1.*np.radians(azimuth[ind])    

        #angle (radians) for 1st rotation
        theta_r = this_range_km/earth_radius
        
        #1st rotation from point 0 towards the north pole 
        axis1 = np.cross(xyz_v1, xyz_hohoho)
        mm1 = rotation_matrix(axis1, theta_r)

        #2nd rotation around vector given by pt1
        mm2 = rotation_matrix(xyz_v1, this_az_r)
            
        #combine the two rotations
        mm3 = np.matmul(mm2,mm1)
        
        #xyz coords of rotated point 
        xyz_v2 = np.matmul(mm3,xyz_v1)
        
        #save results for later conversion to latlon
        xyz_arr[ind,:] = xyz_v2

    #output in lat/lon
    lonlat = crs.transform_points(geo_cent, xyz_arr[:,0], xyz_arr[:,1], xyz_arr[:,2])
    lon2 = np.reshape(lonlat[:,0], orig_shape)
    lat2 = np.reshape(lonlat[:,1], orig_shape)

    return lon2, lat2

