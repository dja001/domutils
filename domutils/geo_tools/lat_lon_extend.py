from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def lat_lon_extend(lon1_in:   Any,
                   lat1_in:   Any,
                   lon2_in:   Any,
                   lat2_in:   Any,
                   half_dist: bool=False,
                   predefined_theta=None) :
    """ Extends latitude and longitudes on a sphere

       Given two points (pt1 and pt2) on a sphere, this function returns a third point (pt3) at the 
       same distance and in the same direction as between pt1 and pt2.
       All points are defined with latitudes and longitudes, same altitude is assumed. 

       The diagram below hopefully make the purpose of this function clearer::

           #   pt3              output                           #
           #     ^                                               #
           #     \\                                              #
           #      \\              -> output with half_dist=True  #
           #       \\                                            #
           #        pt2          input 2                         #
           #         ^                                           #
           #          \\                                         #
           #           \\                                        #
           #            \\                                       #
           #            pt1      input 1                         #

       Args:
            lon1_in:    (array like) longitude of point 1
            lat1_in:    (array like) latitude  of point 1
            lon2_in:    (array like) longitude of point 2
            lat2_in:    (array like) latitude  of point 2
            half_dist:  If true, pt 3 will be located at half the distance between pt1 and pt2
            predefined_theta:  (array like) radians. If set, will determine distance between pt2 and pt3

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
           [ 0.  0.  0. 60.]


    """

    import numpy as np
    from .rotation_matrix  import rotation_matrix
    from .lat_lon_to_xyz import latlon_to_unit_sphere_xyz
    from .lat_lon_to_xyz import unit_sphere_xyz_to_latlon



    #ensure numpy type
    lon1 = np.asarray(lon1_in).flatten()
    lat1 = np.asarray(lat1_in).flatten()
    lon2 = np.asarray(lon2_in).flatten()
    lat2 = np.asarray(lat2_in).flatten()

    #convert lat_lon to xyz
    xyz_pt1 = latlon_to_unit_sphere_xyz(lon1, lat1, combined=True)
    xyz_pt2 = latlon_to_unit_sphere_xyz(lon2, lat2, combined=True)

    #tmp storage vectors for xyz
    xyz_arr = np.zeros([lon1.size,3])

    #extend each pairs of points
    for ind, (v1, v2) in enumerate(zip(xyz_pt1, xyz_pt2)):

        #solve for angle
        if predefined_theta is not None:
            theta = predefined_theta
        else:
            # Normalize vectors 
            v1_norm = v1 / np.linalg.norm(v1)
            v2_norm = v2 / np.linalg.norm(v2)
            
            # Use atan2 for numerical stability
            theta = np.arctan2(np.linalg.norm(np.cross(v1_norm, v2_norm)), np.dot(v1_norm, v2_norm))

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
    lon3, lat3 = unit_sphere_xyz_to_latlon(xyz_arr, combined=True)

    return lon3, lat3
