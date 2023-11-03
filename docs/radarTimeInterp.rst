
Time interpolation using nowcasting
----------------------------------------------

Sometimes, you need precipitation rates or reflectivity at a higher 
temporal resolution than the available data. 
Simple time interpolation between two fields will not do a goot job because of the 
precipitation displacement. 

As a solution to this, the module `obs_process` provides a nowcast 
interpolation functionality. The basic idea is that data at intermediate timesteps, 
data will be estimated as a weighted average of the forward advection of the 
data before and backward advection of the data after. 

Lets start with the required imports and directory setup

    >>> import os
    >>> import datetime
    >>> import matplotlib.pyplot as plt
    >>> import cartopy.crs as ccrs
    >>> import cartopy.feature as cfeature
    >>> import domutils
    >>> import domutils.legs as legs
    >>> import domutils.geo_tools as geo_tools
    >>> import domutils.radar_tools as radar_tools
    >>> import domcmc.fst_tools as fst_tools
    >>> 
    >>> #setting up directories
    >>> domutils_dir = os.path.dirname(domutils.__file__)
    >>> package_dir  = os.path.dirname(domutils_dir)
    >>> test_data_dir = package_dir+'/test_data/'
    >>> test_results_dir = package_dir+'/test_results/'
    >>> if not os.path.isdir(test_results_dir):
    ...     os.makedirs(test_results_dir)
    >>> log_dir = './logs'
    >>> if not os.path.isdir(log_dir):
    ...     os.makedirs(log_dir)


`obs_process` is a python script callable from the shell such as:

    .. code-block:: bash

       #process data with time interpolation
       python -m domutils.radar_tools.obs_process    \
                 --input_t0         202206150800     \
                 --input_tf         202206160000     \
                 --input_dt         10               \
                 --output_t0        202206150900     \
                 --output_tf        202206160000     \
                 --output_dt        1                \
                 --t_interp_method  'nowcast'        \
                 ...

However, for this example we will be running directly from Python
with arguments provided by the attributes of a simple object. 

  >>> # a class that mimics the output of argparse
  >>> class ArgsClass():
  ...     input_t0                 = '202205212100'
  ...     input_tf                 = '202205212200'
  ...     input_dt                 = 10
  ...     output_t0                = '202205212130'
  ...     output_tf                = '202205212140'
  ...     output_dt                = 1
  ...     output_file_format       = 'fst'
  ...     complete_dataset         = 'False'
  ...     t_interp_method          = 'nowcast'
  ...     input_data_dir           = test_data_dir+'/odimh5_radar_composites/'
  ...     input_file_struc         = '%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
  ...     h5_latlon_file           = test_data_dir+'radar_continental_2.5km_2882x2032.pickle'
  ...     sample_pr_file           = test_data_dir+'hrdps_5p1_prp0.fst'
  ...     ncores                   = 1
  ...     median_filt              = 3
  ...     smooth_radius            = 4
  ...     output_dir               = test_results_dir+'/obs_process_t_interp/'
  ...     processed_file_struc     = '%Y%m%d%H%M.fst'
  ...     tinterpolated_file_struc = '%Y%m%d%H.fst'
  ...     log_level                = 'WARNING'

The processing of observations and time interpolation is done 
in one simple function call.

    >>> # all the arguments are attributes of the args object
    >>> args = ArgsClass()
    >>>
    >>> # radar_tools.obs_process(args)

Lets make an image showing the source data, the processed data 
and the time-interpolated data.

This will be easier by first defining a function for plotting each individual panels

    >>> def plot_panel(valid_date, data_path, data_recipe,
    ...                fig, ax_pos, title, 
    ...                proj_aea, map_extent,
    ...                proj_obj, colormap):
    ...     # function for plotting a panel of reflectivity values
    ...
    ...     ax = fig.add_axes(ax_pos, projection=proj_aea)
    ...     ax.set_extent(map_extent)
    ...     dum = ax.annotate(title, size=20,
    ...                       xy=(.02, .9), xycoords='axes fraction',
    ...                       bbox=dict(boxstyle="round", fc='white', ec='white'))
    ...
    ...     # read data
    ...     dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
    ...                                              valid_date=valid_date,
    ...                                              data_path=data_path,
    ...                                              data_recipe=data_recipe)
    ...
    ...     # projection from data space to image space
    ...     projected_data = proj_obj.project_data(dat_dict['precip_rate'])
    ...
    ...     # plot data & palette
    ...     colormap.plot_data(ax=ax, data=projected_data,
    ...                        palette=None)
    ...                        
    ...
    ...     # add political boundaries
    ...     ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.5, edgecolor='0.2')
    ...
    

    >>> #pixel density of image to plot
    >>> ratio = 1.
    >>> hpix = 600.       #number of horizontal pixels
    >>> vpix = ratio*hpix #number of vertical pixels
    >>> img_res = (int(hpix),int(vpix))
    >>>
    >>> #size of image to plot
    >>> fig_w = 15.                    #size of figure
    >>> fig_h = 7.                     #size of figure
    >>> rec_w = 2./fig_w               #size of axes
    >>> rec_h = ratio*(rec_w*fig_w)/fig_h #size of axes
    >>> sp_w = .1/fig_w                #space between panels
    >>> sp_h = .1/fig_h                #space between panels
    >>>
    >>> # color mapping object
    >>> range_arr = [.1,1.,5.,10.,25.,50.,100.]
    >>> missing = -9999.
    >>> colormap = legs.PalObj(range_arr=range_arr,
    ...                        n_col=6,
    ...                        over_high='extend', under_low='white',
    ...                        excep_val=missing, 
    ...                        excep_col='grey_200')
    >>> pal_units = 'mm/h'
    >>> pal_format = '{:5.1f}'
    >>> pal_equal = False
    >>>
    >>> #setup cartopy projection
    >>> ##250km around Blainville radar
    >>> pole_latitude=90.
    >>> pole_longitude=0.
    >>> lat_0 = 46.
    >>> delta_lat = 2.18/2.
    >>> lon_0 = -73.75 
    >>> delta_lon = 3.12/2.
    >>> map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    >>> proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    >>>
    >>> # get lat/lon of input data from one of the h5 files 
    >>> dum_h5_file = test_data_dir+'/odimh5_radar_composites/2022/05/21/qcomp_202205212100.h5'
    >>> input_ll    = radar_tools.read_h5_composite(dum_h5_file, latlon=True)
    >>> input_lats  = input_ll['latitudes']
    >>> input_lons  = input_ll['longitudes']
    >>>
    >>> # get lat/lon of output data 
    >>> output_ll = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)
    >>> output_lats = output_ll['lat']
    >>> output_lons = output_ll['lon']
    >>>
    >>> # instantiate projection object for input data
    >>> input_proj_obj = geo_tools.ProjInds(src_lon=input_lons, src_lat=input_lats,
    ...                                     extent=map_extent, dest_crs=proj_aea, image_res=img_res)
    >>>
    >>> # instantiate projection object for output data
    >>> output_proj_obj = geo_tools.ProjInds(src_lon=output_lons, src_lat=output_lats,
    ...                                      extent=map_extent, dest_crs=proj_aea, image_res=img_res)
    >>>
    >>> ##instantiate figure
    >>> fig = plt.figure(figsize=(fig_w,fig_h))
    >>>
    >>> # plot source data at 10 min intervals
    >>> x0 = sp_w
    >>> y0 = 2.*sp_h + rec_h
    >>> ax_pos = [x0, y0, rec_w, rec_h]
    >>> valid_date = datetime.datetime(2022,5,21,21,30)
    >>> title = 't0'
    >>> plot_panel(valid_date, args.input_data_dir, args.input_file_struc,
    ...            fig, ax_pos, title, 
    ...            proj_aea, map_extent,
    ...            input_proj_obj, colormap)
    >>>
    >>> x0 = 5.*sp_w + 5.*rec_w
    >>> y0 = 2.*sp_h + rec_h
    >>> ax_pos = [x0, y0, rec_w, rec_h]
    >>> valid_date = datetime.datetime(2022,5,21,21,40)
    >>> title = 't0+10min'
    >>> plot_panel(valid_date, args.input_data_dir, args.input_file_struc,
    ...            fig, ax_pos, title, 
    ...            proj_aea, map_extent,
    ...            input_proj_obj, colormap)
    >>>
    >>> for tt, dt in enumerate([2,4,6,8,10,12]):
    ...     # processed observations at equivalent time
    ...     x0 = sp_w + tt*(sp_w +rec_w)
    ...     y0 = sp_h 
    ...     ax_pos = [x0, y0, rec_w, rec_h]
    ...     valid_date = datetime.datetime(2022,5,21,21,30+int(2.*tt))
    ...     print(valid_date)
    ...     title = f't0+{int(2.*tt)}min'
    ...     plot_panel(valid_date, args.output_dir, args.tinterpolated_file_struc,
    ...                fig, ax_pos, title, 
    ...                proj_aea, map_extent,
    ...                output_proj_obj, colormap)
    >>>
    >>> ##save output
    >>> fig_name = test_data_dir+'_static/time_interpol_demo.svg'
    >>> plt.savefig(fig_name,dpi=400)
    >>> plt.close(fig)
