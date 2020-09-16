#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:35:03 2020

@author: dkh018
"""


import os, inspect
import domutils.radar_tools as radar_tools

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


#=============================================
#
# READ THE STAGE IV FILES
#
#=============================================

out_dict = radar_tools.read_stage4_composite(dirdata + \
                                             pathcomposite_st4 + \
                                             namefile_st4)
                                            
accumulation        = out_dict['accumulation']
total_quality_index = out_dict['total_quality_index']
valid_date          = out_dict['valid_date']
print(accumulation.shape)
print(valid_date)
