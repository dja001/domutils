"""
Radar PPI
==============================

   Display radar Plan Position Indicators (PPIs) using a combination 
   of *radar_tools*, *geo_tools* and *legs*.

   - Data consists of a radar Volume scan in the ODIM HDF5 format that 
     are read with *domutils.radar_tools*.
   - Data is projected on Cartopy geoaxes using *domutils.geo_tools*
   - Various color mappings are applied with *domutils.legs*

   Some advanced concepts are demonstrated in this example.
   
   - Quality controls are applied to Doppler velocity based 
     on the Depolarization Ratio (DR) and the total quality index.
   - Matplotlib/cartopy geoaxes are clipped and superposed to show 
     a closeup of a possible meso-cyclone.
"""


def add_feature(ax):
    """plot geographical and political boundaries in matplotlib axes
    """
    import cartopy.feature as cfeature
    ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.1, edgecolor='0.1',zorder=1)

def radar_ax_circ(ax, radar_lat, radar_lon):
    '''plot azimuth lines and range circles around a given radar
    '''
    import numpy as np
    import cartopy.crs as ccrs
    import domutils.geo_tools as geo_tools

    #cartopy transform for latlons
    proj_pc = ccrs.PlateCarree()
    
    color=(100./256.,100./256.,100./256.)

    #add a few azimuths lines
    az_lines = np.arange(0,360.,90.)
    ranges   = np.arange(250.)
    for this_azimuth in az_lines:
        lons, lats = geo_tools.lat_lon_range_az(radar_lon, radar_lat, ranges, this_azimuth)
        ax.plot(lons, lats, transform=proj_pc, c=color, zorder=300, linewidth=.3)

    #add a few range circles
    ranges   = np.arange(0,250.,100.)
    azimuths = np.arange(0,361.)#360 degree will be included for full circles
    for this_range in ranges:
        lons, lats = geo_tools.lat_lon_range_az(radar_lon, radar_lat, this_range, azimuths)
        ax.plot(lons, lats, transform=proj_pc, c=color, zorder=300, linewidth=.3)

def main():

    import os, inspect
    import copy
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    
    # imports from domutils
    import domutils.legs as legs
    import domutils.geo_tools   as geo_tools
    import domutils.radar_tools as radar_tools

    #missing values ane the associated color
    missing  = -9999.
    missing_color = 'grey_160'
    undetect = -3333.
    undetect_color = 'grey_180'

    #file to read
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir  = os.path.dirname(currentdir) #directory where this package lives
    odim_file = parentdir + '/test_data/odimh5_radar_volume_scans/2019071120_24_ODIMH5_PVOL6S_VOL.qc.casbv.h5'

    #Read a PPI from a volume scan in the ODIM H5 format
    #we want the PPI with a nominal elevation of 0.4 degree
    #we retrieve reflectivity (dbzh) and Doppler velocity (vradh) and the Depolarization ratio (dr)
    #the reader computes the lat/lon of data points in the PPI for you
    out_dict = radar_tools.read_h5_vol(odim_file=odim_file, 
                                       elevations=[0.4], 
                                       quantities=['dbzh','vradh','dr'],
                                       no_data=missing, undetect=undetect,
                                       include_quality=True,
                                       latlon=True)
    #radar properties
    radar_lat    = out_dict['radar_lat']
    radar_lon    = out_dict['radar_lon']
    #PPIs
    # You can see the quantities available in the dict with 
    # print(out_dict['0.4'].keys())
    reflectivity = out_dict['0.4']['dbzh']
    doppvelocity = out_dict['0.4']['vradh']
    dr           = out_dict['0.4']['dr']
    tot_qi       = out_dict['0.4']['quality_qi_total']
    latitudes    = out_dict['0.4']['latitudes']
    longitudes   = out_dict['0.4']['longitudes']


    #
    #Quality controls on Doppler velocity
    #pixel is considered weather is DR < 12 dB
    weather_target = np.where( dr < -12., 1, 0) 
    #not a weather target when DR is missing
    weather_target = np.where( np.isclose(dr, missing),  0, weather_target)  
    #not a weather target when DR is undetect
    weather_target = np.where( np.isclose(dr, undetect), 0, weather_target)  
    #a 3D representation of a boxcar filter see radar_tools API for docs on this function
    #5x5 search area in polar coordinates
    remapped_data_5 = radar_tools.median_filter.remap_data(weather_target, window=5, mode='wrap')
    #if less than 12 points (half the points in a 5x5 window) have good dr, pixel is marked as clutter
    is_clutter = np.where(np.sum(remapped_data_5, axis=2) <= 12, True, False)
    #3x3 search area in polar coordinates
    remapped_data_3 = radar_tools.median_filter.remap_data(weather_target, window=3, mode='wrap')
    #if less than 9 points (all the points in a 3x3 window) have good dr, pixel is marked as clutter
    is_clutter = np.where(np.sum(remapped_data_3, axis=2) < 9, True, is_clutter)
    #
    doppvelocity_qc = copy.deepcopy(doppvelocity)
    #DR filtering only applied to points with reflectivities < 35 dB
    doppvelocity_qc = np.where( np.logical_and(is_clutter , reflectivity < 35.) , undetect, doppvelocity_qc)
    #add filtering using total quality index
    doppvelocity_qc = np.where( tot_qi <  0.2 ,                                   undetect, doppvelocity_qc)


    #pixel density of panels in figure
    ratio = 1.
    hpix = 800.       #number of horizontal pixels E-W
    vpix = ratio*hpix #number of vertical pixels   S-N
    img_res = (int(hpix),int(vpix))
    
    #cartopy Rotated Pole projection
    pole_latitude=90.
    pole_longitude=0.
    proj_rp = ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    #plate carree 
    proj_pc = ccrs.PlateCarree()

    #a domain ~250km around the Montreal area where the radar is
    lat_0 = 45.7063
    delta_lat = 2.18
    lon_0 = -73.85
    delta_lon = 3.12
    map_extent=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  

    #a smaller domain for a closeup that will be inlaid in figure
    lat_0 = 46.4329666
    delta_lat = 0.072666
    lon_0 = -75.00555
    delta_lon = 0.104
    map_extent_close=[lon_0-delta_lon, lon_0+delta_lon, lat_0-delta_lat, lat_0+delta_lat]  
    #a circular clipping mask for the closeup axes
    x = np.linspace(-1., 1, int(hpix))
    y = np.linspace(-1., 1, int(vpix))
    xx, yy = np.meshgrid(x, y, indexing='ij')
    clip_alpha = np.where( np.sqrt(xx**2.+yy**2.) < 1., 1., 0. )
    #a circular line around the center of the closeup window
    radius=8. #km
    azimuths = np.arange(0,361.)#360 degree will be included for full circles
    closeup_lons, closeup_lats = geo_tools.lat_lon_range_az(lon_0, lat_0, radius, azimuths)
    #a line 5km long for showing scale in closeup insert
    azimuth = 90 #meteorological angle
    distance = np.linspace(0,5.,50)#360 degree will be included for full circles
    scale_lons, scale_lats = geo_tools.lat_lon_range_az(lon_0-0.07, lat_0-0.04, distance, azimuth)
    

    #point density for figure
    mpl.rcParams['figure.dpi'] = 100.   #crank this up for high def images

    mpl.rcParams.update({'font.size': 25})
    mpl.rcParams.update({'font.family':'Latin Modern Roman'})


    # dimensions for figure panels and spaces
    # all sizes are inches for consistency with matplotlib
    fig_w = 13.5           # Width of figure
    fig_h = 12.5           # Height of figure
    rec_w = 5.             # Horizontal size of a panel
    rec_h = ratio * rec_w  # Vertical size of a panel
    sp_w = .5              # horizontal space between panels
    sp_h = .8              # vertical space between panels
    fig = plt.figure(figsize=(fig_w,fig_h))
    xp = .02               #coords of title (axes normalized coordinates)
    yp = 1.02
    #coords for the closeup  that is overlayed 
    x0 = .55               #x-coord of bottom left position of closeup (axes coords)
    y0 = .55               #y-coord of bottom left position of closeup (axes coords)
    dx = .4                #x-size of closeup axes (fraction of a "regular" panel)
    dy = .4                #y-size of closeup axes (fraction of a "regular" panel)
    #normalize sizes to obtain figure coordinates (0-1 both horizontally and vertically)
    rec_w = rec_w / fig_w
    rec_h = rec_h / fig_h
    sp_w  = sp_w  / fig_w
    sp_h  = sp_h  / fig_h

    #instantiate objects to handle geographical projection of data
    proj_inds = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
                                   extent=map_extent,  dest_crs=proj_rp,
                                   extend_x=False, extend_y=True,
                                   image_res=img_res,  missing=missing)
    #for closeup image
    proj_inds_close = geo_tools.ProjInds(src_lon=longitudes, src_lat=latitudes,
                                         extent=map_extent_close,  dest_crs=proj_rp,
                                         extend_x=False, extend_y=True,
                                         image_res=img_res,  missing=missing)


    #
    #Reflectivity
    #
    #axes for this plot
    pos = [sp_w, sp_h+(sp_h+rec_h), rec_w, rec_h]
    ax = fig.add_axes(pos, projection=proj_rp)
    ax.spines['geo'].set_linewidth(0.3)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_rp)
    ax.set_aspect('auto')

    ax.annotate('Qced Reflectivity', size=30,
                xy=(xp, yp), xycoords='axes fraction')
    
    # colormapping object for reflectivity
    map_reflectivity = legs.PalObj(range_arr=[0.,60], 
                                   n_col=6,
                                   over_high='extend',
                                   under_low='white', 
                                   excep_val=[missing,       undetect], 
                                   excep_col=[missing_color, undetect_color])

    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(reflectivity)
    
    #plot data & palette
    map_reflectivity.plot_data(ax=ax, data=proj_data, zorder=0,
                               palette='right', 
                               pal_units='[dBZ]', pal_format='{:3.0f}')  
    
    #add political boundaries
    add_feature(ax)

    #radar circles and azimuths
    radar_ax_circ(ax, radar_lat, radar_lon)

    #circle indicating closeup area
    ax.plot(closeup_lons, closeup_lats, transform=proj_pc, c=(0.,0.,0.), zorder=300, linewidth=.8)

    #arrow pointing to closeup
    ax.annotate("", xy=(0.33, 0.67), xytext=(.55, .74),  xycoords='axes fraction', 
                arrowprops=dict(arrowstyle="<-"))

    #
    #Closeup of reflectivity 
    #
    pos = [sp_w+x0*rec_w, sp_h+(sp_h+rec_h)+y0*rec_h, dx*rec_w, dy*rec_h]
    ax2 = fig.add_axes(pos, projection=proj_rp, label='reflectivity overlay')
    ax2.set_extent(proj_inds_close.rotated_extent, crs=proj_rp)
    ax2.spines['geo'].set_linewidth(0.0)  #no border line
    ax2.set_facecolor((1.,1.,1.,0.))      #transparent background
    
    #geographical projection of data into axes space
    proj_data = proj_inds_close.project_data(reflectivity)
    
    #RGB values for data to plot
    closeup_rgb = map_reflectivity.to_rgb(proj_data)

    #get corners of image in data space
    extent_data_space = ax2.get_extent()

    ## another way of doing the same thing is to get an object that convers axes coords to data coords
    ## this method is more powerfull as it will return data coords of any points in axes space
    #transform_data_to_axes = ax2.transData + ax2.transAxes.inverted()
    #transform_axes_to_data = transform_data_to_axes.inverted()
    #pts = ((0.,0.),(1.,1.)) #axes space coords
    #pt1, pt2 = transform_axes_to_data.transform(pts)
    #extent_data_space = [pt1[0],pt2[0],pt1[1],pt2[1]]
    
    #add alpha channel (transparency) to closeup image 
    rgba = np.concatenate([closeup_rgb/255.,clip_alpha[...,np.newaxis]], axis=2)

    #plot image
    ax2.imshow(rgba, interpolation='nearest', 
               origin='upper', extent=extent_data_space, zorder=100)
    ax2.set_aspect('auto')

    #circle indicating closeup area
    circle = ax2.plot(closeup_lons, closeup_lats, transform=proj_pc, c=(0.,0.,0.), zorder=300, linewidth=1.5)
    #prevent clipping of the circle we just drawn
    for line in ax2.lines:
        line.set_clip_on(False)


    #
    #Quality Controlled Doppler velocity
    #
    #axes for this plot
    pos = [sp_w+(sp_w+rec_w+1./fig_w), sp_h+(sp_h+rec_h), rec_w, rec_h]
    ax = fig.add_axes(pos, projection=proj_rp)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_rp)
    ax.set_aspect('auto')

    ax.annotate('Qced Doppler velocity', size=30,
                xy=(xp, yp), xycoords='axes fraction')

    #from https://colorbrewer2.org
    brown_purple=[[ 45,  0, 75],
                  [ 84, 39,136],
                  [128,115,172],
                  [178,171,210],
                  [216,218,235],
                  [247,247,247],
                  [254,224,182],
                  [253,184, 99],
                  [224,130, 20],
                  [179, 88,  6],
                  [127, 59,  8]]
    range_arr = [-48.,-40.,-30.,-20,-10.,-1.,1.,10.,20.,30.,40.,48.]

    map_dvel = legs.PalObj(range_arr=range_arr, 
                           color_arr = brown_purple,
                           solid='supplied',
                           excep_val=[missing, undetect], 
                           excep_col=[missing_color, undetect_color])

    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(doppvelocity_qc)

    #plot data & palette
    map_dvel.plot_data(ax=ax,data=proj_data, zorder=0,
                       palette='right', pal_units='[m/s]', pal_format='{:3.0f}')   #palette options
    
    #add political boundaries
    add_feature(ax)

    #radar circles and azimuths
    radar_ax_circ(ax, radar_lat, radar_lon)

    #circle indicating closeup area
    ax.plot(closeup_lons, closeup_lats, transform=proj_pc, c=(0.,0.,0.), zorder=300, linewidth=.8)

    #arrow pointing to closeup
    ax.annotate("", xy=(0.33, 0.67), xytext=(.55, .74),  xycoords='axes fraction', 
                arrowprops=dict(arrowstyle="<-"))

    #
    #Closeup of Doppler velocity 
    #
    pos = [sp_w+1.*(sp_w+rec_w+1./fig_w)+x0*rec_w, sp_h+(sp_h+rec_h)+y0*rec_h, dx*rec_w, dy*rec_h]
    ax2 = fig.add_axes(pos, projection=proj_rp, label='overlay')
    ax2.set_extent(proj_inds_close.rotated_extent, crs=proj_rp)
    ax2.spines['geo'].set_linewidth(0.0) #no border line
    ax2.set_facecolor((1.,1.,1.,0.))     #transparent background
    
    #geographical projection of data into axes space
    proj_data = proj_inds_close.project_data(doppvelocity_qc)
    
    #RGB values for data to plot
    closeup_rgb = map_dvel.to_rgb(proj_data)

    #get corners of image in data space
    extent_data_space = ax2.get_extent()
    
    #add alpha channel (transparency) to closeup image 
    rgba = np.concatenate([closeup_rgb/255.,clip_alpha[...,np.newaxis]], axis=2)

    #plot image
    ax2.imshow(rgba, interpolation='nearest', 
               origin='upper', extent=extent_data_space, zorder=100)
    ax2.set_aspect('auto')

    #line indicating closeup area
    circle = ax2.plot(closeup_lons, closeup_lats, transform=proj_pc, c=(0.,0.,0.), zorder=300, linewidth=1.5)
    for line in ax2.lines:
        line.set_clip_on(False)

    #Show scale in inlay
    ax2.plot(scale_lons, scale_lats, transform=proj_pc, c=(0.,0.,0.), zorder=300, linewidth=.8)
    ax2.annotate("5 km", size=18, xy=(.16, .25),  xycoords='axes fraction', zorder=310)


    #
    #DR
    #
    #axes for this plot
    pos = [sp_w, sp_h, rec_w, rec_h]
    ax = fig.add_axes(pos, projection=proj_rp)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_rp)
    ax.set_aspect('auto')

    ax.annotate('Depolarization ratio', size=30,
                xy=(xp, yp), xycoords='axes fraction')

    # Set up colormapping object
    map_dr = legs.PalObj(range_arr=[-36.,-24.,-12., 0.],
                         color_arr=['purple','blue','orange'],
                         dark_pos =['high',  'high','low'],
                         excep_val=[missing,       undetect], 
                         excep_col=[missing_color, undetect_color])

    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(dr)
    
    #plot data & palette
    map_dr.plot_data(ax=ax,data=proj_data, zorder=0,
                     palette='right', pal_units='[dB]', pal_format='{:3.0f}')  
    
    #add political boundaries
    add_feature(ax)

    #radar circles and azimuths
    radar_ax_circ(ax, radar_lat, radar_lon)


    #
    #Total quality index
    #
    #axes for this plot
    pos = [sp_w+(sp_w+rec_w+1./fig_w), sp_h, rec_w, rec_h]
    ax = fig.add_axes(pos, projection=proj_rp)
    ax.set_extent(proj_inds.rotated_extent, crs=proj_rp)
    ax.set_aspect('auto')

    ax.annotate('Total quality index', size=30,
                xy=(xp, yp), xycoords='axes fraction')
    
    # Set up colormapping object
    pastel = [ [[255,190,187],[230,104, 96]],  #pale/dark red
               [[255,185,255],[147, 78,172]],  #pale/dark purple
               [[255,227,215],[205,144, 73]],  #pale/dark brown
               [[210,235,255],[ 58,134,237]],  #pale/dark blue
               [[223,255,232],[ 61,189, 63]] ] #pale/dark green
    map_qi = legs.PalObj(range_arr=[0., 1.],
                         dark_pos='high',
                         color_arr=pastel,
                         excep_val=[missing,       undetect], 
                         excep_col=[missing_color, undetect_color])

    #geographical projection of data into axes space
    proj_data = proj_inds.project_data(tot_qi)
    
    #plot data & palette
    map_qi.plot_data(ax=ax,data=proj_data, zorder=0,
                       palette='right', pal_units='[unitless]', pal_format='{:3.1f}')   #palette options
    
    #add political boundaries
    add_feature(ax)

    #radar circles and azimuths
    radar_ax_circ(ax, radar_lat, radar_lon)

    ##uncomment to save figure
    #plt.savefig('radar_ppi.svg')

if __name__ == '__main__':
    main()

