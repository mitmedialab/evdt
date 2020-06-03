#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 15:26:31 2020

@author: jackreid
"""

def ShapeFileEditer(shppath, writepath):
    """Reads and copies a shapefile to a new shapefile.
        Args:
           shpfilepath: file path to the input shapefile
           writepath: destination and title of the output shapefile
                           
        Returns:
            N/A
        """
        
    import shapefile
   
    r = shapefile.Reader(shppath)
    w = shapefile.Writer(writepath)
 
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
        if shaperec.record['codap'] == '4' or shaperec.record['codap'] == '5':
            w.record(*shaperec.record)
            w.shape(shaperec.shape)
    
    # Close and save the altered shapefile
    w.close()
    
    
ShapeFileEditer('./FormatedShapefiles/Planning Zones/Zonas_base.shp', './FormatedShapefiles/Planning Zones/Zonas_restricted.shp')