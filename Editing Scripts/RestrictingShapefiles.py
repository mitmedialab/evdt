#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 15:47:17 2020

@author: jackreid
"""

import shapefile

r = shapefile.Reader('./FormatedShapefiles/Bairros/Bairros_Custom_DEFAULT.shp')


        
        
w = shapefile.Writer('./FormatedShapefiles/Bairros/Bairros_Custom_restricted_DEFAULT.shp')
 
# Copy over the existing fields
fields = r.fields
for name in fields:
    if type(name) == "tuple":
        continue
    else:
        args = name
        w.field(*args)
        
#Copy over the existing shapes and records
for shaperec in r.iterShapeRecords():
    coderp = float(shaperec.record['CODRP'])
    if( (coderp > 4.1) and (coderp != 5.1)):
        print(shaperec.record)
        w.record(*shaperec.record)
        w.shape(shaperec.shape)

# Close and save the altered shapefile
w.close()

r2 = shapefile.Reader('./FormatedShapefiles/Bairros/Bairros_Custom_restricted.shp')