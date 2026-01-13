"""
A class for interpolating any data to any grids with Cartopy.

In addition to interpolation, this class is usefull to display geographical data.
Since projection mappings need to be defined only once for a given dataset/display combination, 
multi-pannels figures can be made efficiently.

Most of the action happens through the class :class:`ProjInds`.

The following figure illustrates the convention for storring data in numpy arrays. 
It is assumed that the first index (rows) represents x-y direction (longitudes):

.. image:: _static/illustrative/xy.svg
                :align: center


"""

from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def normalize_longitudes(lons):
    """
    Normalizes an array of longitudes to the range [-180, 180).
    """
    import numpy as np

    

    return np.mod(np.asarray(lons) + 180, 360) - 180


def geographic_extent_to_rotated(extent_geo, rotated_crs):
    """
    Convert a geographic (PlateCarree) extent into rotated-pole coordinates.

    Parameters
    ----------
    extent_geo : list or tuple
        [lon_min, lon_max, lat_min, lat_max] in true geographic coords.
    rotated_crs : cartopy.crs.RotatedPole
        The rotated pole CRS you want to convert into.

    Returns
    -------
    extent_rot : list
        [rot_lon_min, rot_lon_max, rot_lat_min, rot_lat_max] in rotated coords.
    """

    import numpy as np
    import cartopy.crs as ccrs

    lon_min, lon_max, lat_min, lat_max = extent_geo
    
    # Four corner points of the geographic box
    geo_corners = np.array([
        [lon_min, lat_min],
        [lon_min, lat_max],
        [lon_max, lat_min],
        [lon_max, lat_max],
    ])

    pc = ccrs.PlateCarree()

    # Transform to rotated CRS
    rot_corners = rotated_crs.transform_points(
        pc, geo_corners[:, 0], geo_corners[:, 1]
    )

    rot_lon = rot_corners[:, 0]
    rot_lat = rot_corners[:, 1]

    return [
        float(rot_lon.min()),
        float(rot_lon.max()),
        float(rot_lat.min()),
        float(rot_lat.max()),
    ]


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
                           wide (i.e. longitude in the case of geo_axes) by 200 pixels high
                           (i.e. latitude in the case of geo_axes).
            extend_x:      Set to True (default) when the destination grid is larger than the source grid. 
                           This option allows to mark no data points with Missing rather than extrapolating.
                           Set to False for global grids.
            extend_y:      Same as extend_x but in the Y direction.
            average:       (bool) When true, all pts of a source grid falling within a destination
                           grid pt will be averaged. Usefull to display/interpolate hi resolution
                           data to a coarser grid.
                           Weighted averages can be obtained by providing weights to the *project_data*
                           method.
            smooth_radius: Boxcar averaging with a circular area of a given radius given in kilometer.
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


            .. literalinclude:: ../domutils/geo_tools/tests/test_geo_tools.py
               :language: python
               :start-after: DOCS:simple_projinds_example_begins
               :end-before: DOCS:simple_projinds_example_ends

            .. image:: _static/test_geo_tools/test_projinds_simple_example.svg
                :align: center


            Example showing how ProjInds can also be used for nearest neighbor interpolation

            .. literalinclude:: ../domutils/geo_tools/tests/test_geo_tools.py
               :language: python
               :start-after: DOCS:simple_nearest_neighbor_interpolation_begins
               :end-before: DOCS:simple_nearest_neighbor_interpolation_ends

            Interpolation to coarser grids can be done with the *nearest* keyword. 
            With this flag, all high-resoution data falling within a tile of the 
            destination grid will be averaged together. 
            Border detection works as in the example above.

            .. literalinclude:: ../domutils/geo_tools/tests/test_geo_tools.py
               :language: python
               :start-after: DOCS:averaging_interpolation_begins
               :end-before: DOCS:averaging_interpolation_ends


            Sometimes, it is useful to smooth data during the interpolation process.
            For example when comparing radar measurement against model output, smoothing
            can be used to remove the small scales present in the observations but that
            the model cannot represent. 
            
            Use the *smoooth_radius* to average all source data point within a certain radius
            (in km) of the destination grid tiles. 

            .. literalinclude:: ../domutils/geo_tools/tests/test_geo_tools.py
               :language: python
               :start-after: DOCS:smooth_radius_interpolation_begins
               :end-before: DOCS:smooth_radius_interpolation_ends

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

        from packaging import version
        from os import linesep as newline
        import warnings
        import numpy as np
        import cartopy
        import cartopy.img_transform as cimgt
        import matplotlib.pyplot as plt
        #local functions
        from ._find_nearest     import _find_nearest
        from .lat_lon_extend   import lat_lon_extend


        #check specification of destination grid
        if (dest_lon is not None) and (dest_lat is not None):
            #destination lat/lon are provided by user, use those
            dest_lon = normalize_longitudes(dest_lon)
            dest_lat = np.asarray(dest_lat)
            rotated_extent = None

        elif (dest_crs is not None) :
            # we are projecting data onto a given projection extent in cartopy
            
            if extent is not None:
                # we assume lat/lon extent
                # check that values passed are compatible
                # this expression works even if extent is passed as a tuple
                extent = (*normalize_longitudes(extent[:2]), *extent[2:])

                if ((extent[0] > 180.) or (extent[0] < -180.) or
                    (extent[1] > 180.) or (extent[1] < -180.) or
                    (extent[2] >  90.) or (extent[2] <  -90.) or
                    (extent[3] >  90.) or (extent[3] <  -90.)):
                    raise ValueError(f'We assume lat/lon extent. The values provided are not compatible: {extent}')

                # get extent in the provided crs
                rotated_extent = geographic_extent_to_rotated(extent, dest_crs)

                xx = np.linspace(rotated_extent[0], rotated_extent[1], image_res[0])
                yy = np.linspace(rotated_extent[2], rotated_extent[3], image_res[1])
                dest_xx, dest_yy = np.meshgrid(xx, yy)
            else:
                #use default extent for this projection
                rotated_extent = None
                dest_xx, dest_yy, extent = cimgt.mesh_projection(dest_crs, int(image_res[0]), int(image_res[1]))

            #Image returned by Cartopy is of shape (ny,nx) so that nx corresponds to S-N
            # with orientation
            #   S
            #E     W
            #   N                   ...go figure...
            #
            #For the result to work with imshow origin=upper + extent obtained from get_extent, We want
            #   N
            #E     W
            #   S   
            #
            #the following transformation does that. 
            dest_xx = np.flipud(dest_xx)
            dest_yy = np.flipud(dest_yy)

            #get lat/lon from data coords
            proj_ll = cartopy.crs.PlateCarree()
            out = proj_ll.transform_points(dest_crs, dest_xx, dest_yy)
            dest_lon = out[:,:,0]
            dest_lat = out[:,:,1]

            ##took me a long while to figure the  nx,ny -> ny,nx + transpose/rotation above 
            ##lets keep debugging code around for a little while...  
            #print('before')
            #print(dest_lon.shape)
            #print(dest_lat.shape)
            #print('0,0', dest_lon[0,0] ,  dest_lat[0,0])
            #print('0,n', dest_lon[0,-1],  dest_lat[0,-1])
            #print('m,0', dest_lon[-1,0],  dest_lat[-1,0])
            #print('m,n', dest_lon[-1,-1] ,dest_lat[-1,-1])
            #print('after')
            #print(dest_lon.shape)
            #print(dest_lat.shape)
            #print('0,0', dest_lon[0,0] ,  dest_lat[0,0])
            #print('0,n', dest_lon[0,-1],  dest_lat[0,-1])
            #print('m,0', dest_lon[-1,0],  dest_lat[-1,0])
            #print('m,n', dest_lon[-1,-1] ,dest_lat[-1,-1])

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
        src_lon = normalize_longitudes(src_lon)
        src_lat = np.asarray(src_lat)
        
        #only necessary for plotting border
        # borders make no sense for continuous grids such as global grids
        # set either extend_x or extend_y = False to skip computation of borders
        if extend_x and extend_y:
            #get lat/lon at the border of the domain        Note the half dist in the call to lat_lon_extend
            border_lat2d = np.zeros(np.asarray(src_lat.shape)+2)
            border_lon2d = np.zeros(np.asarray(src_lon.shape)+2)
            #center contains data lat/lon
            border_lat2d[1:-1,1:-1] = src_lat
            border_lon2d[1:-1,1:-1] = src_lon
            #extend left side
            border_lon2d[1:-1,0], border_lat2d[1:-1,0] = lat_lon_extend(src_lon[:,1],src_lat[:,1],src_lon[:,0],src_lat[:,0], half_dist=True)
            #extend right side
            border_lon2d[1:-1,-1], border_lat2d[1:-1,-1] = lat_lon_extend(src_lon[:,-2],src_lat[:,-2],src_lon[:,-1],src_lat[:,-1], half_dist=True)
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

            radius_earth = 6371. # km
            smooth_radius_unit = smooth_radius / radius_earth

            #when using a smoothing radius, the tree will be used in project_data
            kdtree, dest_xyz = _find_nearest(src_lon, src_lat, dest_lon, dest_lat,
                                             smooth_radius=smooth_radius_unit,
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
        self.data_shape = src_lon.shape
        self.dest_shape = dest_lon.shape
        self.min_hits = min_hits
        self.missing = missing
        self.rotated_extent = rotated_extent

        if smooth_radius is not None:
            # distances along unit sphere
            self.smooth_radius_unit = smooth_radius_unit
            self.kdtree = kdtree
            self.dest_xyz = dest_xyz
            self.average = True     #uses the averaging mechanism during smoothing
            self.destLon = dest_lon  #need those in project_data when smoothing
            self.destLat = dest_lat
        else:
            self.smooth_radius_unit = None
            self.proj_ind  = proj_ind
            self.average   = average
        
        #data needed for plotting border
        self.border_lons = border_lons
        self.border_lats = border_lats



    def project_data(self,
                     data:Any,
                     weights:Optional[Any]  = None,
                     output_avg_weights:Optional[bool] = False,
                     missing_v:Optional[float]= -9999.):
        """ Project data into geoAxes space

            Args:
                data:       (array like), data values to be projected. 
                            Must have the same dimension as the lat/lon coordinates used to 
                            instantiate the class.
                weights:    (array like), weights to be applied during averaging 
                            (see average and smooth_radius keyword in ProjInds)
                output_avg_weights: 
                            If True, projected_weights will be outputed along with projected_data
                            "Averaged" and "smooth_radius" interpolation can take a long time on large 
                            grids. 
                            This option is useful to get radar data + quality index interpolated 
                            using one call to project_data instead of two halving computation time.
                            Not available for nearest-neighbor interpolation which is already quite fast anyway.
                missing_v:  Value in input data that will be neglected during the averaging process
                            Has no impact unless *average* or *smooth_radius* are used in class
                            instantiation.

            Returns:
                projected_data  A numpy array of the same shape as destination grid used to instantiate the class

                if output_avg_weights=True, returns:

                    projected_data, projected_weights


        """
        import numpy as np

        #ensure numpy
        np_data = np.asarray(data)

        if self.smooth_radius_unit is None :
            #make sure data is of the right shape
            if (np_data.shape != self.data_shape) :
                raise ValueError((f"data is not of the same shape as the coordinates used "  +
                                  f"to initiate projection object; received {np_data.shape} "+
                                  f"and was expecting {self.data_shape}"))
        else:
            #there are no constraints on data shape if smoothing is used during interpolation
            pass

        #flatten data
        data_flat = np_data.ravel()

        #fill it where needed
        if self.average :
            #init matrices
            data_accumulator    = np.zeros(self.dest_shape).ravel()
            weights_accumulator = np.zeros(self.dest_shape).ravel()
            denom               = np.zeros(self.dest_shape).ravel()
            averaged_data       = np.full(self.dest_shape, self.missing).ravel()
            averaged_weights    = np.zeros(self.dest_shape).ravel()
            n_hits              = np.zeros(self.dest_shape, dtype='int32').ravel()
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

            if self.smooth_radius_unit is not None:
                #smooth all data found within distance specified by smooth_radius
                #
                #  Note for future optimisation work
                #  for HRDPS grid with smooth_radius=3,
                #  kdtree call takes ~15s while loop runs in ~60s

                #KDtree call
                good_pts_list = self.kdtree.query_ball_point(self.dest_xyz, self.smooth_radius_unit)
                for ind, good_pts in enumerate(good_pts_list):

                    this_data    = data_flat[good_pts]
                    (valid_pts,) = np.asarray((this_data - missing_v) > 1e-3).nonzero()
                    if valid_pts.size > 0 :
                        this_data   = this_data[valid_pts]
                        this_weights     = weights_flat[np.asarray(good_pts)[valid_pts]]
                        data_accumulator[ind]    = np.sum(this_weights*this_data)
                        weights_accumulator[ind] = np.sum(this_weights*this_weights)
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
                        data_accumulator[in_pt]    += weights_flat[out_pt]*data_flat[out_pt]
                        weights_accumulator[in_pt] += weights_flat[out_pt]*weights_flat[out_pt]
                        denom[in_pt]       += weights_flat[out_pt]
                        n_hits[in_pt]      += 1

            #the averaging part
            (hits,) = np.logical_and(denom > 0., n_hits >= self.min_hits).nonzero()
            if hits.size > 0 :
                averaged_data[hits]    =    data_accumulator[hits]/denom[hits]
                averaged_weights[hits] = weights_accumulator[hits]/denom[hits]

            #output are 2D arrays
            proj_data    = np.reshape(averaged_data,    self.dest_shape)
            proj_weights = np.reshape(averaged_weights, self.dest_shape)

        else:
            if output_avg_weights:
                raise ValueError('Keyword output_avg_weights=True is not compatible with nearest neighbor interpolation') 

            #init output array
            proj_data = np.full(self.dest_shape, self.missing)
            (good_pts,) = np.asarray( (self.proj_ind >= 0) ).nonzero()
            if good_pts.size != 0:
                proj_data.ravel()[good_pts] = data_flat[self.proj_ind[good_pts]]

        if output_avg_weights:
            return proj_data, proj_weights
        else:
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
        from packaging import version
        import cartopy
        import cartopy.crs as ccrs
        import warnings

        if ax is None:
            raise ValueError('The "ax" keyword must be provided')

        #clip pixels outside of domain
        if self.smooth_radius_unit is None:
            if mask_outside :
                #get corners of image in data space
                extent_data_space = ax.get_extent()
            
                rgb   = np.full(self.dest_shape + (3,), 1., dtype='float32')
                alpha = np.full(self.dest_shape + (1,), 0., dtype='float32')
                #set transparent inside of the domain, opaque outside
                outside_pts = np.asarray( (self.proj_ind < 0) ).nonzero()
                if outside_pts[0].size != 0:
                    alpha.ravel()[outside_pts] = 1.

                rgba = np.concatenate([rgb,alpha],axis=2)

                #no lines on the contour of the axes
                if version.parse(cartopy.__version__) >= version.parse("0.18.0"):
                    ax.spines['geo'].set_linewidth(0)
                else:
                    ax.outline_patch.set_linewidth(0) 

                #plot mask
                ax.imshow(rgba, axes=ax, interpolation='nearest', 
                          origin='upper', extent=extent_data_space, zorder=2)

                #white outline around border to mask border pixel shown by some renderers
                xx = [0., 1, 1, 0, 0]
                yy = [0., 0, 1, 1, 0]
                ax.plot(xx, yy, color='white', linewidth=1., transform=ax.transAxes, zorder=4,clip_on=False)
        else :
            if mask_outside :
                warnings.warn('The keywords mask_outside is not compatible with smooth_radius, it is now ignored')




        #plot border
        ax.plot(self.border_lons, self.border_lats,
                color='.1', linewidth=linewidth, transform=ccrs.PlateCarree(), zorder=zorder)




    def main():
        pass

    if __name__ == "__main__":
        main()




