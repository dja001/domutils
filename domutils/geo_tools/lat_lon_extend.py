from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def lat_lon_extend(lon1_in:   Any,
                   lat1_in:   Any,
                   lon2_in:   Any,
                   lat2_in:   Any,
                   crs:       Any=None,
                   half_dist: bool=False) :
    """ Extends latitude and longitudes on a sphere

       Given two points (pt1 and pt2) on a sphere, this function returns a third point (pt3) at the 
       same distance and in the same direction as between pt1 and pt2.
       All points are defined with latitudes and longitudes, same altitude is assumed. 

       The diagram below hopefully make the purpose of this function clearer::

           #   pt3              output                           #
           #     ^                                               #
           #      \                                              #
           #       \              -> output with half_dist=True  #
           #        \                                            #
           #        pt2          input 2                         #
           #         ^                                           #
           #          \                                          #
           #           \                                         #
           #            \                                        #
           #            pt1      input 1                         #

       Args:
            lon1_in:    (array like) longitude of point 1
            lat1_in:    (array like) latitude  of point 1
            lon2_in:    (array like) longitude of point 2
            lat2_in:    (array like) latitude  of point 2
            crs:        Instance of Cartopy geoAxes in which pt coordinates are defined 
                        (default is PlateCarree)
            half_dist:  If true, pt 3 will be located at half the distance between pt1 and pt2

       Returns:
            (longitude, latitude)    (array like) of extended point 3

       Examples:

           Extend one point.

           >>> import numpy as np
           >>> import domutils.geo_tools as geo_tools
           >>> # coordinates of pt1 
           >>> lat1 = 0.; lon1 = 0.
           >>> # coordinates of pt2 
           >>> lat2 = 0.; lon2 = 90.
           >>> # coordinates of extended point
           >>> lon3, lat3 = geo_tools.lat_lon_extend(lon1,lat1,lon2,lat2)
           >>> print(lon3, lat3)
           [180.] [0.]

           Extend a number of points all at once

           >>> # coordinates for four pt1 
           >>> lat1 = [ 0., 0., 0., 0. ]
           >>> lon1 = [ 0., 0., 0., 0. ]
           >>> # coordinates for four pt2 
           >>> lat2 = [ 0.,90., 0., 30.]
           >>> lon2 = [90., 0.,45., 0. ]
           >>> # coordinates of extended points
           >>> lon3, lat3 = geo_tools.lat_lon_extend(lon1,lat1,lon2,lat2)
           >>> with np.printoptions(precision=1,suppress=True):
           ...      print(lon3)
           ...      print(lat3)
           [180. 180.  90.   0.]
           [ 0.   0.   0.  59.8]
           >>> #           ^
           >>> #           Presumably not =60. because cartopy uses a spheroid


    """

    import numpy as np
    import cartopy.crs as ccrs

    from .rotation_matrix  import rotation_matrix


    #ensure numpy type
    lon1 = np.array(lon1_in, copy=True)
    lat1 = np.array(lat1_in, copy=True)
    lon2 = np.array(lon2_in, copy=True)
    lat2 = np.array(lat2_in, copy=True)

    #convert lat_lon to xyz
    if crs is None:
        crs = ccrs.PlateCarree()
    geo_cent = crs.as_geocentric()
    xyz_pt1 = geo_cent.transform_points(crs, lon1, lat1)
    xyz_pt2 = geo_cent.transform_points(crs, lon2, lat2)

    #tmp storage vectors for xyz
    xyz_arr = np.zeros([lon1.size,3])

    #extend each pairs of points
    for ind, (v1, v2) in enumerate(zip(xyz_pt1, xyz_pt2)):

        #solve for angle
        theta = np.arccos( np.sum(v1*v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)) )
        if half_dist :
            theta /= 2.

        #get normal vector
        v3 = np.cross(v1,v2)
        v3 /= np.linalg.norm(v3)     #normalize 

        #;define rotation matrix that maps pt1 to pt2
        mm = rotation_matrix(v3, theta)

        #xyz position of result
        v4 = np.matmul(mm,v2)

        #save results for later conversion to latlon
        xyz_arr[ind,:] = v4
    #endfor

    #output in lat/lon
    lonlat = crs.transform_points(geo_cent, xyz_arr[:,0], xyz_arr[:,1], xyz_arr[:,2])
    lon3 = lonlat[:,0]
    lat3 = lonlat[:,1]

    return lon3, lat3
