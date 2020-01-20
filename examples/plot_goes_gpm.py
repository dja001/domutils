"""
GPM precip rate measurements over Goes Albedo
==============================================

   Many things are demonstrated in this example:
        - The superposition of two data types on one figure
        - Plotting the same data on different domains
        - The use of the *average* keyword for displaying high resolution
          data onto a coarser grid

"""
import numpy as np
import os, inspect
import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# In your scripts use something like :
import domutils.geo_tools as geo_tools
import domutils.legs      as legs 

def makePanel(fig, pos, imgRes, mapExtent, missing,
              dprLats, dprLons, dprPR, 
              goesLats, goesLons, goesAlbedo,
              mapPR, mapGoes, 
              mapExtentSmall=None,includeZero=True,
              averageDPR=False):
    ''' Generic function for plotting data on an ax 

        Data is displayed with specific projection settings

    '''
    
    #cartopy crs for lat/lon (ll) and the image (Miller)
    proj_ll  = ccrs.Geodetic()
    proj_mil = ccrs.Miller()
    
    #global 
    #instantiate object to handle geographical projection of data
    # 
    #Note the average=True for GPM data, high resolution DPR data
    # will be averaged within coarser images pixel tiles
    projIndsDPR = geo_tools.projInds(srcLon=dprLons,   srcLat=dprLats,
                                     extent=mapExtent, destCrs=proj_mil, 
                                     average=averageDPR, missing=missing,
                                     image_res=imgRes)
    projIndsGoes = geo_tools.projInds(srcLon=goesLons,   srcLat=goesLats,
                                      extent=mapExtent, destCrs=proj_mil,
                                      image_res=imgRes, missing=missing)
    
    ax = fig.add_axes(pos, projection=proj_mil)
    ax.set_extent(mapExtent)
    
    #geographical projection of data into axes space
    projDataPR   = projIndsDPR.project_data(dprPR)
    projDataGoes = projIndsGoes.project_data(goesAlbedo)
    
    #get RGB values for each data types
    precipRGB =   mapPR.to_rgb(projDataPR)
    albedoRGB = mapGoes.to_rgb(projDataGoes)
    
    #blend the two images by hand
    #image will be opaque where reflectivity > 0
    if includeZero:
        alpha = np.where(projDataPR >= 0., 1., 0.)  #include zero
    else:
        alpha = np.where(projDataPR >  0., 1., 0.)  #exclude zero
    combinedRGB = np.zeros(albedoRGB.shape,dtype='uint8')
    for zz in np.arange(3):
        combinedRGB[:,:,zz] = (1. - alpha)*albedoRGB[:,:,zz] + alpha*precipRGB[:,:,zz]
    
    #plot image w/ imshow
    x11, x22 = ax.get_xlim()    #get image limits in Cartopy data coordinates
    y11, y22 = ax.get_ylim()
    dum = ax.imshow(combinedRGB, interpolation='nearest', extent=[x11,x22,y11,y22])
    ax.set_aspect('auto')
    
    #add political boundaries
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='yellow',zorder=1)

    #plot extent of the small domain that will be displayed in next panel
    if mapExtentSmall is not None :
        brightRed = np.array([255.,0.,0.])/255.
        w = mapExtentSmall[0]
        e = mapExtentSmall[1]
        s = mapExtentSmall[2]
        n = mapExtentSmall[3]
        ax.plot([w, e, e, w, w], [s,s,n,n,s],transform=proj_ll, color=brightRed, linewidth=5 )


def main():


    #recover previously prepared data
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir) #directory where this package lives
    source_file = parentdir + '/test_data/goes_gpm_data.pickle'
    with open(source_file, 'rb') as f:
        dataDict = pickle.load(f)
    dprLats    = dataDict['dprLats']        
    dprLons    = dataDict['dprLons']       
    dprPR      = dataDict['dprPrecipRate']  
    goesLats   = dataDict['goesLats']       
    goesLons   = dataDict['goesLons']       
    goesAlbedo = dataDict['goesAlbedo']     

    #missing value
    missing = -9999.

    #Figure position stuff
    picH = 5.4
    picW = 8.8
    palSp = .1/picW
    palW = .25/picW
    ratio = .8
    sqSZ = 6.
    recW =       sqSZ/picW
    recH = ratio*sqSZ/picH
    spW = .1/picW
    spH = 1.0/picH
    x1 = .1/picW 
    y1 = .2/picH 

    #number of pixels of the image that will be shown
    hpix = 400.       #number of horizontal pixels
    vpix = ratio*hpix #number of vertical pixels
    imgRes   = (int(vpix),int(hpix))

    #point density for figure
    mpl.rcParams.update({'font.size': 17})
    #Use this to make text editable in svg files
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['svg.fonttype'] = 'none'
    #Hi def figure
    mpl.rcParams['figure.dpi'] = 400

    #instantiate figure
    fig = plt.figure(figsize=(picW,picH))

    # Set up colormapping objects
    
    #For precip rates
    ranges = [0.,.4,.8,1.5,3.,6.,12.]
    mapPR = legs.pal_obj(range_arr=ranges,
                         n_col=6,
                         over_high='extend',
                         under_low='white', 
                         excep_val=[missing,0.],excep_col=['grey_230','white'])

    #For Goes albedo
    mapGoes = legs.pal_obj(range_arr=[0.,.6],
                           over_high = 'extend',
                           color_arr='b_w', dark_pos='low',
                           excep_val=[-1, missing],excep_col=['grey_130','grey_130'])

    #Plot data on a domain covering North-America
    #
    #
    mapExtent = [-141.0, -16., -7.0, 44.0]
    #position
    x0 = x1
    y0 = y1
    pos = [x0,y0,recW,recH]
    #border of smaller domain to plot on large figure
    mapExtentSmall = [-78., -68., 12.,22.]
    #
    makePanel(fig, pos, imgRes, mapExtent,  missing,
              dprLats, dprLons, dprPR, 
              goesLats, goesLons, goesAlbedo,
              mapPR, mapGoes, mapExtentSmall,
              averageDPR=True)



    #instantiate 2nd figure
    fig2 = plt.figure(figsize=(picW,picH))
    # sphinx_gallery_thumbnail_number = 2

    #Closeup on a domain in the viscinity of Haiti
    #
    #
    mapExtent = mapExtentSmall
    #position
    x0 = x1
    y0 = y1
    pos = [x0,y0,recW,recH]
    #
    makePanel(fig2, pos, imgRes, mapExtent,  missing,
              dprLats, dprLons, dprPR, 
              goesLats, goesLons, goesAlbedo,
              mapPR, mapGoes, includeZero=False)


    #plot palettes 
    x0 = x0 + recW + palW
    y0 = y0
    mapPR.plot_palette(pal_pos=[x0,y0,palW,recH],
                       pal_units='[mm/h]', 
                       pal_format='{:2.1f}', 
                       equal_legs=True)

    x0 = x0 + 5.*palW 
    y0 = y0
    mapGoes.plot_palette(pal_pos=[x0,y0,palW,recH],
                         pal_units='unitless',
                         pal_format='{:2.1f}')

    #uncomment to save figure
    #picName = 'goes_plus_gpm.svg'
    #plt.savefig(picName,dpi=400)


if __name__ == '__main__':
    main()

