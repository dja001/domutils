from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def plot_rdpr_rdqi(fst_file:   str=None, 
                   this_date:  Any=None,
                   figure_dir: str=None,
                   uv_motion:  Any=None,
                   z_acc:      Any=None,
                   lats:       Any=None,
                   lons:       Any=None,
                   info=None,
                   args=None            ):
    """ plot RDPR and RDQI from a rpn "standard" file 

    Data needs to be at correct valid time

    If the file does not exist, the image will display "Non existing file"

    Args:

        fst_file:   full path of standard file to read
        this_date:  validity time of data to plot
        args:       object whose attributes represent the argukents to obs_process

    
    Returns:

        Nothing, only plot a figure

    """

    import os
    from os import linesep as newline
    import datetime
    import logging
    import gc
    import shutil
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from   packaging import version

    #remove annoying shapely deprecation warnings
    import warnings
    from shapely.errors import ShapelyDeprecationWarning
    warnings.filterwarnings('ignore', category=ShapelyDeprecationWarning)
    import cartopy
    import cartopy.feature as cfeature

    import domutils.legs as legs
    import domcmc.fst_tools as fst_tools
    import domutils.geo_tools as geo_tools
    import domutils._py_tools as dpy

    #logging
    logger = logging.getLogger(__name__)

    #value assigned to missing data
    missing = -9999.

    #use provided data path for cartiopy shapefiles
    #TODO there has got to be a better way to do this!
    if args is not None:
        if hasattr(args, 'cartopy_dir'):
            if args.cartopy_dir is not None:
                cartopy.config['pre_existing_data_dir'] = args.cartopy_dir
    else:
        raise ValueError('the "args" object must be passed to this routine')

    fig_format = args.figure_format

    #Read data
    if fst_file is not None:
        mode = 'prqi'
        logger.info('Reading RDPR and RDQI from: '+fst_file)
        pr_dict = fst_tools.get_data(file_name=fst_file, var_name='RDPR', datev=this_date, latlon=True)
        qi_dict = fst_tools.get_data(file_name=fst_file, var_name='RDQI', datev=this_date)
    else:
        mode = 'motion_vectors'
        if uv_motion is None:
            raise ValueError('uv_motion needed in {mode=}')
        else:
            uv_motion = np.transpose(uv_motion)
        if z_acc is None:
            raise ValueError('uv_motion needed in {mode=}')
        else:
            z_acc = np.transpose(z_acc)
            z_acc = np.where(np.isfinite(z_acc), z_acc, missing)




    #make figure directory if it does not exist
    dpy.parallel_mkdir(figure_dir)


    #setup figure properties
    ratio = 0.5
    fig_name_recipe = '%Y%m%d_%H%M%S.svg'
    # all sizes are inches for consistency with matplotlib
    rec_w = 6.            # Horizontal size of a panel  /2.54 for dimensions in cm
    rec_h = ratio * rec_w # Vertical size of a panel
    sp_w = .2             # horizontal space between panels
    sp_h = .5             # vertical space between panels
    pal_sp = .1           # spavce between panel and palette
    pal_w = .25           # width of palette
    tit_h = 1.            # height of title
    xp = .04              # axes relative x position of image caption
    yp = 1.05             # axes relative y position of image caption
    dpi = 500             # density of pixel for figure
    #size of figure
    if mode == 'prqi':
        fig_w = 3. +    2*(sp_w + rec_w + pal_w + pal_sp )
    elif mode == 'motion_vectors':
        fig_w = 3. +    3*(sp_w + rec_w + pal_w + pal_sp )
    fig_h = 2.*sp_h +       sp_h + rec_h + tit_h
    #normalize all dimensions
    rec_w /= fig_w
    rec_h /= fig_h
    sp_w  /= fig_w
    sp_h  /= fig_h
    pal_sp/= fig_w
    pal_w /= fig_w
    tit_h /= fig_h 
    # matplotlib global settings
    if mode == 'prqi':
        dpi = 500
    elif mode == 'motion_vectors':
        dpi = 200

    mpl.rcParams.update({
        'font.family': 'Latin Modern Roman',
        'font.size': 24,
        'axes.titlesize': 24,
        'axes.labelsize': 24,
        'xtick.labelsize': 20,
        'ytick.labelsize': 20,
        'legend.fontsize': 20,
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        })

    # pretty font in figures
    # instantiate figure
    fig = plt.figure(figsize=(fig_w, fig_h), constrained_layout=False)
    fig.set_layout_engine(None)

    ax = fig.add_axes([0,0,1,1],zorder=0)
    ax.axis('off')
    ax.annotate(this_date.strftime('%Y-%m-%d %H:%M'), size=35,
                xy=(0.015, 0.92), xycoords='figure fraction',
                bbox=dict(boxstyle="round", fc=[1,1,1,.9], ec=[1,1,1,0]))

    if info is not None:
        ax.annotate(info, size=25,
                    xy=(0.015, 0.82), xycoords='figure fraction',
                    bbox=dict(boxstyle="round", fc=[1,1,1,.9], ec=[1,1,1,0]))

    #setup color mapping objects:
    #
    #Precip rate
    map_pr = legs.PalObj(range_arr=[.1, 3., 6., 12., 25., 50., 100.],
                         n_col=6,
                         over_high='extend', under_low='white',
                         excep_val=missing, excep_col='grey_200')
    #reflectivity
    map_dbz = legs.PalObj(range_arr=[0,60],
                          n_col=6,
                          over_high='extend', under_low='white',
                          excep_val=missing, excep_col='grey_200')
    #custom pastel color segments for QI index
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[255,227,215],[205,144, 73]],  #pale/dark brown
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    map_qi = legs.PalObj(range_arr=[0., 1.],
                         dark_pos='high',
                         color_arr=pastel,
                         excep_val=[missing,0.],
                         excep_col=['grey_220','white'])

    if mode == 'prqi':
        lats = pr_dict['lat']
        lons = pr_dict['lon']
    elif mode == 'motion_vectors':
        if (lats is None) or (lons is None):
            raise ValueError('lats and lons needed for plotting motion vectors')
    
    #Setup geographical projection 
    # Full HRDPS grid
    pole_latitude=35.7
    pole_longitude=65.5
    lat_0 = 48.8
    delta_lat = 10.
    lon_0 = 266.00
    delta_lon = 40.
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    proj_aea = cartopy.crs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    logger.info('Making projection object')
    proj_obj = geo_tools.ProjInds(src_lon=lons, src_lat=lats,
                                  extent=map_extent, dest_crs=proj_aea, 
                                  image_res=(800,400))
    if mode == 'prqi':
        if pr_dict is None:
            #data not found or not available at desired date
            #print warning and make empty image
            message=('RDPR not available in file: '+newline+
                                           fst_file+newline+
                                          'at date'+newline+
                                           str(this_date))
            logger.warning(message)
            ax = fig.add_axes([0,0,1,1])
            ax.axis('off')
            ax.annotate(message, size=18,
                         xy=(.1, .5), xycoords='axes fraction')
        else:
            #PR found in file, proceed to plot it


            #plot precip rate
            #
            #position of this fig
            x0 = sp_w + 0.*(rec_w + sp_w)
            y0 = sp_h + 0.*(rec_h + sp_h)
            pos = [x0, y0, rec_w, rec_h]
            #setup axes
            ax = fig.add_axes(pos, projection=proj_aea)
            # lat/lon extent will not work properly you need to use rotated_extent in the projection crs
            ax.set_extent(proj_obj.rotated_extent, crs=proj_aea)
            ax.set_autoscale_on(False)
            ax.set_aspect('auto', adjustable='datalim')
            #thinner lines
            if version.parse(cartopy.__version__) >= version.parse("0.18.0"):
                ax.spines['geo'].set_linewidth(0.3)
            else:
                ax.outline_patch.set_linewidth(0.3) 
            #plot image caption
            ax.annotate('RDPR', size=30,
                         xy=(xp, yp), xycoords='axes fraction')
            #geographical projection of data
            projected_pr = proj_obj.project_data(pr_dict['values'])
            #apply color mapping n plot data
            map_pr.plot_data(ax, 
                             projected_pr, 
                             palette='right',
                             pal_linewidth=0.3, pal_units='[mm/h]', 
                             pal_format='{:5.1f}', equal_legs=True)
            #force axes to respect ratio we previously indicated...
            #plot geographical contours
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, edgecolor='0.3',zorder=1)
            #plot border
            proj_obj.plot_border(ax, mask_outside=True, linewidth=.3)

            # Final call to prevent resizing by cartopy's geoaxes calls
            ax.set_position(pos)
            ax.set_anchor('C')   # optional but helps stability
            ax.set_aspect('auto', adjustable='datalim')


            #plot quality index
            #
            #position of this fig
            x0 = sp_w + 1.*(rec_w + sp_w + pal_sp + pal_w + 1.5/fig_w)
            y0 = sp_h + 0.*(rec_h + sp_h)
            pos = [x0, y0, rec_w, rec_h]
            #setup axes
            ax = fig.add_axes(pos, projection=proj_aea)
            ax.set_extent(proj_obj.rotated_extent, crs=proj_aea)
            ax.set_autoscale_on(False)
            ax.set_aspect('auto', adjustable='datalim')
            #thinner lines
            if version.parse(cartopy.__version__) >= version.parse("0.18.0"):
                ax.spines['geo'].set_linewidth(0.3)
            else:
                ax.outline_patch.set_linewidth(0.3) 
            #plot image caption
            ax.annotate('RDQI', size=30,
                         xy=(xp, yp), xycoords='axes fraction')
            if qi_dict is None:
                #QI not available indicate it on figure
                message='RDQI not available in file: '+newline+fst_file
                logger.warning.warn(message)
                ax.annotate(message, size=10,
                             xy=(.0, .5), xycoords='axes fraction')
            else:
                #QI is available, plot it
                #
                #geographical projection of data
                projected_qi = proj_obj.project_data(qi_dict['values'])
                #apply color mapping n plot data
                map_qi.plot_data(ax, 
                                 projected_qi, 
                                 palette='right',
                                 pal_linewidth=0.3, pal_units='[unitless]',
                                 pal_format='{:2.1f}')
                #force axes to respect ratio we previously indicated...
                #plot geographical contours
                ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, edgecolor='0.3',zorder=1)
                #plot border
                proj_obj.plot_border(ax, mask_outside=True, linewidth=0.3)

            # Final call to prevent resizing by cartopy's geoaxes calls
            ax.set_position(pos)
            ax.set_anchor('C')   # optional but helps stability
            ax.set_aspect('auto', adjustable='datalim')

    elif mode == 'motion_vectors':
        #plot the 3 precip rate fields at the origin of the mv
        #
        for ii in range(3):
            #position of this fig
            x0 = sp_w + ii*(rec_w + sp_w)
            y0 = sp_h + 0.*(rec_h + sp_h)
            pos = [x0, y0, rec_w, rec_h]
            #setup axes
            ax = fig.add_axes(pos, projection=proj_aea)
            # lat/lon extent will not work properly you need to use rotated_extent in the projection crs
            ax.set_extent(proj_obj.rotated_extent, crs=proj_aea)
            ax.set_autoscale_on(False)
            ax.set_aspect('auto', adjustable='datalim')
            #thinner lines
            ax.spines['geo'].set_linewidth(0.3)
            #plot image caption
            ax.annotate('dBZ', size=30,
                         xy=(xp, yp), xycoords='axes fraction')
            #geographical projection of data
            projected_pr = proj_obj.project_data(z_acc[:,:,ii])
            #apply color mapping n plot data
            map_dbz.plot_data(ax, 
                              projected_pr, 
                              palette='right',
                              pal_linewidth=0.3, pal_units='[dBZ]', 
                              pal_format='{:5.1f}')
            #force axes to respect ratio we previously indicated...
            #plot geographical contours
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, edgecolor='0.3',zorder=1)
            #plot border
            proj_obj.plot_border(ax, mask_outside=True, linewidth=.3)

            # Final call to prevent resizing by cartopy's geoaxes calls
            ax.set_position(pos)
            ax.set_anchor('C')   # optional but helps stability
            ax.set_aspect('auto', adjustable='datalim')

            if ii == 1:
                sample = 30
                speed = np.sqrt(uv_motion[::sample,::sample,0]**2. + uv_motion[::sample,::sample,1]**2.)
                q = ax.quiver(
                         lons[::sample,::sample],        lats[::sample,::sample], 
                    uv_motion[::sample,::sample,0], uv_motion[::sample,::sample,1],
                    transform=cartopy.crs.PlateCarree(),
                    scale=60,                      # tune this to adjust arrow size
                    width=0.001,
                    pivot="middle",
                )



    #save figure
    svg_name = figure_dir + this_date.strftime(fig_name_recipe)

    logger.info('Saving figure:'+svg_name)
    plt.savefig(svg_name)

    if fig_format != 'svg':
        dpy.convert(svg_name, fig_format, del_orig=True, density=dpi, geometry='50%')

    #not sure what is accumulating but adding this garbage collection step 
    #prevents jobs from aborting when a large number of files are made 
    plt.close(fig)
    gc.collect()

    logger.info('plot_rdpr_rdqi Done')
