def plot_components():
    """ This test runs obs_process and generates images from the output files

    The docs is also copied and shown as an example in the documentation

    As such the purpose of this test is not so much to test the code but to make 
    sure that the documentation stays up to date. 
    """

    # DOCS:setup_begins
    import os
    import datetime
    import subprocess
    import glob
    import shutil
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import dask
    from dask.distributed import Client, LocalCluster
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools
    import domutils.radar_tools as radar_tools
    import domcmc.fst_tools as fst_tools
    import domutils._py_tools as py_tools
    

    # DOCS:function_definition_begins
    def plot_panel(data,
                   fig, ax_pos, title, 
                   proj_aea, 
                   proj_obj, colormap, 
                   plot_palette=None, 
                   pal_units=None, 
                   show_artefacts=False):
    
        ax = fig.add_axes(ax_pos, projection=proj_aea)
        ax.set_extent(proj_obj.rotated_extent, crs=proj_aea)
        dum = ax.annotate(title, size=32,
                          xy=(.022, .85), xycoords='axes fraction',
                          bbox=dict(boxstyle="round", fc='white', ec='white'))
    
        # projection from data space to image space
        projected_data = proj_obj.project_data(data)
    
        # plot data & palette
        colormap.plot_data(ax=ax, data=projected_data,
                           palette=plot_palette, 
                           pal_units=pal_units, pal_format='{:5.1f}', 
                           equal_legs=True)
    
        # add political boundaries
        ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.5, edgecolor='0.2')
    
        # show artefacts in accumulation plots
        if show_artefacts:
            ax2 = fig.add_axes(ax_pos)
            ax2.set_xlim((0.,1.))
            ax2.set_ylim((0.,1.))
            ax2.patch.set_alpha(0.0)
            ax2.set_axis_off()
            xpos = np.linspace(0.24, 0.40, 5)
            ypos = np.linspace(0.75, 0.85, 5)
            for x0, y0, dx in [(xx,yy,.1) for xx, yy in zip(xpos, ypos)]:
                ax2.arrow(x0, y0, dx, -.03,
                          width=0.015, facecolor='red', edgecolor='black', 
                          head_width=3*0.01, linewidth=2.)
     
    # DOCS:function_definition_ends

    # DOCS:figure_setup_begins
    dpi = 400
    mpl.rcParams.update({
        'font.family': 'Latin Modern Roman',
        'font.size': 32,
        'axes.titlesize': 32,
        'axes.labelsize': 32,
        'xtick.labelsize': 30,
        'ytick.labelsize': 30,
        'legend.fontsize': 30,
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        })
    #pixel density of each panel
    ratio = 1.
    hpix = 1200.      #number of horizontal pixels
    vpix = ratio*hpix #number of vertical pixels
    img_res = (int(hpix),int(vpix))
    
    #size of image to plot
    fig_w = 52.                    #size of figure
    fig_h = 15.7                   #size of figure
    rec_w = 7./fig_w               #size of axes
    rec_h = ratio*(rec_w*fig_w)/fig_h #size of axes
    sp_w = .5/fig_w                #space between panel and border
    sp_m = 2.2/fig_w               #space between panels
    sp_h = .5/fig_h                #space between panels
    
    # color mapping object
    range_arr = [.1,1.,5.,10.,25.,50.,100.]
    missing = -9999.
    # colormap object for precip rates
    pr_colormap = legs.PalObj(range_arr=range_arr,
                              n_col=6,
                              over_high='extend', under_low='white',
                              excep_val=missing, 
                              excep_col='grey_200')
    # colormap for QI index
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[255,227,215],[205,144, 73]],  #pale/dark brown
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    qi_colormap = legs.PalObj(range_arr=[0., 1.],
                              dark_pos='high',
                              color_arr=pastel,
                              excep_val=[missing,0.],
                              excep_col=['grey_220','white'])
    
    #setup cartopy projection
    ###250km around Blainville radar
    #pole_latitude=90.
    #pole_longitude=0.
    #lat_0 = 46.
    #delta_lat = 2.18/2.
    #lon_0 = -73.75 
    #delta_lon = 3.12/2.
    #map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    #proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)

    # 300x300 Minnesota/Wisconsin
    pole_latitude=35.7
    pole_longitude=65.5
    lat_0 = 46.7
    delta_lat = 3.14*.5 
    lon_0 = 267.3
    delta_lon = 4.17*.5
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    
    # get lat/lon of input data from one of the h5 files 
    test_data_dir = '/fs/homeu3/eccc/mrd/ords/rpnad/dja001/python/packages/domutils_package/test_data/'
    dum_h5_file = os.path.join(test_data_dir, 'odimh5_radar_composites', '2022/qcomp_202205212000.h5')
    input_ll    = radar_tools.read_h5_composite(dum_h5_file, latlon=True)
    input_lats  = input_ll['latitudes']
    input_lons  = input_ll['longitudes']
    
    # get lat/lon of output data 
    sample_pr_file = os.path.join(test_data_dir, 'hrdps_5p1_prp0.fst')
    output_ll = fst_tools.get_data(sample_pr_file, var_name='PR', latlon=True)
    output_lats = output_ll['lat']
    output_lons = output_ll['lon']
    
    # instantiate projection object for input data
    input_proj_obj = geo_tools.ProjInds(src_lon=input_lons, src_lat=input_lats,
                                        extent=map_extent, dest_crs=proj_aea, image_res=img_res)
    
    # instantiate projection object for output data
    output_proj_obj = geo_tools.ProjInds(src_lon=output_lons, src_lat=output_lats,
                                         extent=map_extent, dest_crs=proj_aea, image_res=img_res)

    def figure_for_timestep(src_delta_min, interp_delta_min, t0,
                            fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m ):

        source_t_offset   = datetime.timedelta(seconds=src_delta_min * 60.0)
        source_valid_time  = t0 + source_t_offset
        interpolated_t_offset = datetime.timedelta(seconds=interp_delta_min * 60.0)
        interpolated_valid_time = source_valid_time + interpolated_t_offset

        # matplotlib global settings
        dpi = 400
        mpl.rcParams.update({
            'font.family': 'Latin Modern Roman',
            'font.size': 32,
            'axes.titlesize': 32,
            'axes.labelsize': 32,
            'xtick.labelsize': 30,
            'ytick.labelsize': 30,
            'legend.fontsize': 30,
            'figure.dpi': dpi,
            'savefig.dpi': dpi,
            })

        # instantiate figure
        fig = plt.figure(figsize=(fig_w,fig_h))

        # load data
        time_str = interpolated_valid_time.strftime('%Y%m%d%H%M')
        savename = f'/space/hall7/sitestore/eccc/mrd/rpnad/dja001/tmp/tmp_advected_data/{time_str}_adveced_data.npz'
        np_data = np.load(savename)
        nx, ny, nz = np_data['rr_arr'].shape
        for member_id in  np.arange(nz):
            this_rr = np_data['rr_arr'][:,:,member_id]
            this_qi = np_data['qi_arr'][:,:,member_id]
            this_weighted_qi = np_data['weighted_qi_arr'][:,:,member_id]

            this_rr = np.where(~np.isfinite(this_rr), -9999., this_rr)
            this_qi = np.where(~np.isfinite(this_qi), 0, this_qi)
            this_weighted_qi = np.where(~np.isfinite(this_weighted_qi), 0, this_weighted_qi)

            print(member_id)
            if member_id == nz-1:
                plot_palette = 'right'
            else:
                plot_palette = None

            # precip rate
            x0 = sp_w + member_id * (rec_w + sp_m)
            y0 = sp_h 
            ax_pos = [x0, y0, rec_w, rec_h]
            title = f'Precip rate'
            plot_panel(this_rr,
                       fig, ax_pos, title, 
                       proj_aea, 
                       output_proj_obj, pr_colormap,
                       plot_palette=plot_palette,
                       pal_units='mm/h')

            # quality index
            x0 = sp_w + member_id * (rec_w + sp_m)
            y0 = 2.*sp_h + rec_h
            ax_pos = [x0, y0, rec_w, rec_h]
            title = f'Weighted Quality index'
            plot_panel(this_weighted_qi,
                       fig, ax_pos, title, 
                       proj_aea, 
                       output_proj_obj, qi_colormap,
                       plot_palette=plot_palette,
                       pal_units='[unitless]')


        # save output
        figure_dir = '/home/dja001/python/packages/domutils_package/test_results_3.13.12/generated_figures/test_radar_time_interpolation/'
        date_prefix = interpolated_valid_time.strftime('%Y%m%d%H%M')
        fig_name_svg = os.path.join(figure_dir, f'{date_prefix}_components.svg')
        plt.savefig(fig_name_svg)
        plt.close(fig)
        print(f'done with {fig_name_svg}')

        return source_valid_time, interpolated_valid_time

    # DOCS:figure_setup_ends

    # DOCS:animation_frames_begins
    t0 = datetime.datetime(2022,8,29,3,48)
    source_deltat = np.arange(0, 30, 6, dtype=int)    # minutes
    interpolated_deltat = np.arange(6) # minutes
    serial=True
    if serial:
        for src_delta_min in source_deltat:
            for interp_delta_min in interpolated_deltat:
                figure_for_timestep(src_delta_min, interp_delta_min, t0, fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m)
    else:
        #client = dask.distributed.Client(processes=True, threads_per_worker=1, 
                                         #n_workers=20, 
                                         #silence_logs=40) 

        tasks = [dask.delayed(figure_for_timestep)(src_delta_min, interp_delta_min, t0, fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m)
                  for src_delta_min in source_deltat
                  for interp_delta_min in interpolated_deltat]

        with LocalCluster(processes=True, n_workers=10, threads_per_worker=1) as cluster, Client(cluster) as client:
            results = dask.compute(tasks)  # parallel execution
    
    # DOCS:animation_frames_ends



if __name__ == '__main__' : 

    plot_components()


