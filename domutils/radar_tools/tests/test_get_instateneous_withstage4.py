#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:35:03 2020

@author: dkh018
"""


import os, inspect
import domutils.radar_tools as radar_tools
import datetime
#=============================================
#
# GET ALL THE DIRECTORIES
#
#=============================================
currentdir  = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir   = os.path.dirname(currentdir) #directory where this package lives
dirdata     = os.path.dirname(os.path.dirname(parentdir))


#=============================================
#
# NAME OF THE STAGE IV FILES
#
#=============================================

pathcomposite_st4 = "/test_data/stage4_composites/"
dateinterest      = "2019081918" # format: YYYYMMDDHH
tps               ="06" # 01, 06 or 24
namefile_st4      = "ST4." + dateinterest + "." + tps + "h" 



data_path   = dirdata + pathcomposite_st4
data_recipe = "ST4.%Y%m%d%H." + tps + 'h'
valid_date  = datetime.datetime(2019, 8, 19, 18)

out_dict = radar_tools.get_instantaneous(valid_date=valid_date,
                                          desired_quantity="precip_rate",
                                          data_path=data_path,
                                          data_recipe=data_recipe,
                                          latlon=True)
    
    
    
    