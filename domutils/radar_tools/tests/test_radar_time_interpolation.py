# to run only one test
#
# pytest -vs test_radar_time_interpolation.py::test_time_interpolation


import pytest
import os
import datetime
import numpy as np

# DOCS:class_begins
# a class that mimics the output of argparse
class ArgsClass():
    def __init__(self, setup_test_paths):
        test_data_dir    = setup_test_paths['test_data_dir']
        test_results_dir = setup_test_paths['test_results_dir']

        generated_files_dir  = os.path.join(test_results_dir, 'generated_files',   'test_radar_time_interpolation')
        generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_radar_time_interpolation')

        self.input_t0                 = '202208290230'
        self.input_tf                 = '202208290530'
        self.input_dt                 = '6M'
        self.output_t0                = '202208290330'
        self.output_tf                = '202208290430'
        self.output_dt                = '1M'
        self.interp_max_dt            = '13M'
        self.complete_dataset         = 'False'
        self.t_interp_method          = 'nowcast'
        self.input_data_dir           = os.path.join(test_data_dir, 'odimh5_radar_composites')
        self.input_file_struc         = '%Y/qcomp_%Y%m%d%H%M.h5'
        self.h5_latlon_file           = os.path.join(test_data_dir, 'radar_continental_2.5km_2882x2032.pickle')
        self.sample_pr_file           = os.path.join(test_data_dir, 'hrdps_5p1_prp0.fst')
        self.ncores                   = 40    # use as many cpus as you have on your system 
        self.preproc_median_filt      = '3'
        self.preproc_smooth_radius    = '4'
        self.nowcast_median_filt      = '3'
        self.output_dir               = os.path.join(generated_files_dir, 'obs_process_t_interp')
        self.output_file_format       = 'fst'
        self.output_file_struc        = '%Y%m%d%H%M.fst'
        self.figure_format            = 'svg'
        self.log_level                = 'WARNING'

# DOCS:class_ends

# DOCS:function_definition_begins
def plot_panel(data,
               fig, ax_pos, title, 
               proj_aea, 
               proj_obj, colormap, 
               plot_palette=None, 
               pal_units=None, 
               show_artefacts=False):
    '''function that plots individual panels
    '''
    import matplotlib.pyplot as plt
    import cartopy.feature as cfeature

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


def figure_for_timestep(src_delta_min, interp_delta_min, t0,
                        proj_aea,
                        input_proj_obj, output_proj_obj,
                        pr_colormap, qi_colormap, 
                        generated_figure_dir, 
                        args, fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m ):

    '''make the figure for every output timestep
    '''

    import subprocess
    import datetime
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import domutils.radar_tools as radar_tools

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

    # source data on original grid
    dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
                                             valid_date=source_valid_time,
                                             data_path=args.input_data_dir,
                                             data_recipe=args.input_file_struc)
    x0 = sp_w 
    y0 = 2.*sp_h + rec_h
    ax_pos = [x0, y0, rec_w, rec_h]
    title = f'Source precip rate \n @ t0+{src_delta_min}minutes'
    plot_panel(dat_dict['precip_rate'],
               fig, ax_pos, title, 
               proj_aea, 
               input_proj_obj, pr_colormap,
               plot_palette='right',
               pal_units='[mm/h]')

    # source quality index
    x0 = sp_w + rec_w + sp_m
    y0 = 2.*sp_h + rec_h
    ax_pos = [x0, y0, rec_w, rec_h]
    title = f'Source quality index \n @ t0+{src_delta_min}minutes'
    plot_panel(dat_dict['total_quality_index'],
               fig, ax_pos, title, 
               proj_aea, 
               input_proj_obj, qi_colormap,
               plot_palette='right',
               pal_units='[unitless]')

    # Time interpolated data
    dat_dict = radar_tools.get_instantaneous(desired_quantity='precip_rate',
                                             valid_date=interpolated_valid_time,
                                             data_path=args.output_dir,
                                             data_recipe=args.output_file_struc)
    x0 = sp_w 
    y0 = sp_h
    ax_pos = [x0, y0, rec_w, rec_h]
    title = f'Interpolated precip rate \n @ t0+{src_delta_min+interp_delta_min}minutes'
    plot_panel(dat_dict['precip_rate'],
               fig, ax_pos, title, 
               proj_aea, 
               output_proj_obj, pr_colormap,
               plot_palette='right',
               pal_units='[mm/h]')

    # quality index 
    x0 = sp_w  + rec_w + sp_m
    y0 = sp_h
    ax_pos = [x0, y0, rec_w, rec_h]
    title = f' Interpolated quality index\n @ t0+{src_delta_min+interp_delta_min}minutes'
    plot_panel(dat_dict['total_quality_index'],
               fig, ax_pos, title, 
               proj_aea, 
               output_proj_obj, qi_colormap,
               plot_palette='right',
               pal_units='[unitless]')

    # save output
    date_prefix = interpolated_valid_time.strftime('%Y%m%d%H%M')
    fig_name = os.path.join(generated_figure_dir, f'{date_prefix}_frame.png')
    plt.savefig(fig_name)
    #fig_name_svg = os.path.join(generated_figure_dir, f'{date_prefix}_frame.svg')
    #plt.savefig(fig_name_svg)
    plt.close(fig)
    print(f'done with {fig_name}')

    # use "convert" to make a gif out of the png
    cmd = ['convert', fig_name, '-geometry', '15%', '-quantize', 'transparent', '-dither', 'FloydSteinberg', '-colors', '256',  fig_name.replace('png', 'gif')]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

    # we don't need the original png anymore
    os.remove(fig_name)

    return source_valid_time, interpolated_valid_time

# DOCS:function_definition_ends

def interpolate_and_animate(setup_test_paths, args, 
                            proj_aea, map_extent,
                            anim_t0, anim_source_deltat):
    """ Run obs_process and generate images from the output files

    This function is called once for each case being demonstrated.

    Its code is also copied and shown as an example in the documentation.
    """

    # DOCS:setup_begins
    import os
    import datetime
    import subprocess
    import glob
    import shutil
    import copy
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import dask
    from dask.distributed import Client, LocalCluster
    import domutils.legs as legs
    import domutils.geo_tools as geo_tools
    import domutils.radar_tools as radar_tools
    import domcmc.fst_tools as fst_tools
    import domutils._py_tools as py_tools
    
    #setting up directories
    test_data_dir    = setup_test_paths['test_data_dir']
    test_results_dir = setup_test_paths['test_results_dir']

    generated_files_dir  = os.path.join(test_results_dir, 'generated_files',   'test_radar_time_interpolation')
    generated_figure_dir = os.path.join(test_results_dir, 'generated_figures', 'test_radar_time_interpolation')
    reference_figure_dir = os.path.join(test_data_dir,    'reference_figures', 'test_radar_time_interpolation')

    py_tools.parallel_mkdir(generated_files_dir)
    py_tools.parallel_mkdir(generated_figure_dir)
    # DOCS:setup_ends

    # observations are processed here
    # the output are saved in individual files 
    # DOCS:process_data_begins
    radar_tools.obs_process(args)
    # DOCS:process_data_ends

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
    fig_w = 19.                    #size of figure
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
    
    # get lat/lon of input data from one of the h5 files 
    dum_h5_file = os.path.join(test_data_dir, 'odimh5_radar_composites', '2022/qcomp_202205212000.h5')
    input_ll    = radar_tools.read_h5_composite(dum_h5_file, latlon=True)
    input_lats  = input_ll['latitudes']
    input_lons  = input_ll['longitudes']
    
    # get lat/lon of output data 
    output_ll = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)
    output_lats = output_ll['lat']
    output_lons = output_ll['lon']
    
    # instantiate projection object for input data
    input_proj_obj = geo_tools.ProjInds(src_lon=input_lons, src_lat=input_lats,
                                        extent=map_extent, dest_crs=proj_aea, image_res=img_res)
    
    # instantiate projection object for output data
    output_proj_obj = geo_tools.ProjInds(src_lon=output_lons, src_lat=output_lats,
                                         extent=map_extent, dest_crs=proj_aea, image_res=img_res)

    # DOCS:figure_setup_ends

    # DOCS:animation_frames_begins
    interpolated_deltat = np.arange(6) # minutes

    # making the figures only requires the file paths found in args
    # obs_process attached large arrays and projection objects to this object;
    # they are removed here so that only light-weight data is sent to the dask workers
    plot_args = copy.copy(args)
    for attr in ('dask_client', 'proj_obj', 'out_lats', 'out_lons'):
        setattr(plot_args, attr, None)

    serial=False
    if serial:
        for src_delta_min in anim_source_deltat:
            for interp_delta_min in interpolated_deltat:
                figure_for_timestep(src_delta_min, interp_delta_min, anim_t0, 
                                    proj_aea,
                                    input_proj_obj, output_proj_obj,
                                    pr_colormap, qi_colormap, 
                                    generated_figure_dir, 
                                    plot_args, fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m)
    else:
        tasks = [dask.delayed(figure_for_timestep)(src_delta_min, interp_delta_min, anim_t0, 
                                                   proj_aea,
                                                   input_proj_obj, output_proj_obj,
                                                   pr_colormap, qi_colormap, 
                                                   generated_figure_dir, 
                                                   plot_args, fig_w, fig_h, sp_w, sp_h, rec_w, rec_h, sp_m)
                  for src_delta_min in anim_source_deltat
                  for interp_delta_min in interpolated_deltat]

        with LocalCluster(processes=True, n_workers=10, threads_per_worker=1) as cluster, Client(cluster) as client:
            results = dask.compute(*tasks)  # parallel execution
    
    # DOCS:animation_frames_ends

    #compare image with saved reference
    #fig_name = os.path.join(generated_figure_dir, '01_time_interpol_demo_plain.gif')
    #reference_figure = os.path.join(reference_figure_dir, os.path.basename(fig_name))
    #images_are_similar = py_tools.render_similarly(fig_name, reference_figure,
    #                                               output_dir=os.path.join(test_results_dir, 'render_similarly'))

    #test fails if images are not similar
    #assert images_are_similar

    # DOCS:animated_gif_begins
    date_prefix = anim_t0.strftime('%Y%m')
    movie_name = os.path.join(generated_figure_dir, f'{date_prefix}_movie.gif')
    gif_list = sorted(glob.glob(os.path.join(generated_figure_dir,f'{date_prefix}*frame.gif')))   
    cmd = ['convert', '-loop', '0', '-delay', '30']+gif_list+[movie_name]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    # DOCS:animated_gif_ends

    #assert os.path.isfile(movie_name)

    # DOCS:accumulation_begins
    duration = 30 # minutes
    end_date = anim_t0 + datetime.timedelta(minutes=30)

    # the next figure has only one row of panels
    # the panels keep the same size, only the height of the figure changes
    fig_h = 8.                         #size of figure
    rec_h = ratio*(rec_w*fig_w)/fig_h  #size of axes
    sp_h  = .5/fig_h                   #space between panel and border
    
    # instantiate figure
    fig = plt.figure(figsize=(fig_w,fig_h))
    
    # make accumulation from source data
    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            input_dt=6., # minutes
                                            data_path=args.input_data_dir,
                                            data_recipe=args.input_file_struc)
    x0 = 2.*sp_w + rec_w
    y0 = sp_h 
    ax_pos = [x0, y0, rec_w, rec_h]
    title = 'Accumulation from \n source data'
    plot_panel(dat_dict['accumulation'],
               fig, ax_pos, title, 
               proj_aea, 
               input_proj_obj, pr_colormap,
               plot_palette='right',
               pal_units='mm',
               show_artefacts=True)
    
    # make accumulation from time interpolated data
    dat_dict = radar_tools.get_accumulation(end_date=end_date,
                                            duration=duration,
                                            input_dt=1., # minutes
                                            data_path=args.output_dir, 
                                            data_recipe=args.output_file_struc)
    x0 = sp_w 
    y0 = sp_h
    ax_pos = [x0, y0, rec_w, rec_h]
    title = 'Accumulation from \n time interpolated data'
    plot_panel(dat_dict['accumulation'],
               fig, ax_pos, title, 
               proj_aea,
               output_proj_obj, pr_colormap)
    
    # save output
    fig_name = os.path.join(generated_figure_dir, f'{date_prefix}_accumulation.svg')
    plt.savefig(fig_name)
    plt.close(fig)
    
    # DOCS:accumulation_ends

    #compare image with saved reference
    reference_figure = os.path.join(reference_figure_dir, os.path.basename(fig_name))
    #images_are_similar = py_tools.render_similarly(fig_name, reference_figure,
    #                                               output_dir=os.path.join(test_results_dir, 'render_similarly') )

    ##test fails if images are not similar
    #assert images_are_similar


@pytest.mark.rpnpy
def test_time_interpolation(setup_test_paths):
    """ This test runs obs_process and generates images from the output files

    The code of this test is also copied and shown as an example in the documentation

    As such the purpose of this test is not so much to test the code but to make 
    sure that the documentation stays up to date. 
    """

    # DOCS:case_setup_begins
    import cartopy.crs as ccrs

    # a new argument object is needed for each case since obs_process
    # modifies the arguments it receives
    args = ArgsClass(setup_test_paths)

    # times of the source data that will be displayed in the animation
    anim_t0 = datetime.datetime(2022,8,29,3,42)
    anim_source_deltat = np.arange(0, 37, 6, dtype=int)    # minutes

    # domain of the figures; 300x300 km over Minnesota/Wisconsin
    pole_latitude=35.7
    pole_longitude=65.5
    lat_0 = 46.7
    delta_lat = 3.14*.5 
    lon_0 = 267.3
    delta_lon = 4.17*.5
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    # DOCS:case_setup_ends

    interpolate_and_animate(setup_test_paths, args, 
                            proj_aea, map_extent,
                            anim_t0, anim_source_deltat)


    # second case; 250 km around the Blainville radar
    args = ArgsClass(setup_test_paths)
    args.input_t0  = '202205212000'
    args.input_tf  = '202205212300'
    args.output_t0 = '202205212100'
    args.output_tf = '202205212200'

    anim_t0 = datetime.datetime(2022,5,21,21,0)
    anim_source_deltat = np.arange(0, 37, 6, dtype=int)    # minutes

    pole_latitude=90.
    pole_longitude=0.
    lat_0 = 46.
    delta_lat = 2.18/2.
    lon_0 = -73.75 
    delta_lon = 3.12/2.
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)

    interpolate_and_animate(setup_test_paths, args, 
                            proj_aea, map_extent,
                            anim_t0, anim_source_deltat)


if __name__ == '__main__' : 

    # when called directly, the paths normally provided by the
    # setup_test_paths fixture are defined here
    setup_test_paths = {}
    setup_test_paths['test_data_dir'] = '/fs/homeu3/eccc/mrd/ords/rpnad/dja001/python/packages/domutils_package/test_data/'
    setup_test_paths['test_results_dir'] = '/fs/homeu3/eccc/mrd/ords/rpnad/dja001/python/packages/domutils_package/test_results_3.13.12/'

    test_time_interpolation(setup_test_paths)

