#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 15:37:14 2020

@author: jackreid
"""



from shapely.geometry import Point
from shapely.ops import transform

import pyproj
import pyproj.enums
##
#import sys
#print(sys.modules.keys())
#
#
#
#if 'pyproj' not in sys.modules:
#    import pyproj
#    print('importing pyproj')
#    
#if 'shapely.geometry' not in sys.modules:
#    import shapely
#    from shapely.geometry import Point
#    print('importing Point')
##    
#if 'shapely.ops' not in sys.modules:
#    from shapely.ops import transform
#    print('importing transform')
    
##    
#print(len(sys.modules.keys()))

foo = pyproj.enums.TransformDirection.FORWARD


wgs84_pt = Point(-72.2495, 43.886)

wgs84 = pyproj.CRS('EPSG:4326')
utm = pyproj.CRS('EPSG:32618')

project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
utm_point = transform(project, wgs84_pt)
print(utm_point)