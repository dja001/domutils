#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:35:03 2020

@author: dkh018
"""


import os, inspect
import domutils.radar_tools as radar_tools


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir) #directory where this package lives

out_dict = radar_tools.read_stage4_composite(parentdir + \
                                             '/test_data/stage4_composites/ST4.2019081918.06h')
          


 >>> accumulation        = out_dict['accumulation']
           >>> total_quality_index = out_dict['total_quality_index']
           >>> valid_date          = out_dict['valid_date']
           >>> print(accumulation.shape)
           (1650, 1500)
           >>> print(valid_date)
           2019-08-20 00:00:00+00:00