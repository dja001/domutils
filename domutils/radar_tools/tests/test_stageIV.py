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
# RUN EXAMPLES 
#
#=============================================

# data deposit for the test
pathcomposite_st4 = "/test_data/stage4_composites/"
data_path         = dirdata + pathcomposite_st4

dateformat        = "%Y%m%d%H"


# ***example 1***: 6-h accumulatation from a 6-hour file 
dateinterest     = "2019081918"    # format: YYYYMMDDHH
tps              = "06"            # 01, 06 or 24
data_recipe      = "ST4." + dateformat + "." + tps + 'h'
valid_date       = datetime.datetime.strptime(dateinterest, dateformat)

out_dict_acc_ex1 = radar_tools.get_accumulation(end_date=valid_date,
                                            duration=60*int(tps),
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            desired_quantity="accumulation",
                                            latlon=True)


# ***example 2***: accumulate 3-h precip from a 1-hour files
tps              = "01"            # 01, 06 or 24
dateinterest     = "2020063003"    # format: YYYYMMDDHH
data_recipe      = "ST4." + dateformat + "." + tps + 'h'
valid_date       = datetime.datetime.strptime(dateinterest, dateformat)
  

out_dict_acc_ex2 = radar_tools.get_accumulation(end_date=valid_date,
                                            duration=60*int(3),
                                            data_path=data_path,
                                            data_recipe=data_recipe,
                                            desired_quantity="accumulation",
                                            latlon=True)
