
from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def lat_lon_range_az( lon1_in:      Any, 
                      lat1_in:      Any,
                      range_in:     Any,
                      azimuth_in:   Any,
                      crs:          Optional[Any]=None, 
                      earth_radius: Optional[Any]=None ):

    """ Computes lat/lon of a point at a given range and azimuth (meteorological angles)

       Given a point (pt1) on a sphere, this function returns the lat/lon of a second point (pt2) 
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
           #       |          -                           #
           #       |           -                          #
           #      pt1          -  E                       #
           #        \\         -                          #
           #  range  \\       -                           #
           #          \\     -                            #
           #           \\  -                              #
           #           pt2    output is lat lon of pt2    #


       Internally, two rotations on the sphere are conducted
            - 1st rotation shifts pt1 toward the North and is dictated by range
            - 2nd rotation is around point pt1 and is determined by azimuth

       Input arrays will be broadcasted together.

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
           >>> #   print(lon2, lat2) should give approximately
           >>> #   0.0 45.192099833854435
           >>> print(np.allclose((lon2, lat2), (0.0, 45.)))
           True
           >>>  #Also works for inputs arrays
           >>> lat1        = [[0.,     0],
           ...                [0.,     0]]
           >>> lon1        = [[0.,     0],
           ...                [0.,     0]]
           >>> range_km    = [[C/8.,  C/8.],
           ...                [C/8.,  C/8.]]
           >>> azimuth_deg = [[0.,     90.],
           ...                [-90.,   180]]
           >>> lon2, lat2 = geo_tools.lat_lon_range_az(lon1,lat1,range_km,azimuth_deg)
           >>> print(np.allclose(lon2, np.array([[ 0.0000000e+00,  4.5000000e+01],
           ...                                   [-4.5000000e+01,  7.0167093e-15]])))
           True

           Since arrays are broadcasted together, inputs that consists of repeated values
           can be passed as floats. 
           Here, we get the lat/lon along a circle 50km from a reference point

           >>> #longitudes and latitudes 
           >>> #of points along a circle of 50 km radius around a point at 37 deg N, 88 deg Ouest
           >>> #note how only azimuths is an array
           >>> lat0 =  37.
           >>> lon0 = -88.
           >>> ranges    = 50.
           >>> azimuths  = np.arange(0, 360, 10, dtype='float')
           >>> circle_lons, circle_lats = geo_tools.lat_lon_range_az(lat0, lon0, ranges, azimuths)
           >>> print(circle_lons)
           [37.         38.83132026 40.63355249 42.37690625 44.03018684 45.56010269
            46.93060903 48.10234846 49.03230506 49.67387639 49.97769473 49.89369016
            49.37504076 48.38468097 46.9046979  44.94791385 42.56907866 39.87096244
            37.         34.12903756 31.43092134 29.05208615 27.0953021  25.61531903
            24.62495924 24.10630984 24.02230527 24.32612361 24.96769494 25.89765154
            27.06939097 28.43989731 29.96981316 31.62309375 33.36644751 35.16867974]

           >>> print(circle_lats)
           [-87.5503392  -87.55592346 -87.57258224 -87.60003229 -87.63779731
            -87.68520148 -87.74135996 -87.8051664  -87.87527736 -87.95009446
            -88.02774645 -88.10607547 -88.18263607 -88.25472035 -88.31942859
            -88.37380702 -88.41506673 -88.44087378 -88.4496608  -88.44087378
            -88.41506673 -88.37380702 -88.31942859 -88.25472035 -88.18263607
            -88.10607547 -88.02774645 -87.95009446 -87.87527736 -87.8051664
            -87.74135996 -87.68520148 -87.63779731 -87.60003229 -87.57258224
            -87.55592346]


    """

    import numpy as np
    import cartopy.crs as ccrs
    from .rotation_matrix  import rotation_matrix_components
    from .lat_lon_to_xyz import latlon_to_unit_sphere_xyz
    from .lat_lon_to_xyz import unit_sphere_xyz_to_latlon

    #ensure numpy type; copy to avoid modifying inputs
    lon1       = np.array(lon1_in,    copy=True)
    lat1       = np.array(lat1_in,    copy=True)
    range_km   = np.array(range_in,   copy=True)
    azimuth    = np.array(azimuth_in, copy=True)

    #arrays are broadcasted together (eg, single values replicated to the shape of larger arrays)
    lon1, lat1, range_km, azimuth = np.broadcast_arrays(lon1, lat1, range_km, azimuth)

    #in the end, everything will be reshaped to the broadcasted shape
    output_shape = lon1.shape 

    #as flat arrays
    lon1     = lon1.ravel()
    lat1     = lat1.ravel()
    range_km = range_km.ravel()
    azimuth  = -1.*np.deg2rad(azimuth.ravel()) # -1 since rotation matrix does counterclockwise rotation

    #convert lat_lon to xyz
    xyz_pt1 = latlon_to_unit_sphere_xyz(lon1, lat1, combined=True)

    #xyz of north pole
    [xyz_hohoho] = latlon_to_unit_sphere_xyz(np.array([0.]), np.array([90.]))

    #radius of the earth
    if earth_radius is None:
        earth_radius = 6371.    #[km]

    #angle(s) (radians) for 1st rotation
    theta_r = range_km/earth_radius

    #1st rotation from point 0 towards the north pole 
    axis1 = np.cross(xyz_pt1, xyz_hohoho)
    m1a, m1b, m1c, m1d, m1e, m1f, m1g, m1h, m1i = rotation_matrix_components(axis1, theta_r)

    #2nd rotation around vector given by pt1
    m2a, m2b, m2c, m2d, m2e, m2f, m2g, m2h, m2i = rotation_matrix_components(xyz_pt1, azimuth)

    #combine the two rotations
    # equivalent to doing  np.matmul(M2, M1) for many M2 and M1 simultaneously
    m3a = m2a*m1a + m2b*m1d + m2c*m1g
    m3b = m2a*m1b + m2b*m1e + m2c*m1h
    m3c = m2a*m1c + m2b*m1f + m2c*m1i
    m3d = m2d*m1a + m2e*m1d + m2f*m1g
    m3e = m2d*m1b + m2e*m1e + m2f*m1h
    m3f = m2d*m1c + m2e*m1f + m2f*m1i
    m3g = m2g*m1a + m2h*m1d + m2i*m1g
    m3h = m2g*m1b + m2h*m1e + m2i*m1h
    m3i = m2g*m1c + m2h*m1f + m2i*m1i

    #clear original components
    del m1a, m1b, m1c, m1d, m1e, m1f, m1g, m1h, m1i
    del m2a, m2b, m2c, m2d, m2e, m2f, m2g, m2h, m2i 

    #get destination points by applying rotations to input locations
    #                     x                  y                  z
    x_arr = m3a*xyz_pt1[:,0] + m3b*xyz_pt1[:,1] + m3c*xyz_pt1[:,2]
    y_arr = m3d*xyz_pt1[:,0] + m3e*xyz_pt1[:,1] + m3f*xyz_pt1[:,2]
    z_arr = m3g*xyz_pt1[:,0] + m3h*xyz_pt1[:,1] + m3i*xyz_pt1[:,2]

    #output in lat/lon
    lon2, lat2 = unit_sphere_xyz_to_latlon(x_arr, y_arr, z_arr, combined=False)
    lon2 = np.reshape(lon2, output_shape)
    lat2 = np.reshape(lat2, output_shape)

    return lon2, lat2


if __name__ == "__main__":
    import doctest
    doctest.testmod()

