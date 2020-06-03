#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:57:03 2020

@author: jackreid
"""
import shapefile
import ShapefileFormatter

shppath = './FormatedShapefiles/Bairros_with_Population4.shp'
datapath = './FormatedData/TotalEmployment_2017.xlsx'
writepath = './FormatedShapefiles/Bairros_with_Population5.shp'

testr = shapefile.Reader(shppath)

ShapefileFormatter.ShapefileFormatter(shppath, datapath, 'Emp', 'Emp', writepath)

r = shapefile.Reader(writepath)


