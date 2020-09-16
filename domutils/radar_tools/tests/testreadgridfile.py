#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 16:40:05 2020

@author: dkh018
"""

import pygrib

import matplotlib.pyplot as plt 
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
import numpy as np


pathfile = "/home/dkh018/site4/traitementStageIV/201906-201908_ST4"
namefile = pathfile + "/ST4.2019082000.06h"

#xr.open_dataset(namefile, engine='cfgrib')
gr = pygrib.open(namefile)

grb = gr.select(name="Total Precipitation")[0]


lats, lons = grb.latlons() 

data = grb.values


np.ma.set_fill_value(data, fill_value=-999.)
values = data.filled()

m = Basemap(projection="cyl", llcrnrlon=-120, urcrnrlon=-60,
            llcrnrlat=lats.min(), urcrnrlat=lats.max(),
            resolution='c')

x, y = m(lons, lats)

cs = m.pcolormesh(x, y, data, shading='flat', cmap=plt.cm.gist_ncar_r)

m.drawcoastlines()
m.drawmapboundary()

plt.colorbar(cs, orientation='vertical', shrink=0.5)

plt.show()
