"""
A class for interpolating any data to any grids with Cartopy.

In addition to interpolation, this class is usefull to display geographical data.
Since projection mappings need to be defined only once for a given dataset/display combination, 
multi-pannels figures can be made efficiently.

Most of the action happens through the class :class:`ProjInds`.

The following figure illustrates the convention for storring data in numpy arrays. 
It is assumed that the first index (rows) represents x-y direction (longitudes):

.. image:: _static/xy.svg
                :align: center


"""

from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

class ProjInds():
    """ A class for making, keeping record of, and applying projection indices.

        This class handles the projection of gridded data with lat/lon coordinates
        to cartopy's own data space in geoAxes. 

        Args:
            src_lon:       (array like) longitude of data.
                           Has to be same dimension as data.
            src_lat:       (array like) latitude of data.
                           Has to be same dimension as data.
            dest_lon:      Longitude of destination grid on which the data will be regridded
            dest_lat:      Latitude of destination grid on which the data will be regridded
            extent:        To be used together with dest_crs, to get destination grid from a cartopy geoAxes
                           (array like) Bounds of geoAxes domain [lon_min, lon_max, lat_min, lat_max]
            dest_crs:      If provided, cartopy crs instance for the destination grid (necessary for plotting maps)
            source_crs:    Cartopy crs of the data coordinates.
                           If None, a Geodetic crs is used for using latitude/longitude coordinates.
            fig:           Instance of figure currently being used.
                           If None (the default) a new figure will be instantiated
                           but never displayed.
            image_res:     Pixel density of the figure being generated. eg (300,200)
                           means that the image displayed on the geoAxes will be 300 pixels
                           wide by 200 pixels high.
            extend_x:      Set to True (default) when the destination grid is larger than the source grid. 
                           This option allows to mark no data points with Missing rather than extrapolating.
                           Set to False for global grids.
            extend_y:      Same as extend_x but in the Y direction.
            average:       (bool) When true, all pts of a source grid falling within a destination
                           grid pt will be averaged. Usefull to display/interpolate hi resolution
                           data to a coarser grid.
                           Weighted averages can be obtained by providing weights to the *project_data*
                           method.
            smooth_radius: Boxcar averaging with a circular area of a given radius.
                           This option allows to perform smoothing at the same time as interpolation.
                           For each point in the destination grid, all source data points within
                           a radius given by *smooth_radius* will be averaged together.
            min_hits:      For use in conjunction with average or smooth_radius. This keyword
                           specifies the minimum number of data points for an average to be considered
                           valid.
            missing:       Value which will be assigned to points outside of the data domain.

        Example:

            Simple example showing how to project and display data.
            Rotation of points on the globe is also demonstrated

            >>> import numpy as np
            >>> import matplotlib as mpl
            >>> import matplotlib.pyplot as plt
            >>> import cartopy.crs as ccrs
            >>> import cartopy.feature as cfeature
            >>> import domutils.legs as legs
            >>> import domutils.geo_tools as geo_tools
            >>>
            >>> # make mock data and coordinates
            >>> # note that there is some regularity to the grid 
            >>> # but that it does not conform to any particular projection
            >>> regular_lons =     [ [-91. , -91  , -91   ],
            ...                      [-90. , -90  , -90   ],
            ...                      [-89. , -89  , -89   ] ]
            >>> regular_lats =     [ [ 44  ,  45  ,  46   ],
            ...                      [ 44  ,  45  ,  46   ],
            ...                      [ 44  ,  45  ,  46   ] ]
            >>> data_vals =        [ [  6.5,   3.5,    .5 ],
            ...                      [  7.5,   4.5,   1.5 ],
            ...                      [  8.5,   5.5,   2.5 ] ]
            >>> missing = -9999.
            >>>
            >>> #pixel resolution of image that will be shown in the axes
            >>> img_res = (800,600)
            >>> #point density for entire figure
            >>> mpl.rcParams['figure.dpi'] = 800
            >>>
            >>> #projection and extent of map being displayed
            >>> proj_aea = ccrs.AlbersEqualArea(central_longitude=-94.,
            ...                                 central_latitude=35.,
            ...                                 standard_parallels=(30.,40.))
            >>> map_extent=[-94.8,-85.2,43,48.]
            >>>
            >>> #-------------------------------------------------------------------
            >>> #regular lat/lons are boring, lets rotate the coordinate system about
            >>> # the central data point
            >>> 
            >>> #use cartopy transforms to get xyz coordinates
            >>> proj_ll = ccrs.Geodetic()
            >>> geo_cent = proj_ll.as_geocentric()
            >>> xyz = geo_cent.transform_points(proj_ll, np.asarray(regular_lons),
            ...                                          np.asarray(regular_lats))
            >>>
            >>> #lets rotate points by 45 degrees counter clockwise
            >>> theta = np.pi/4
            >>> rotation_matrix = geo_tools.rotation_matrix([xyz[1,1,0], #x
            ...                                              xyz[1,1,1], #y
            ...                                              xyz[1,1,2]],#z
            ...                                              theta)
            >>> rotated_xyz = np.zeros((3,3,3))
            >>> for ii, (lat_arr, lon_arr) in enumerate(zip(regular_lats, regular_lons)):
            ...     for jj, (this_lat, this_lon) in enumerate(zip(lat_arr, lat_arr)):
            ...         rotated_xyz[ii,jj,:] = np.matmul(rotation_matrix,[xyz[ii,jj,0], #x
            ...                                                           xyz[ii,jj,1], #y
            ...                                                           xyz[ii,jj,2]])#z
            >>>
            >>> #from xyz to lat/lon
            >>> rotated_latlon = proj_ll.transform_points(geo_cent, rotated_xyz[:,:,0],
            ...                                                     rotated_xyz[:,:,1],
            ...                                                     rotated_xyz[:,:,2])
            >>> rotatedLons = rotated_latlon[:,:,0]
            >>> rotatedLats = rotated_latlon[:,:,1]
            >>> # done rotating
            >>> #-------------------------------------------------------------------
            >>> 
            >>> #larger characters
            >>> mpl.rcParams.update({'font.size': 15})
            >>>
            >>> #instantiate figure
            >>> fig = plt.figure(figsize=(7.5,6.))
            >>> 
            >>> #instantiate object to handle geographical projection of data
            >>> # onto geoAxes with this specific crs and extent
            >>> ProjInds = geo_tools.ProjInds(rotatedLons, rotatedLats,extent=map_extent, dest_crs=proj_aea,
            ...                               image_res=img_res)
            >>> 
            >>> #axes for this plot
            >>> ax = fig.add_axes([.01,.1,.8,.8], projection=proj_aea)
            >>> ax.set_extent(map_extent)
            >>> 
            >>> # Set up colormapping object 
            >>> color_mapping = legs.PalObj(range_arr=[0.,9.],
            ...                              color_arr=['brown','blue','green','orange',
            ...                                         'red','pink','purple','yellow','b_w'],
            ...                              solid='col_dark',
            ...                              excep_val=missing, excep_col='grey_220')
            >>> 
            >>> #geographical projection of data into axes space
            >>> proj_data = ProjInds.project_data(data_vals)
            >>> 
            >>> #plot data & palette
            >>> color_mapping.plot_data(ax=ax,data=proj_data,
            ...                         palette='right', pal_units='[unitless]', 
            ...                         pal_format='{:4.0f}')   #palette options
            >>> 
            >>> #add political boundaries
            >>> dum = ax.add_feature(cfeature.STATES.with_scale('50m'), 
            ...                      linewidth=0.5, edgecolor='0.2',zorder=1)
            >>> 
            >>> #plot border and mask everything outside model domain
            >>> ProjInds.plot_border(ax, mask_outside=False, linewidth=2.)
            >>> 
            >>> #uncomment to save figure
            >>> plt.savefig('_static/projection_demo.svg')

            .. image:: _static/projection_demo.svg
                :align: center


            Example showing how ProjInds can also be used for nearest neighbor interpolation

            >>> import numpy as np
            >>> 
            >>> # Source data on a very simple grid
            >>> src_lon =     [ [-90.1 , -90.1  ],
            ...                 [-89.1 , -89.1  ] ]
            >>> 
            >>> src_lat =     [ [ 44.1  , 45.1  ],
            ...                 [ 44.1  , 45.1  ] ]
            >>> 
            >>> data    =     [ [  3    ,  1    ],
            ...                 [  4    ,  2    ] ]
            >>> 
            >>> # destination grid where we want data
            >>> # Its larger than the source grid and slightly offset
            >>> dest_lon =     [ [-91. , -91  , -91 , -91  ],
            ...                  [-90. , -90  , -90 , -90  ],
            ...                  [-89. , -89  , -89 , -89  ],
            ...                  [-88. , -88  , -88 , -88  ] ]
            >>> 
            >>> dest_lat =     [ [ 43  ,  44  ,  45 ,  46 ],
            ...                  [ 43  ,  44  ,  45 ,  46 ],
            ...                  [ 43  ,  44  ,  45 ,  46 ],
            ...                  [ 43  ,  44  ,  45 ,  46 ] ]
            >>>
            >>> #instantiate object to handle interpolation
            >>> ProjInds = geo_tools.ProjInds(data_xx=src_lon,   data_yy=src_lat,
            ...                               dest_lon=dest_lon, dest_lat=dest_lat,
            ...                               missing=-99.)
            >>> #interpolate data with "project_data"
            >>> interpolated = ProjInds.project_data(data)
            >>> #nearest neighbor output, pts outside the domain are set to missing
            >>> #Interpolation with border detection in all directions
            >>> print(interpolated)
            [[-99. -99. -99. -99.]
             [-99.   3.   1. -99.]
             [-99.   4.   2. -99.]
             [-99. -99. -99. -99.]]
            >>>
            >>>
            >>> #on some domain, border detection is not desirable, it can be turned off
            >>> #
            >>> # extend_x here refers to the dimension in data space (longitudes) that are
            >>> # represented along rows of python array.
            >>>
            >>> # for example:
            >>> 
            >>> # Border detection in Y direction (latitudes) only
            >>> proj_inds_ext_y = geo_tools.ProjInds(data_xx=src_lon,   data_yy=src_lat,
            ...                                      dest_lon=dest_lon, dest_lat=dest_lat,
            ...                                      missing=-99.,
            ...                                      extend_x=False)
            >>> interpolated_ext_y = proj_inds_ext_y.project_data(data)
            >>> print(interpolated_ext_y)
            [[-99.   3.   1. -99.]
             [-99.   3.   1. -99.]
             [-99.   4.   2. -99.]
             [-99.   4.   2. -99.]]
            >>> #
            >>> # Border detection in X direction (longitudes) only
            >>> proj_inds_ext_x = geo_tools.ProjInds(data_xx=src_lon,   data_yy=src_lat,
            ...                                      dest_lon=dest_lon, dest_lat=dest_lat,
            ...                                      missing=-99.,
            ...                                      extend_y=False)
            >>> interpolated_ext_x = proj_inds_ext_x.project_data(data)
            >>> print(interpolated_ext_x)
            [[-99. -99. -99. -99.]
             [  3.   3.   1.   1.]
             [  4.   4.   2.   2.]
             [-99. -99. -99. -99.]]
            >>> # 
            >>> # no border detection
            >>> proj_inds_no_b = geo_tools.ProjInds(data_xx=src_lon,   data_yy=src_lat,
            ...                                     dest_lon=dest_lon, dest_lat=dest_lat,
            ...                                     missing=-99.,
            ...                                     extend_x=False, extend_y=False)
            >>> interpolated_no_b = proj_inds_no_b.project_data(data)
            >>> print(interpolated_no_b)
            [[3. 3. 1. 1.]
             [3. 3. 1. 1.]
             [4. 4. 2. 2.]
             [4. 4. 2. 2.]]

            Interpolation to coarser grids can be done with the *nearest* keyword. 
            With this flag, all high-resoution data falling within a tile of the 
            destination grid will be averaged together. 
            Border detection works as in the example above.

            >>> import numpy as np
            >>> # source data on a very simple grid
            >>> src_lon =     [ [-88.2 , -88.2  ],
            ...                 [-87.5 , -87.5  ] ]
            >>> 
            >>> src_lat =     [ [ 43.5  , 44.1  ],
            ...                 [ 43.5  , 44.1  ] ]
            >>> 
            >>> data    =     [ [  3    ,  1    ],
            ...                 [  4    ,  2    ] ]
            >>> 
            >>> # coarser destination grid where we want data
            >>> dest_lon =     [ [-92. , -92  , -92 , -92  ],
            ...                  [-90. , -90  , -90 , -90  ],
            ...                  [-88. , -88  , -88 , -88  ],
            ...                  [-86. , -86  , -86 , -86  ] ]
            >>> 
            >>> dest_lat =     [ [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ] ]
            >>> 
            >>> #instantiate object to handle interpolation
            >>> #Note the average keyword set to true
            >>> ProjInds = geo_tools.ProjInds(data_xx=src_lon,   data_yy=src_lat,
            ...                               dest_lon=dest_lon, dest_lat=dest_lat,
            ...                               average=True, missing=-99.)
            >>> 
            >>> #interpolate data with "project_data"
            >>> interpolated = ProjInds.project_data(data)
            >>> 
            >>> #Since all high resolution data falls into one of the output 
            >>> #grid tile, they are all aaveraged togetherL:  (1+2+3+4)/4 = 2.5 
            >>> print(interpolated)
            [[-99.  -99.  -99.  -99. ]
             [-99.  -99.  -99.  -99. ]
             [-99.    2.5 -99.  -99. ]
             [-99.  -99.  -99.  -99. ]]
            >>>
            >>> #weighted average can be obtained by providing weights for each data pt 
            >>> #being averaged
            >>> weights   =     [ [  0.5   ,  1.    ],
            ...                   [  1.    ,  0.25  ] ]
            >>> 
            >>> weighted_avg = ProjInds.project_data(data, weights=weights)
            >>> #result is a weighted average:  
            >>> # (1.*1 + 0.25*2 + 0.5*3 + 1.*4) / (1.+0.25+0.5+1.) = 7.0/2.75 = 2.5454
            >>> print(weighted_avg)
            [[-99.         -99.         -99.         -99.        ]
             [-99.         -99.         -99.         -99.        ]
             [-99.           2.54545455 -99.         -99.        ]
             [-99.         -99.         -99.         -99.        ]]

            Sometimes, it is useful to smooth data during the interpolation process.
            For example when comparing radar measurement against model output, smoothing
            can be used to remove the small scales present in the observations but that
            the model cannot represent. 
            
            Use the *smoooth_radius* to average all source data point within a certain radius
            (in km) of the destination grid tiles. 

            >>> # source data on a very simple grid
            >>> src_lon =     [ [-88.2 , -88.2  ],
            ...                 [-87.5 , -87.5  ] ]
            >>> 
            >>> src_lat =     [ [ 43.5  , 44.1  ],
            ...                 [ 43.5  , 44.1  ] ]
            >>> 
            >>> data    =     [ [  3    ,  1    ],
            ...                 [  4    ,  2    ] ]
            >>> 
            >>> # coarser destination grid where we want data
            >>> dest_lon =     [ [-92. , -92  , -92 , -92  ],
            ...                  [-90. , -90  , -90 , -90  ],
            ...                  [-88. , -88  , -88 , -88  ],
            ...                  [-86. , -86  , -86 , -86  ] ]
            >>> 
            >>> dest_lat =     [ [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ],
            ...                  [ 42  ,  44  ,  46 ,  48 ] ]
            >>> 
            >>> #instantiate object to handle interpolation
            >>> #All source data points found within 300km of each destination 
            >>> #grid tiles will be averaged together
            >>> ProjInds = geo_tools.ProjInds(data_xx=src_lon,    data_yy=src_lat,
            ...                               dest_lat=dest_lat,  dest_lon=dest_lon,
            ...                               smooth_radius=300., missing=-99.)
            >>> 
            >>> #interpolate and smooth data with "project_data"
            >>> interpolated = ProjInds.project_data(data)
            >>> 
            >>> #output is smoother than data source
            >>> print(interpolated)
            [[-99.         -99.         -99.         -99.        ]
             [  2.66666667   2.5          1.5        -99.        ]
             [  2.5          2.5          2.5        -99.        ]
             [  2.5          2.5          1.5        -99.        ]]




             

    """
    def __init__(self,
                 data_xx:       Optional[Any]=None,
                 data_yy:       Optional[Any]=None,
                 src_lon:       Optional[Any]=None,
                 src_lat:       Optional[Any]=None,
                 dest_lon:      Optional[Any]=None,
                 dest_lat:      Optional[Any]=None,
                 extent:        Optional[Any]=None,
                 dest_crs:      Optional[Any]=None,
                 source_crs:    Optional[Any]=None,
                 fig:           Optional[Any]=None,
                 image_res:     Optional[tuple]=(400,400),
                 extend_x:      Optional[Any]=True,
                 extend_y:      Optional[Any]=True,
                 average:       Optional[Any]=False,
                 smooth_radius: Optional[Any]=None,
                 min_hits:      Optional[Any]=1,
                 missing:       Optional[float]=-9999.):

        from os import linesep as newline
        import warnings
        import numpy as np
        import cartopy.img_transform as cimgt
        import matplotlib.pyplot as plt
        #local functions
        from ._find_nearest     import _find_nearest
        from .lat_lon_extend   import lat_lon_extend


        #check specification of destination grid
        if (dest_lon is not None) and (dest_lat is not None):
            #destination lat/lon are provided by user, use those
            dest_lon = np.asarray(dest_lon)
            dest_lat = np.asarray(dest_lat)

        elif (dest_crs is not None) :
            #we are projecting data onto an image, get destination grid from Cartopy
            delete_dummy_fig = False
            if fig is None:
                dummy_fig = plt.figure()
                delete_dummy_fig = True
            else:
                dummy_fig = fig
            dummy_ax = dummy_fig.add_axes([0.,0.,1.,1.], projection=dest_crs)
            if extent is not None:
                dummy_ax.set_extent(extent)
            dummy_ax.outline_patch.set_linewidth(0) #No axes contour line
            
            if extent is not None:
                #get corners of image in data space
                transform_data_to_axes = dummy_ax.transData + dummy_ax.transAxes.inverted()
                transform_axes_to_data = transform_data_to_axes.inverted()
                pts = ((0.,0.),(1.,1.))
                pt1, pt2 = transform_axes_to_data.transform(pts)
        
                #get regular grid of pts in projected figure    units of dest_lon and dest_lat are in dataspace
                #                                                                nx            ny
                dest_lon, dest_lat, extent = cimgt.mesh_projection(dest_crs, image_res[0], image_res[1],
                                                                   x_extents=[pt1[0],pt2[0]], y_extents=[pt1[1],pt2[1]])
            else:
                #use default extent for this projection
                dest_lon, dest_lat, extent = cimgt.mesh_projection(dest_crs, image_res[0], image_res[1])

        else: 
            raise ValueError(' The lat/lon of the destination grid must be specified using:'              + newline +
                             '    - Directly through the use of the "dest_lat" and "dest_lon" keywords '  + newline +
                             '    - By specifying "dest_crs" and the "extent" keywords of a figure being' + newline +
                             '      generated')


        #check specification of input grid
        if (src_lon is not None) and (src_lat is not None):
             #source grid provided by user, use it 
             pass
        elif (data_xx is not None) and (data_yy is not None):
            #old way of providing same info, use those and write a deprecation message
            src_lon = data_xx
            src_lat = data_yy
            warnings.warn('The keywords "data_xx" and "data_yy" are deprecated. ' + newline +
                          'Use keywords "src_lon" and "src_lat" instead ', DeprecationWarning)
        else : 
            raise ValueError(' The lat/lon of the source data mush be provided through the "src_lon" and "src_lat" keywords.')

        
        #insure input coords are numpy arrays
        np_xx = np.asarray(src_lon)
        np_yy = np.asarray(src_lat)
        
        #only necessary for plotting border
        # borders make no sense for continuous grids such as global grids
        # set either extend_x or extend_y = False to skip computation of borders
        if extend_x and extend_y:
            #get lat/lon at the border of the domain        Note the half dist in the call to lat_lon_extend
            border_lat2d = np.zeros(np.asarray(np_yy.shape)+2)
            border_lon2d = np.zeros(np.asarray(np_xx.shape)+2)
            #center contains data lat/lon
            border_lat2d[1:-1,1:-1] = np_yy
            border_lon2d[1:-1,1:-1] = np_xx
            #extend left side
            border_lon2d[1:-1,0], border_lat2d[1:-1,0] = lat_lon_extend(np_xx[:,1],np_yy[:,1],np_xx[:,0],np_yy[:,0], half_dist=True)
            #extend right side
            border_lon2d[1:-1,-1], border_lat2d[1:-1,-1] = lat_lon_extend(np_xx[:,-2],np_yy[:,-2],np_xx[:,-1],np_yy[:,-1], half_dist=True)
            #extend top
            border_lon2d[0,:], border_lat2d[0,:] = lat_lon_extend(border_lon2d[2,:],border_lat2d[2,:],border_lon2d[1,:],border_lat2d[1,:], half_dist=True)
            #extend bottom
            border_lon2d[-1,:], border_lat2d[-1,:] = lat_lon_extend(border_lon2d[-3,:],border_lat2d[-3,:],border_lon2d[-2,:],border_lat2d[-2,:], half_dist=True)
            #we are only interested in the extended values
            left   = np.flip(border_lon2d[1:-1,0].flatten())
            top    =         border_lon2d[0,:].flatten()
            right  =         border_lon2d[1:-1,-1].flatten()
            bottom = np.flip(border_lon2d[-1,:]).flatten()
            border_lons = np.concatenate([left,top,right,bottom,np.array(left[0],ndmin=1)])  #last entry is first for a complete polygon
            left   = np.flip(border_lat2d[1:-1,0].flatten())
            top    =         border_lat2d[0,:].flatten()
            right  =         border_lat2d[1:-1,-1].flatten()
            bottom = np.flip(border_lat2d[-1,:]).flatten()
            border_lats = np.concatenate([left,top,right,bottom,np.array(left[0],ndmin=1)])
        else:
            border_lats = None
            border_lons = None
        
        #find proj_ind using _find_nearest
        if smooth_radius is not None:
            #when using a smoothing radius, the tree will be used in project_data
            kdtree, dest_xyz = _find_nearest(src_lon, src_lat, dest_lon, dest_lat,
                                             smooth_radius=smooth_radius,
                                             extend_x=False, extend_y=False, missing=missing,
                                             source_crs=source_crs, dest_crs=dest_crs)
        elif average:
            #reverse order since we will likely encounter need multiple data pts per destination grid tile
            proj_ind = _find_nearest(dest_lon, dest_lat, src_lon, src_lat,
                                     extend_x=False, extend_y=False, missing=missing,
                                     source_crs=source_crs, dest_crs=dest_crs)
        else:
            #regular nearest neighbor search
            proj_ind = _find_nearest(src_lon, src_lat, dest_lon, dest_lat,
                                     extend_x=extend_x, extend_y=extend_y, missing=missing,
                                     source_crs=source_crs, dest_crs=dest_crs)
        
        #save needed data
        #data needed for projecting data
        self.data_shape = np_xx.shape
        self.dest_shape = dest_lon.shape
        self.min_hits = min_hits
        self.missing = missing

        if smooth_radius is not None:
            #crs space in meters
            self.smooth_radius_m = smooth_radius * 1e3
            self.kdtree = kdtree
            self.dest_xyz = dest_xyz
            self.average = True     #uses the averaging mechanism during smoothing
            self.destLon = dest_lon  #need those in project_data when smoothing
            self.destLat = dest_lat
        else:
            self.smooth_radius_m = None
            self.proj_ind  = proj_ind
            self.average   = average
        
        #data needed for plotting border
        self.border_lons = border_lons
        self.border_lats = border_lats
        
        #cleanup
        if dest_crs:
            dummy_ax.remove()
            if delete_dummy_fig :
                plt.close(dummy_fig)



    def project_data(self,
                     data:Any,
                     weights:Optional[Any]  = None,
                     missing_v:Optional[float]= -9999.):
        """ Project data into geoAxes space

            Args:
                data:       (array like), data values to be projected. 
                            Must have the same dimension as the lat/lon coordinates used to 
                            instantiate the class.
                weights:    (array like), weights to be applied during averaging 
                            (see average and smooth_radius keyword in ProjInds)
                missing_v:  Value in input data that will be neglected during the averaging process
                            Has no impact unless *average* or *smooth_radius* are used in class
                            instantiation.

            Returns:
                A numpy array of the same shape as destination grid used to instantiate the class

        """
        import numpy as np

        #ensure numpy
        np_data = np.asarray(data)

        if self.smooth_radius_m is None :
            #make sure data is of the right shape
            if (np_data.shape != self.data_shape) :
                raise ValueError("data is not of the same shape as the coordinates used to initiate projection object")
        else:
            #there are no constraints on data shape if smoothing is used during interpolation
            pass

        #flatten data
        data_flat = np_data.ravel()

        #fill it where needed
        if self.average :
            #init matrices
            accumulator = np.zeros(self.dest_shape).ravel()
            denom       = np.zeros(self.dest_shape).ravel()
            averaged    =  np.full(self.dest_shape, self.missing).ravel()
            n_hits       = np.zeros(self.dest_shape, dtype='int32').ravel()
            #init/check weights matrix
            if weights is None:
                #by default all data pts have equal weights = 1.
                weights_np = np.ones(np_data.shape).ravel()
            else:
                #weights were provided
                weights_np = np.asarray(weights)
                if (weights_np.shape != np_data.shape) :
                    raise ValueError("Weights should have the same shape as data")
            weights_flat = weights_np.ravel()

            if self.smooth_radius_m is not None:
                #smooth all data found within distance specified by smooth_radius
                for ind, xyz in enumerate(self.dest_xyz):

                    good_pts = self.kdtree.query_ball_point(xyz, self.smooth_radius_m)
                    this_data    = data_flat[good_pts]
                    (valid_pts,) = np.asarray((this_data - missing_v) > 1e-3).nonzero()
                    if valid_pts.size > 0 :
                        this_data   = this_data[valid_pts]
                        this_weights     = weights_flat[np.asarray(good_pts)[valid_pts]]
                        accumulator[ind] = np.sum(this_weights*this_data)
                        denom[ind]       = np.sum(this_weights)
                        n_hits[ind]      = valid_pts.size

                
            else:
                #average out all input falling within output grid tile
                (good_pts,) = np.asarray( np.abs(self.proj_ind - self.missing) >= 1e-3 ).nonzero()
                if good_pts.size > 0 :
                    in_inds = self.proj_ind[good_pts]
                    ii = np.arange(self.proj_ind.size)
                    out_inds = ii[good_pts]
                    for in_pt, out_pt in zip(in_inds, out_inds):
                        accumulator[in_pt] += weights_flat[out_pt]*data_flat[out_pt]
                        denom[in_pt]       += weights_flat[out_pt]
                        n_hits[in_pt]      += 1

            #the averaging part
            (hits,) = np.logical_and(denom > 0., n_hits >= self.min_hits).nonzero()
            if hits.size > 0 :
                averaged[hits] = accumulator[hits]/denom[hits]

            #output is a 2D array
            proj_data = np.reshape(averaged, self.dest_shape)

        else:

            #init output array
            proj_data = np.full(self.dest_shape, self.missing)
            (good_pts,) = np.asarray( (self.proj_ind >= 0) ).nonzero()
            if good_pts.size != 0:
                proj_data.ravel()[good_pts] = data_flat[self.proj_ind[good_pts]]

        return proj_data



    def plot_border(self,
                    ax:Any=None,
                    crs:Optional[Any]=None,
                    linewidth:Optional[float]=0.5,
                    zorder:Optional[int]=3,
                    mask_outside:Optional[bool]=False):
        """ Plot border of a more or less regularly gridded domain

            Optionally, mask everything that is outside the domain for simpler
            figures. 
            
            Args:
                ax:           Instance of a cartopy geoAxes where border is to be plotted
                crs:          Cartopy crs of the data coordinates. 
                              If None, a Geodetic crs is used for using latitude/longitude coordinates.
                linewidth:    Width of border being plotted
                mask_outside: If True, everything outside the domain will be hidden
                zorder:       zorder for the mask being applied with maskOutside=True. This number
                              should be larger than any other zorder in the axes. 

            Returns:
                Nothing
        """
        import numpy as np
        import cartopy.crs as ccrs
        import warnings

        if ax is None:
            raise ValueError('The "ax" keyword must be provided')

        #assume data is defined by latitude/longigude
        if crs is None :
            proj_ll = ccrs.Geodetic()

        #clip pixels outside of domain
        if self.smooth_radius_m is None:
            if mask_outside :
                #get corners of image in data space
                transform_data_to_axes = ax.transData + ax.transAxes.inverted()
                transform_axes_to_data = transform_data_to_axes.inverted()
                pts = ((0.,0.),(1.,1.))
                pt1, pt2 = transform_axes_to_data.transform(pts)
                extent_data_space = [pt1[0],pt2[0],pt1[1],pt2[1]]
            
                rgb   = np.full(self.dest_shape + (3,), 1., dtype='float32')
                alpha = np.full(self.dest_shape + (1,), 0., dtype='float32')
                #set transparent inside of the domain, opaque outside
                outside_pts = np.asarray( (self.proj_ind < 0) ).nonzero()
                if outside_pts[0].size != 0:
                    alpha.ravel()[outside_pts] = 1.

                rgba = np.concatenate([rgb,alpha],axis=2)

                #no lines on the contour of the axes
                ax.outline_patch.set_linewidth(0.0)

                #plot mask
                ax.imshow(rgba, axes=ax, interpolation='nearest', extent=extent_data_space, zorder=2)

                #white outline around border to mask border pixel shown by some renderers
                xx = [0., 1, 1, 0, 0]
                yy = [0., 0, 1, 1, 0]
                ax.plot(xx, yy, color='white', linewidth=1., transform=ax.transAxes, zorder=4,clip_on=False)
        else :
            if mask_outside :
                warnings.warn('The keywords mask_outside is not compatible with smooth_radius, it is now ignored')




        #plot border
        ax.plot(self.border_lons, self.border_lats,
                color='.1', linewidth=linewidth, transform=proj_ll, zorder=zorder)




    def main():
        pass

    if __name__ == "__main__":
        main()




