from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def plot_rdpr_rdqi(fst_file:   str=None, 
                   this_date:  Any=None,
                   fig_dir:    Optional[str]=None, 
                   fig_format: Optional[str]='gif'):
    """ plot RDPR and RDQI from a rpn "standard" file 

    Data needs to be at correct valid time

    If the file does not exist, the image will display "Non existing file"

    Args:

        fst_file:   full path of standard file to read
        this_date:  validity time of data to plot
        fig_dir:    directory where figures will be written

    
    Returns:

        Nothing, only plot a figure

    """

    import os
    from os import linesep as newline
    import datetime
    import warnings
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import domutils.legs as legs
    import domcmc.fst_tools as fst_tools
    import domutils.geo_tools as geo_tools
    import domutils._py_tools as dPy

    #Read data
    pr_dict = fst_tools.get_data(file_name=fst_file, var_name='RDPR', datev=this_date, latlon=True)
    qi_dict = fst_tools.get_data(file_name=fst_file, var_name='RDQI', datev=this_date)

    #value assigned to missing data
    missing = -9999.

    #make figure directory if it does not exist
    if not os.path.isdir(fig_dir):
        os.makedirs(fig_dir)

    #setup figure properties
    ratio = 0.5
    fig_name_recipe = '%Y%m%d_%H%M.svg'
    # all sizes are inches for consistency with matplotlib
    rec_w = 6.            # Horizontal size of a panel  /2.54 for dimensions in cm
    rec_h = ratio * rec_w # Vertical size of a panel
    sp_w = .1             # horizontal space between panels
    sp_h = .5             # vertical space between panels
    pal_sp = .1           # spavce between panel and palette
    pal_w = .25           # width of palette
    tit_h = 1.            # height of title
    xp = .04              # axes relative x position of image caption
    yp = 1.05             # axes relative y position of image caption
    dpi = 500             # density of pixel for figure
    #size of figure
    fig_w = 3. +    2*(sp_w + rec_w + pal_w + pal_sp )
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
    mpl.rcParams.update({'font.size': 24})
    # Use this for editable text in svg
    mpl.rcParams['text.usetex']  = False
    mpl.rcParams['svg.fonttype'] = 'none'
    # Hi def figure
    mpl.rcParams['figure.dpi'] = dpi
    # instantiate figure
    fig = plt.figure(figsize=(fig_w, fig_h))

    ax = fig.add_axes([0,0,1,1],zorder=0)
    ax.axis('off')
    ax.annotate(this_date.strftime('%Y-%m-%d %H:%M'), size=35,
                xy=(0.015, 0.92), xycoords='figure fraction',
                bbox=dict(boxstyle="round", fc=[1,1,1,.9], ec=[1,1,1,0]))

    if pr_dict is None:
        #data not found or not available at desired date
        #print warning and make empty image
        message=('RDPR not available in file: '+newline+
                                          fst_file+newline+
                                         'at date'+newline+
                                              str(this_date))
        warnings.warn(message)
        ax = fig.add_axes([0,0,1,1])
        ax.axis('off')
        ax.annotate(message, size=18,
                     xy=(.1, .5), xycoords='axes fraction')
    else:
        #PR found in file, proceed to plot it

        #setup color mapping objects:
        #
        #Precip rate
        map_pr = legs.PalObj(range_arr=[.1, 3., 6., 12., 25., 50., 100.],
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

        #Setup geographical projection 
        # Full HRDPS grid
        pole_latitude=35.7
        pole_longitude=65.5
        lat_0 = 48.8
        delta_lat = 10.
        lon_0 = 266.00
        delta_lon = 40.
        map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
        proj_aea = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
        proj_obj = geo_tools.ProjInds(src_lon=pr_dict['lon'], src_lat=pr_dict['lat'],
                                      extent=map_extent, dest_crs=proj_aea, 
                                      image_res=(800,400))
                                      #image_res=(rec_w*dpi,rec_h*dpi))
        #plot precip rate
        #
        #position of this fig
        x0 = sp_w + 0.*(rec_w + sp_w)
        y0 = sp_h + 0.*(rec_h + sp_h)
        pos = [x0, y0, rec_w, rec_h]
        #setup axes
        ax = fig.add_axes(pos, projection=proj_aea)
        ax.set_extent(map_extent)
        ax.outline_patch.set_linewidth(.3)
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
        ax.set_aspect('auto')  
        #plot geographical contours
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, edgecolor='0.3',zorder=1)
        #plot border
        proj_obj.plot_border(ax, mask_outside=True, linewidth=.3)


        #plot quality index
        #
        #position of this fig
        x0 = sp_w + 1.*(rec_w + sp_w + pal_sp + pal_w + 1.5/fig_w)
        y0 = sp_h + 0.*(rec_h + sp_h)
        pos = [x0, y0, rec_w, rec_h]
        #setup axes
        ax = fig.add_axes(pos, projection=proj_aea)
        ax.set_extent(map_extent)
        ax.outline_patch.set_linewidth(.3)
        #plot image caption
        ax.annotate('RDQI', size=30,
                     xy=(xp, yp), xycoords='axes fraction')
        if qi_dict is None:
            #QI not available indicate it on figure
            message='RDQI not available in file: '+newline+fst_file
            warnings.warn(message)
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
            ax.set_aspect('auto')  
            #plot geographical contours
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, edgecolor='0.3',zorder=1)
            #plot border
            proj_obj.plot_border(ax, mask_outside=True, linewidth=.3)


    #save figure
    svg_name = fig_dir + this_date.strftime(fig_name_recipe)
    plt.savefig(svg_name)
    plt.close(fig)


    dPy.lmroman(svg_name)
    if fig_format != 'svg':
        dPy.convert(svg_name, fig_format, del_orig=False, density=500, geometry='50%')

    #not sure what is accumulating but adding this garbage collection step 
    #prevents jobs from aborting when a largen number of files are made 
    #gc.collect()
    print('done with: ', svg_name)
