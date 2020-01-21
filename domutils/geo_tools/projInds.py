"""
A class for interpolating any data to any grids with Cartopy.

In addition to interpolation, this class is usefull to display geographical data.
Since projection mappings need to be defined only once for a given dataset/display combination, 
multi-pannels figures can be made efficiently.

Most of the action happens through the class :class:`projInds`. 

The following figure illustrates the convention for storring data in numpy arrays. 
It is assumed that the first index (rows) represents x-y direction (longitudes):

.. image:: _static/xy.svg
                :align: center


"""

from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

class projInds():
    """ A class for making, keeping record of, and applying projection indices.

        This class handles the projection of gridded data with lat/lon coordinates
        to cartopy's own data space in geoAxes. 

        Args:
            srcLon:       (array like) longitude of data. 
                          Has to be same dimension as data.
            srcLat:       (array like) latitude of data.
                          Has to be same dimension as data.
            destLon:      Longitude of destination grid on which the data will be regridded
            destLat:      Latitude of destination grid on which the data will be regridded
            extent:       To be used together with destCrs, to get destination grid from a cartopy geoAxes 
                          (array like) Bounds of geoAxes domain [lon_min, lon_max, lat_min, lat_max]
            destCrs:      If provided, cartopy crs instance for the destination grid (necessary for plotting maps)
            sourceCrs:    Cartopy crs of the data coordinates. 
                          If None, a Geodetic crs is used for using latitude/longitude coordinates.
            fig:          Instance of figure currently being used. 
                          If None (the default) a new figure will be instantiated 
                          but never displayed. 
            image_res:    Pixel density of the figure being generated. eg (300,200)
                          means that the image displayed on the geoAxes will be 300 pixels
                          wide by 200 pixels high. 
            extendX:      Needed when the destination grid is larger than the source grid, to
                          mark no data points with Missing rather than extrapolating. 
                          Set to False if extending the source grid in the x direction 
                          is inappropriate for the application (e.g. global grid).
            extendY:      Same as extendX but in the Y direction.
            average:      (bool) When true, all pts of a source grid falling within a destination
                          grid pt will be averaged. Usefull to display/interpolate hi resolution
                          data to a coarser grid.
                          Weighted averages can be obtained by providing weights to the *project_data*
                          method.
            smoothRadius: Boxcar averaging with a circular area of a given radius.
                          This option allows to perform smoothing at the same time as interpolation.
                          For each point in the destination grid, all source data points within 
                          a radius given by *smoothRadius* will be averaged together. 
            minHits       For use in conjunction with average or smoothRadius. This keyword
                          specifies the minimum number of data points for an average to be considered 
                          valid. 
            missing:      Value which will be assigned to points outside of the data domain.

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
            >>> regularLons =     [ [-91. , -91  , -91   ], 
            ...                     [-90. , -90  , -90   ], 
            ...                     [-89. , -89  , -89   ] ]
            >>> regularLats =     [ [ 44  ,  45  ,  46   ],
            ...                     [ 44  ,  45  ,  46   ], 
            ...                     [ 44  ,  45  ,  46   ] ]
            >>> dataVals =        [ [  6.5,   3.5,    .5 ],
            ...                     [  7.5,   4.5,   1.5 ],
            ...                     [  8.5,   5.5,   2.5 ] ]
            >>> missing = -9999.
            >>>
            >>> #pixel resolution of image that will be shown in the axes
            >>> imgRes = (800,600)
            >>> #point density for entire figure
            >>> mpl.rcParams['figure.dpi'] = 800
            >>>
            >>> #projection and extent of map being displayed
            >>> proj_aea = ccrs.AlbersEqualArea(central_longitude=-94.,
            ...                                 central_latitude=35.,
            ...                                 standard_parallels=(30.,40.))
            >>> mapExtent=[-94.8,-85.2,43,48.]  
            >>>
            >>> #-------------------------------------------------------------------
            >>> #regular lat/lons are boring, lets rotate the coordinate system about
            >>> # the central data point
            >>> 
            >>> #use cartopy transforms to get xyz coordinates
            >>> proj_ll = ccrs.Geodetic()
            >>> geo_cent = proj_ll.as_geocentric()
            >>> xyz = geo_cent.transform_points(proj_ll, np.asarray(regularLons), 
            ...                                          np.asarray(regularLats))
            >>>
            >>> #lets rotate points by 45 degrees counter clockwise
            >>> theta = np.pi/4
            >>> rotationMatrix = geo_tools.rotation_matrix([xyz[1,1,0], #x
            ...                                             xyz[1,1,1], #y
            ...                                             xyz[1,1,2]],#z
            ...                                             theta)
            >>> rotated_xyz = np.zeros((3,3,3))
            >>> for ii, (latArr, lonArr) in enumerate(zip(regularLats, regularLons)):
            ...     for jj, (thisLat, thisLon) in enumerate(zip(latArr, latArr)):
            ...         rotated_xyz[ii,jj,:] = np.matmul(rotationMatrix,[xyz[ii,jj,0], #x
            ...                                                          xyz[ii,jj,1], #y
            ...                                                          xyz[ii,jj,2]])#z
            >>>
            >>> #from xyz to lat/lon
            >>> rotatedLatlon = proj_ll.transform_points(geo_cent, rotated_xyz[:,:,0], 
            ...                                                    rotated_xyz[:,:,1],
            ...                                                    rotated_xyz[:,:,2])
            >>> rotatedLons = rotatedLatlon[:,:,0]
            >>> rotatedLats = rotatedLatlon[:,:,1]
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
            >>> projInds = geo_tools.projInds(rotatedLons, rotatedLats,extent=mapExtent, destCrs=proj_aea, 
            ...                               image_res=imgRes)
            >>> 
            >>> #axes for this plot
            >>> ax = fig.add_axes([.01,.1,.8,.8], projection=proj_aea)
            >>> ax.set_extent(mapExtent)
            >>> 
            >>> # Set up colormapping object 
            >>> colorMapping = legs.pal_obj(range_arr=[0.,9.],
            ...                             color_arr=['brown','blue','green','orange',
            ...                                        'red','pink','purple','yellow','b_w'],
            ...                             solid='col_dark',
            ...                             excep_val=missing, excep_col='grey_220')
            >>> 
            >>> #geographical projection of data into axes space
            >>> projData = projInds.project_data(dataVals)
            >>> 
            >>> #plot data & palette
            >>> colorMapping.plot_data(ax=ax,data=projData,
            ...                         palette='right', pal_units='[unitless]', 
            ...                         pal_format='{:4.0f}')   #palette options
            >>> 
            >>> #add political boundaries
            >>> dum = ax.add_feature(cfeature.STATES.with_scale('50m'), 
            ...                      linewidth=0.5, edgecolor='0.2',zorder=1)
            >>> 
            >>> #plot border and mask everything outside model domain
            >>> projInds.plotBorder(ax, maskOutside=False, linewidth=2.)
            >>> 
            >>> #uncomment to save figure
            >>> plt.savefig('_static/projection_demo.svg')

            .. image:: _static/projection_demo.svg
                :align: center


            Example showing how projInds can also be used for nearest neighbor interpolation

            >>> import numpy as np
            >>> 
            >>> # Source data on a very simple grid
            >>> srcLon =     [ [-90.1 , -90.1  ], 
            ...                [-89.1 , -89.1  ] ]
            >>> 
            >>> srcLat =     [ [ 44.1  , 45.1  ],
            ...                [ 44.1  , 45.1  ] ]
            >>> 
            >>> data   =     [ [  3    ,  1    ],
            ...                [  4    ,  2    ] ]
            >>> 
            >>> # destination grid where we want data
            >>> # Its larger than the source grid and slightly offset
            >>> destLon =     [ [-91. , -91  , -91 , -91  ], 
            ...                 [-90. , -90  , -90 , -90  ], 
            ...                 [-89. , -89  , -89 , -89  ], 
            ...                 [-88. , -88  , -88 , -88  ] ]
            >>> 
            >>> destLat =     [ [ 43  ,  44  ,  45 ,  46 ],
            ...                 [ 43  ,  44  ,  45 ,  46 ], 
            ...                 [ 43  ,  44  ,  45 ,  46 ], 
            ...                 [ 43  ,  44  ,  45 ,  46 ] ]
            >>>
            >>> #instantiate object to handle interpolation
            >>> projInds = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                               destLon=destLon, destLat=destLat,
            ...                               missing=-99.)
            >>> #interpolate data with "project_data"
            >>> interpolated = projInds.project_data(data)
            >>> #nearest neighbor output, pts outside the domain are set to missing
            >>> #Interpolation with border detection in all directions
            >>> print(interpolated)
            [[-99. -99. -99. -99.]
             [-99.   3.   1. -99.]
             [-99.   4.   2. -99.]
             [-99. -99. -99. -99.]]
            >>>
            >>>
            >>> #on some domain, border detection is not desireable, it can be turned off
            >>> #
            >>> # extendX here refers to the dimension in data space (longitudes) that are 
            >>> # represented along rows of python array.
            >>>
            >>> # for example:
            >>> 
            >>> # Border detection in Y direction (latitudes) only
            >>> projIndsExtY = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                                  destLon=destLon, destLat=destLat, 
            ...                                  missing=-99., 
            ...                                  extendX=False)
            >>> interpolatedExtY = projIndsExtY.project_data(data)
            >>> print(interpolatedExtY)
            [[-99.   3.   1. -99.]
             [-99.   3.   1. -99.]
             [-99.   4.   2. -99.]
             [-99.   4.   2. -99.]]
            >>> #
            >>> # Border detection in X direction (longitudes) only
            >>> projIndsExtX = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                                  destLon=destLon, destLat=destLat, 
            ...                                  missing=-99., 
            ...                                  extendY=False)
            >>> interpolatedExtX = projIndsExtX.project_data(data)
            >>> print(interpolatedExtX)
            [[-99. -99. -99. -99.]
             [  3.   3.   1.   1.]
             [  4.   4.   2.   2.]
             [-99. -99. -99. -99.]]
            >>> # 
            >>> # no border detection
            >>> projIndsNoB = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                                  destLon=destLon, destLat=destLat, 
            ...                                  missing=-99., 
            ...                                  extendX=False, extendY=False)
            >>> interpolatedNoB = projIndsNoB.project_data(data)
            >>> print(interpolatedNoB)
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
            >>> srcLon =     [ [-88.2 , -88.2  ], 
            ...                [-87.5 , -87.5  ] ]
            >>> 
            >>> srcLat =     [ [ 43.5  , 44.1  ],
            ...                [ 43.5  , 44.1  ] ]
            >>> 
            >>> data   =     [ [  3    ,  1    ],
            ...                [  4    ,  2    ] ]
            >>> 
            >>> # coarser destination grid where we want data
            >>> destLon =     [ [-92. , -92  , -92 , -92  ], 
            ...                 [-90. , -90  , -90 , -90  ], 
            ...                 [-88. , -88  , -88 , -88  ], 
            ...                 [-86. , -86  , -86 , -86  ] ]
            >>> 
            >>> destLat =     [ [ 42  ,  44  ,  46 ,  48 ],
            ...                 [ 42  ,  44  ,  46 ,  48 ], 
            ...                 [ 42  ,  44  ,  46 ,  48 ], 
            ...                 [ 42  ,  44  ,  46 ,  48 ] ]
            >>> 
            >>> #instantiate object to handle interpolation
            >>> #Note the average keyword set to true
            >>> projInds = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                              destLon=destLon, destLat=destLat,
            ...                              average=True, missing=-99.)
            >>> 
            >>> #interpolate data with "project_data"
            >>> interpolated = projInds.project_data(data)
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
            >>> weightedAvg = projInds.project_data(data, weights=weights)
            >>> #result is a weighted average:  
            >>> # (1.*1 + 0.25*2 + 0.5*3 + 1.*4) / (1.+0.25+0.5+1.) = 7.0/2.75 = 2.5454
            >>> print(weightedAvg)
            [[-99.         -99.         -99.         -99.        ]
             [-99.         -99.         -99.         -99.        ]
             [-99.           2.54545455 -99.         -99.        ]
             [-99.         -99.         -99.         -99.        ]]

            Sometimes, it is usefull to smooth data during the interpolation proces. 
            For example when comparing radar measurement against model output, smoothing
            can be used to remove the small scales present in the observations but that
            the model cannot represent. 
            
            Use the *smooothRadius* to average all source data point within a certain radius
            (in km) of the destination grid tiles. 

            >>> # source data on a very simple grid
            >>> srcLon =     [ [-88.2 , -88.2  ], 
            ...                [-87.5 , -87.5  ] ]
            >>> 
            >>> srcLat =     [ [ 43.5  , 44.1  ],
            ...                [ 43.5  , 44.1  ] ]
            >>> 
            >>> data   =     [ [  3    ,  1    ],
            ...                [  4    ,  2    ] ]
            >>> 
            >>> # coarser destination grid where we want data
            >>> destLon =     [ [-92. , -92  , -92 , -92  ], 
            ...                 [-90. , -90  , -90 , -90  ], 
            ...                 [-88. , -88  , -88 , -88  ], 
            ...                 [-86. , -86  , -86 , -86  ] ]
            >>> 
            >>> destLat =     [ [ 42  ,  44  ,  46 ,  48 ],
            ...                 [ 42  ,  44  ,  46 ,  48 ], 
            ...                 [ 42  ,  44  ,  46 ,  48 ], 
            ...                 [ 42  ,  44  ,  46 ,  48 ] ]
            >>> 
            >>> #instantiate object to handle interpolation
            >>> #All source data points found within 300km of each destination 
            >>> #grid tiles will be averaged together
            >>> projInds = geo_tools.projInds(data_xx=srcLon,  data_yy=srcLat,
            ...                               destLat=destLat, destLon=destLon,
            ...                               smoothRadius=300., missing=-99.)
            >>> 
            >>> #interpolate and smooth data with "project_data"
            >>> interpolated = projInds.project_data(data)
            >>> 
            >>> #output is smoother than data source
            >>> print(interpolated)
            [[-99.         -99.         -99.         -99.        ]
             [  2.66666667   2.5          1.5        -99.        ]
             [  2.5          2.5          2.5        -99.        ]
             [  2.5          2.5          1.5        -99.        ]]




             

    """
    def __init__(self,  data_xx:      Optional[Any]=None, 
                        data_yy:      Optional[Any]=None,
                        srcLon:       Optional[Any]=None,
                        srcLat:       Optional[Any]=None, 
                        destLon:      Optional[Any]=None,
                        destLat:      Optional[Any]=None, 
                        extent:       Optional[Any]=None, 
                        destCrs:      Optional[Any]=None,
                        sourceCrs:    Optional[Any]=None,
                        fig:          Optional[Any]=None,
                        image_res:    Optional[tuple]=(400,400), 
                        extendX:      Optional[Any]=True, 
                        extendY:      Optional[Any]=True, 
                        average:      Optional[Any]=False, 
                        smoothRadius: Optional[Any]=None, 
                        minHits:      Optional[Any]=1, 
                        missing:      Optional[float]=-9999. ):

        from os import linesep as newline
        import warnings
        import numpy as np
        import cartopy.crs as ccrs
        import cartopy.img_transform as cimgt
        import scipy.spatial
        import matplotlib.pyplot as plt
        #local functions
        from ._findNearest     import _findNearest
        from .lat_lon_extend   import lat_lon_extend
        from .rotation_matrix  import rotation_matrix


        #check specification of destinating grid 
        if (destLon is not None) and (destLat is not None):
            #destination lat/lon are provided by user, use those
            destLon = np.asarray(destLon)
            destLat = np.asarray(destLat)

        elif (destCrs is not None) and (extent is not None): 
            #we are projecting data onto an image, get destination grid from Cartopy
            if fig is None:
                dummyFig = plt.figure()
            else:
                dummyFig = fig
            dummyAx = dummyFig.add_axes([0.,0.,1.,1.], projection=destCrs)
            dummyAx.set_extent(extent)
            dummyAx.outline_patch.set_linewidth(0) #thinner axes contour line
            
            #get corners of image in data space
            transform_data_to_axes = dummyAx.transData + dummyAx.transAxes.inverted()
            transform_axes_to_data = transform_data_to_axes.inverted()
            pts = ((0.,0.),(1.,1.))
            pt1, pt2 = transform_axes_to_data.transform(pts)
        
            #get regular grid of pts in projected figure    units of destLon and destLat are in dataspace
            #                                                          nx            ny
            destLon, destLat, extent = cimgt.mesh_projection( destCrs, image_res[0], image_res[1],
                                                          x_extents=[pt1[0],pt2[0]], y_extents=[pt1[1],pt2[1]])

        else: 
            raise ValueError(' The lat/lon of the destination grid must be specified using:'             + newline +
                             '    - Directly through the use of the "destLat" and "destLon" keywords '   + newline +
                             '    - By specifying "destCrs" and the "extent" keywords of a figure being' + newline +
                             '      generated')


        #check specification of input grid
        if (srcLon is not None) and (srcLat is not None):
             #source grid provided by user, use it 
             pass
        elif (data_xx is not None) and (data_yy is not None):
            #old way of providing same info, use those and write a deprecation message
            srcLon = data_xx
            srcLat = data_yy
            warnings.warn('The keywords "data_xx" and "data_yy" are deprecated. ' + newline +
                          'Use keywords "srcLon" and "srcLat" instead ', DeprecationWarning)
        else : 
            raise ValueError(' The lat/lon of the source data mush be provided through the "srcLon" and "srcLat" keywords.')

        
        #insure input coords are numpy arrays
        np_xx = np.asarray(srcLon)
        np_yy = np.asarray(srcLat)
        
        #only necessary for plotting border
        #get lat/lon at the border of the domain        Note the half dist in the call to lat_lon_extend
        borderLat2d = np.zeros(np.asarray(np_yy.shape)+2)
        borderLon2d = np.zeros(np.asarray(np_xx.shape)+2)
        #center contains data lat/lon
        borderLat2d[1:-1,1:-1] = np_yy
        borderLon2d[1:-1,1:-1] = np_xx
        #extend left side
        borderLon2d[1:-1,0], borderLat2d[1:-1,0] = lat_lon_extend(np_xx[:,1],np_yy[:,1],np_xx[:,0],np_yy[:,0], halfDist=True)
        #extend right side
        borderLon2d[1:-1,-1], borderLat2d[1:-1,-1] = lat_lon_extend(np_xx[:,-2],np_yy[:,-2],np_xx[:,-1],np_yy[:,-1], halfDist=True)
        #extend top
        borderLon2d[0,:], borderLat2d[0,:] = lat_lon_extend(borderLon2d[2,:],borderLat2d[2,:],borderLon2d[1,:],borderLat2d[1,:], halfDist=True)
        #extend bottom
        borderLon2d[-1,:], borderLat2d[-1,:] = lat_lon_extend(borderLon2d[-3,:],borderLat2d[-3,:],borderLon2d[-2,:],borderLat2d[-2,:], halfDist=True)
        #we are only interested in the extendded values
        left   = np.flip(borderLon2d[1:-1,0].flatten())
        top    =         borderLon2d[0,:].flatten()
        right  =         borderLon2d[1:-1,-1].flatten()
        bottom = np.flip(borderLon2d[-1,:]).flatten()
        borderLons = np.concatenate([left,top,right,bottom,np.array(left[0],ndmin=1)])  #last entry is first for a complete polygon
        left   = np.flip(borderLat2d[1:-1,0].flatten())
        top    =         borderLat2d[0,:].flatten()
        right  =         borderLat2d[1:-1,-1].flatten()
        bottom = np.flip(borderLat2d[-1,:]).flatten()
        borderLats = np.concatenate([left,top,right,bottom,np.array(left[0],ndmin=1)])
        
        #find proj_ind using findNearest
        if smoothRadius is not None:
            #when using a smoothing radius, the tree will be used in project_data
            kdtree, dest_xyz = _findNearest(srcLon, srcLat, destLon, destLat,
                                            smoothRadius=smoothRadius, 
                                            extendX=False, extendY=False, missing=missing, sourceCrs=sourceCrs, destCrs=destCrs)
        elif average:
            #reverse order since we will likely encounter need multiple data pts per destination grid tile
            proj_ind = _findNearest(destLon, destLat, srcLon, srcLat, 
                                    extendX=False, extendY=False, missing=missing, sourceCrs=sourceCrs, destCrs=destCrs)
        else:
            #regular nearest neighbot search
            proj_ind = _findNearest(srcLon, srcLat, destLon, destLat, 
                                    extendX=extendX, extendY=extendY, missing=missing, sourceCrs=sourceCrs, destCrs=destCrs)
        
        #save needed data
        #data nedded for projecting data
        self.data_shape = np_xx.shape
        self.destShape = destLon.shape   
        self.minHits = minHits
        self.missing = missing

        if smoothRadius is not None:
            #crs space in meters
            self.smoothRadius_m = smoothRadius * 1e3
            self.kdtree = kdtree
            self.dest_xyz = dest_xyz
            self.average = True     #uses the averaging mechanism during smoothing
            self.destLon = destLon  #need those in project_data when smoothing
            self.destLat = destLat
        else:
            self.smoothRadius_m = None
            self.proj_ind  = proj_ind
            self.average   = average
        
        #data nedded for plotting border
        self.borderLons = borderLons
        self.borderLats = borderLats
        
        #cleanup
        if destCrs:
            dummyAx.remove()
            plt.close(dummyFig)



    def project_data(self, data:Any, 
                           weights:Optional[Any]  = None,
                           missingV:Optional[float]= -9999. ):
        """ Project data into geoAxes space

            Args:
                data:       (array like), data values to be projected. 
                            Must have the same dimension as the lat/lon coordinates used to 
                            instantiate the class.
                weights:    (array like), weights to be applied during averaging 
                            (see average and smoothRadius keyword in projInds)
                missingV:   Value in input data that will be neglected during the averaging process
                            Has no impact unless *average* or *smoothRadius* are used in class 
                            instantiation.

            Returns:
                A numpy array of the same shape as destination grid used to instantiate the class

        """
        import numpy as np

        #ensure numpy
        np_data = np.asarray(data)

        if self.smoothRadius_m is None :
            #make sure data is of the right shape
            if (np_data.shape != self.data_shape) :
                raise ValueError("data is not of the same shape as the coordinates used to initate projection object")
        else:
            #there are no constraints on data shape if smoothing is used during interpolation
            pass

        #flatten data
        data_flat = np_data.ravel()

        #fill it where needed
        if self.average :
            #init matrices
            accumulator = np.zeros(self.destShape).ravel()
            denom       = np.zeros(self.destShape).ravel()
            averaged    =  np.full(self.destShape,self.missing).ravel()
            nHits       = np.zeros(self.destShape, dtype='int32').ravel() 
            #init/check weights matrice 
            if weights is None:
                #by default all data pts have equal weights = 1.
                weights_np = np.ones(np_data.shape).ravel()
            else:
                #weights were provided
                weights_np = np.asarray(weights)
                if (weights_np.shape != np_data.shape) :
                    raise ValueError("Weights should have the same shape as data")
            weights_flat = weights_np.ravel()

            if self.smoothRadius_m is not None:
                #smooth all data found within distance specified by smoothRadius
                for ind, xyz in enumerate(self.dest_xyz):

                    good_pts = self.kdtree.query_ball_point(xyz, self.smoothRadius_m)
                    thisData    = data_flat[good_pts]
                    (validPts,) = np.asarray((thisData - missingV) > 1e-3).nonzero()
                    if validPts.size > 0 :
                        thisData    = thisData[validPts]
                        thisWeights = weights_flat[np.asarray(good_pts)[validPts]]
                        accumulator[ind] = np.sum(thisWeights*thisData)
                        denom[ind]       = np.sum(thisWeights)
                        nHits[ind]       = validPts.size

                
            else:
                #average out all input falling within output grid tile
                (good_pts,) = np.asarray( np.abs(self.proj_ind - self.missing) >= 1e-3 ).nonzero()
                if good_pts.size > 0 :
                    in_inds = self.proj_ind[good_pts]
                    ii = np.arange(self.proj_ind.size)
                    out_inds = ii[good_pts]
                    for inPt, outPt in zip(in_inds, out_inds):
                        accumulator[inPt] += weights_flat[outPt]*data_flat[outPt]
                        denom[inPt]       += weights_flat[outPt]
                        nHits[inPt]       += 1

            #the averaging part
            (hits,) = np.logical_and(denom > 0., nHits >= self.minHits).nonzero()
            if hits.size > 0 :
                averaged[hits] = accumulator[hits]/denom[hits]

            #output is a 2D array
            proj_data = np.reshape(averaged, self.destShape)

        else:

            #init output array
            proj_data = np.full(self.destShape,self.missing)
            (good_pts,) = np.asarray( (self.proj_ind >= 0) ).nonzero()
            if good_pts.size != 0:
                proj_data.ravel()[good_pts] = data_flat[self.proj_ind[good_pts]]

        return proj_data



    def plotBorder(self, ax:Any=None, 
                         crs:Optional[Any]=None, 
                         linewidth:Optional[float]=0.5,
                         zorder:Optional[int]=3,
                         maskOutside:Optional[bool]=False):
        """ Plot border of a more or less regularly gridded domain

            Optionally, mask everything that is outside the domain for simpler
            figures. 
            
            Args:
                ax:           Instance of a cartopy geoAxes where border is to be plotted
                crs:          Cartopy crs of the data coordinates. 
                              If None, a Geodetic crs is used for using latitude/longitude coordinates.
                linewidth:    Width of border being plotted
                maskOutside:  If True, everything outside the domain will be hidden
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
        if self.smoothRadius_m is None:
            if maskOutside :
                #get corners of image in data space
                transform_data_to_axes = ax.transData + ax.transAxes.inverted()
                transform_axes_to_data = transform_data_to_axes.inverted()
                pts = ((0.,0.),(1.,1.))
                pt1, pt2 = transform_axes_to_data.transform(pts)
                extent_data_space = [pt1[0],pt2[0],pt1[1],pt2[1]]
            
                rgb   = np.full(self.destShape+(3,),1.,dtype='float32')
                alpha = np.full(self.destShape+(1,),0.,dtype='float32')
                #set transparent inside of the domain, opaque outside
                outside_pts = np.asarray( (self.proj_ind < 0) ).nonzero()
                if outside_pts[0].size != 0:
                    alpha.ravel()[outside_pts] = 1.

                rgba = np.concatenate([rgb,alpha],axis=2)

                #no lines on the contour of the axes
                ax.outline_patch.set_linewidth(0.0)

                #plot mask
                ax.imshow(rgba, axes=ax, interpolation='nearest',extent=extent_data_space,zorder=2)

                #white outline around border to mask border pixel shown by some renderers
                xx = [0., 1, 1, 0, 0]
                yy = [0., 0, 1, 1, 0]
                ax.plot(xx, yy, color='white', linewidth=1., transform=ax.transAxes, zorder=4,clip_on=False)
        else :
            if maskOutside :
                warnings.warn('The keywords maskOutside is not compatible with smoothRadius, it is now ignored')




        #plot border
        ax.plot(self.borderLons, self.borderLats,
                         color='.1', linewidth=linewidth, transform=proj_ll,zorder=zorder)




    def main():
        pass

    if __name__ == "__main__":
        main()




