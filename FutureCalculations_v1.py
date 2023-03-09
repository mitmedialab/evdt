#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:15:07 2020

@author: jackreid
"""
import shapefile
import shapely.ops
import shapely.geometry
import tkinter as tk
from tkinter.ttk import Progressbar

def mangrovehealthchange(root, zoneshp, mangrovehealthshp):
    writepath = './FormatedShapefiles/Mangroves/m_health_FUTURE.shp'
    w = shapefile.Writer(writepath)
 
    totalshapes = len(mangrovehealthshp.shapes())
    i=0
    # Copy over the existing fields
    fields = mangrovehealthshp.fields
    for name in fields:
        if type(name) == "tuple":
            continue
        else:
            args = name
            w.field(*args)
            
    progresswindow = tk.Toplevel(root)
    progresswindow.geometry("+400+350")
    progresslabel = tk.Label(progresswindow, text='Progresso do Cálculo', font=('Arial',24))
    progresslabel.pack(pady=10)
    progress = Progressbar(progresswindow, orient = 'horizontal', 
              length = 1000, mode = 'determinate') 
    progress.pack(pady = 10) 

    for mangroveshaperec in mangrovehealthshp.iterShapeRecords():
        i+=1
        if i%100 == 0:
            progressvalue = i/totalshapes*100
            print('Progress: ', progressvalue, '%')
            progress['value'] = progressvalue
            root.update_idletasks()
            
        mangroveboundary = mangroveshaperec.shape
        mangroveboundary = shapely.geometry.shape(mangroveboundary)
        health = mangroveshaperec.record['mangroveHe']
        
        for zoneshaperec in zoneshp.iterShapeRecords():
            zoneboundary = zoneshaperec.shape
            zoneboundary = shapely.geometry.shape(zoneboundary)
            if mangroveboundary.intersects(zoneboundary):
                zonestatus_str = zoneshaperec.record['A_grupo']
                if zonestatus_str == 'Tombamento':
                    zonestatus = 3
                elif zonestatus_str == 'Zona de Amortecimento':
                    zonestatus = 2
                if zonestatus_str == 'Uso Sustentável':
                    zonestatus = 1
                elif zonestatus_str == 'Proteção Integral':
                    zonestatus = 3
                
                if zonestatus == 0:
                    health = health + 2
                elif zonestatus == 1:
                    health = health + 1
                elif zonestatus == 2:
                    if health < 3:
                        health = health + 1
                    elif health > 4:
                        health = health - 1
                    else:
                        health = health
                else:
                    health = health - 1
                
                if health > 6:
                    health = 6
                elif health < 0:
                    health = 0
                break
        
        mangroveshaperec.record['mangroveHe'] = health
        w.record(*mangroveshaperec.record)
        w.shape(mangroveshaperec.shape)
        
    
    # Close and save the altered shapefile
    w.close()
    progresswindow.destroy()
    return shapefile.Reader(writepath)

    

            
    
    
    
    
    
    
    
    
    
    # for shaperec in self.zone_default.iterShapeRecords():
    #         boundary = shaperec.shape # get a boundary polygon
    #         if shapely.geometry.Point((geox, geoy)).within(shapely.geometry.shape(boundary)): # make a point and see if it's in the polygon
    #             #Pull data from shapefile
    #             name = shaperec.record[1] # get the second field of the corresponding record
    #             population = shaperec.record['POP']
    #             zonetype = shaperec.record['Zone_Type']
    #             emp = shaperec.record['Emp']
    #             agri= shaperec.record['Agri']
    #             print("The point is in", name)
                
    #             #Calculate area of zone
    #             geom = shapely.geometry.polygon.Polygon(boundary.points)
    #             geom_area = shapely.ops.transform(
    #                     partial(
    #                         pyproj.transform,
    #                         pyproj.Proj(init='EPSG:4326'),
    #                         pyproj.Proj(init='epsg:3857')),
    #                         shapely.geometry.shape(geom))
    #             area = geom_area.area
                
    #             #Calculate area of mangrove loss in zone
    #             area_of_loss = 0;
    #             for shaperec in self.shape_mangroveloss.iterShapeRecords():
    #                 m_boundary = shaperec.shape # get a boundary polygon
    #                 m_boundary_shape = shapely.geometry.shape(m_boundary)
    #                 if m_boundary_shape.intersects(shapely.geometry.shape(boundary)):
    #                     m_geom = shapely.geometry.polygon.Polygon(m_boundary.points)
    #                     m_geom_area = shapely.ops.transform(
    #                         partial(
    #                             pyproj.transform,
    #                             pyproj.Proj(init='EPSG:4326'),
    #                             pyproj.Proj(init='epsg:3857')),
    #                         shapely.geometry.shape(m_geom))
    #                     area_of_loss = area_of_loss + m_geom_area.area