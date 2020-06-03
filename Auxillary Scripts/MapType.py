#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:02:07 2020

@author: jackreid
"""
class MapType:
    
    def __init__(self, filepaths, **kwargs):
        
        import shapefile
        
        if 'maptype' in kwargs:
            self.maptype = kwargs.pop('maptype')
        else:
            self.maptype = 'shp'
            
        
        self.filepaths = filepaths
        if self.filepaths[0] != []:
            self.filepaths.insert(0, [])
        if self.maptype == 'shp':
            self.shps = []
            for shpname in self.filepaths:
                if shpname == []:
                    self.shps.append([])
                else:
                    self.shps.append(shapefile.Reader(shpname))
        
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = 0
        
        if 'color_metrics' in kwargs:
            self.color_metrics = kwargs.pop('color_metrics')
            # print(self.color_metrics)
            if self.color_metrics[0] != []:
                self.color_metrics.insert(0, [[]])
                # print('a', self.color_metrics)
            for item in self.color_metrics[1:len(self.color_metrics)]:
                if item[0] != []:
                    item.insert(0, [])
                    # print('b', self.color_metrics)
        else:
            self.color_metrics = [[]] * len(self.filepaths)
                
        if 'color_default' in kwargs:
            self.color_default = kwargs.pop('color_default')
        else:
            self.color_default = [0] * len(self.filepaths)
           
        if 'color_titles' in kwargs:
            self.color_titles = kwargs.pop('color_titles')
            if self.color_titles[0] != []:
                self.color_titles.insert(0, [[]])
            for item in self.color_titles[1:len(self.color_titles)]:
                if item[0] != []:
                    item.insert(0, [])
        else:
            self.color_titles = self.color_metrics
            
        
        if 'original_filepaths' in kwargs:
            self.original_filepaths = kwargs.pop('original_filepaths')
            if self.original_filepaths[0] != []:
                self.original_filepaths.insert(0, [])
            if self.maptype == 'shp':
                self.original_shps = []
                for item in self.original_filepaths:
                    if item != []:
                        self.original_shps.append(shapefile.Reader(item))
        else:
            self.original_filepaths = [] * len(self.filepaths)
            
if str.__eq__(__name__, '__main__'):    
    zone_filepaths = [[], './FormatedShapefiles/Bairros/Bairros_Custom_restricted.shp']
    
            
    zone_color_metrics = [ [ [], 'POPDEN', 'EmpRate', 'AgriRate', 'Zone_TypeN'] ]
    
    zonecolortitles = [[[], 'Densidade Populacional (pop/km^2)', 
                        'Taxa de Emprego (emp/pop)', 
                        'Taxa de Emprego Agrícola (agrí/emp)', 
                        'Estado de Conservação']]
    defaultzonefilepath = ['./FormatedShapefiles/Bairros/Bairros_Custom_restricted_DEFAULT.shp']
    zones = MapType(zone_filepaths, 
        color_metrics = zone_color_metrics, 
        color_titles = zonecolortitles, 
        original_filepaths = defaultzonefilepath, 
        maptype='shp')
            
            
    # mapfilepaths = [[], "./basemap.png", "./map.jpg", "./mangrove_health.png" ]
    # mapimgs = MapType(mapfilepaths, 
    #                        maptype='img')
 


# mangrovenames = [ [], './FormatedShapefiles/Mangroves/m_loss.shp', 
#                   './FormatedShapefiles/Mangroves/m_health.shp',
#                   ]
# mangrovecolors = [ [ [], 'mangrovelo'], [[], 'mangroveHe'] ]
# mangrovecolortitles =  [[[], 'Perda de Manguezais'], [[], 'Saúde dos Manguezais']]
# overlays = MapType(mangrovenames, 
#               default = 0,
#               color_metrics = mangrovecolors, 
#               color_default = [0, 0, 0],
#               color_titles = mangrovecolortitles, 
#               maptype='shp')
        
       