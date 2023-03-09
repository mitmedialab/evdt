#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:54:50 2019

@author: jackreid

http://prj2epsg.org/

"""

import shapefile
from pyproj import Proj, transform
from functools import partial
from shapely.geometry.polygon import Polygon
import shapely.ops as ops
import shapely

r = shapefile.Reader('/home/jackreid/Documents/School/Research/Space Enabled/Code/Decisions/Data/Santiago/Shapefiles/Metro_comunas_simple.shp')

       
        
# Create a new shapefile in memory
w = shapefile.Writer('/home/jackreid/Documents/School/Research/Space Enabled/Code/Decisions/Data/Santiago/Shapefiles/Metro_comunas_simple2.shp')

# Copy over the existing fields
fields = r.fields
for name in fields:
    if type(name) == "tuple":
        continue
    else:
        args = name
        w.field(*args)
        

records = r.records()
for row in records:
    args = row
    w.record(*args)
    
input_projection = Proj(init="epsg:3857")
output_projection = Proj(init="epsg:4326")

geom = r.shapes()

i = 0

for feature in geom:
    i+=1
    progress = i/len(geom)
    print(progress)
    
    if len(feature.parts) == 1:
        # print('single')
        poly_list = []
        for coords in feature.points:
            x, y = coords[0], coords[1]
            new_x, new_y = transform(input_projection, output_projection, x, y)
            poly_coord = [float(new_x), float(new_y)]
            poly_list.append(poly_coord)
        w.poly([poly_list])
    else:
        # print('multiple')
        feature.parts.append(len(feature.points))
        poly_list = []
        parts_counter = 0
        while parts_counter < len(feature.parts) - 1:
            # print(parts_counter)
            coord_count = feature.parts[parts_counter]
            no_of_points = abs(feature.parts[parts_counter] - feature.parts[parts_counter + 1] )
            part_list = []
            end_point = coord_count + no_of_points
            while coord_count < end_point:
                for coords in feature.points[coord_count:end_point]:
                    x, y = coords[0], coords[1]
                    # tranform the coord
                    new_x, new_y = transform(input_projection, output_projection, x, y)
                    # put the coord into a list structure
                    poly_coord = [float(new_x), float(new_y)]
                    # append the coords to the part list
                    part_list.append(poly_coord)
                    coord_count = coord_count + 1
            # append the part to the poly_list
            poly_list.append(part_list)
            parts_counter = parts_counter + 1
        # add the geometry to to new file
        w.poly(poly_list)
    
w.close()




