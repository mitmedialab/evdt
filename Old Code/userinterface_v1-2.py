#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:11:58 2020

@author: jackreid
"""

import tkinter as tk
import PIL as pil
from PIL import ImageTk
from PIL import Image
import tkinter.font
import MapWindow_v2
import MapWindow
import calculate_area
import pyproj
import shapefile
import ShapefileFormatter
# import shapely.geometry
import shapely
from functools import partial
import shapely.ops
import shapely.geometry


class EVDT(tk.Canvas):

# =============================================================================
#     Initiating User Interface
# =============================================================================
    
    mapfilepaths = ["./basemap.png", "./map.jpg", "./mangrove_health.png" ]
    map_base = mapfilepaths[0]
    map_mangrove_extent = mapfilepaths[1]
    map_mangrove_health = mapfilepaths[2]
    
    
    shapefilepaths = ['./FormatedShapefiles/Bairros_with_Population2.shp', './FormatedShapefiles/Mangroves/mangrovelossshape.shp']
    shape_bairros = shapefilepaths[0]
    shape_mangroveloss = shapefilepaths[1]
    
    zoneshape = shapefile.Reader(shape_bairros) #open the shapefile
    all_shapes = zoneshape.shapes() # get all the polygons
    all_records = zoneshape.records()
    
    
    def __init__(self, root):
        super().__init__(root, bg='white', width=1300, height=800)
        self.zonesetting = tk.IntVar() 
        self.zonesetting.set(1)
        self.mapsetting = tk.IntVar()
        self.mapsetting.set(1)
        # self.mapsetting = 1
        self.shapesetting= 0
        self.mangrovesetting = tk.IntVar()
        self.mangrovesetting.set(0)
        self.tense = 0

        self.frame_map, self.label_date, self.label_real, self.mapimg = self.make_map_window(root)
        self.frame_buttons = self.make_layer_buttons(root)
        self.frame_info, self.list_info, self.list_zone = self.make_info_display(root)
        self.frame_control, self.btn_calculate, self.btn_future = self.make_control(root)
        
        
    def zone_type(self,name):
        zone_window = tk.Toplevel(self)
        zone_window.title('Set Type of Zone')
       
        lbl_text = tk.Label(zone_window, text='Set Type of Zone', font=('Arial',24))
        lbl_text.grid(column=1, row=0)
        
        button1 = tk.Button(zone_window, text='Conservation', command=lambda: self.change_zone_type(name, 'Conservation',zone_window))
        button1.grid(column=0, row=1) 
        button2 = tk.Button(zone_window, text='Semi-Protected', command=lambda: self.change_zone_type(name, 'Semi-Protected',zone_window))
        button2.grid(column=1, row=1) 
        button3 = tk.Button(zone_window, text='Unprotected', command=lambda: self.change_zone_type(name, 'Unprotected',zone_window))
        button3.grid(column=2, row=1)

             
    def change_zone_type(self,name,newtype, parent):

        r1 = shapefile.Reader(self.shape_bairros)
        w1 = shapefile.Writer("./temp.shp")
 
         # Copy over the existing fields
        fields = r1.fields
        for fieldname in fields:
            if type(fieldname) == "tuple":
                continue
            else:
                args = fieldname
                w1.field(*args) 
                
        
        # Copy over exisiting records and geometries, appending MHI to each record
        for shaperec in r1.iterShapeRecords():
            testname = shaperec.record['BAIRRO']
            if name == testname:
                shaperec.record['Zone_Type'] = newtype 
            w1.record(*shaperec.record)
            w1.shape(shaperec.shape)
        
        # Close and save the altered shapefile
        w1.close()
    
        ShapefileFormatter.ShapeFileCopier('./temp', self.shape_bairros)

        self.list_zone.delete(tk.END)
        self.list_zone.insert(tk.END, 'Status: ' + newtype)
        self.list_zone.itemconfig(tk.END, {'bg':'red'})
        parent.destroy()

    
    def print_coords(self, event):
        # print(event.x, event.y)
        event.x, event.y = self.mapimg.canvasx(event.x), self.mapimg.canvasy(event.y)
        geox, geoy = self.mapimg.to_geographical_coordinates(event.x, event.y)
        print(geox, geoy)

        for shaperec in self.zoneshape.iterShapeRecords():
            boundary = shaperec.shape # get a boundary polygon
            if shapely.geometry.Point((geox, geoy)).within(shapely.geometry.shape(boundary)): # make a point and see if it's in the polygon
                name = shaperec.record[1] # get the second field of the corresponding record
                population = shaperec.record[10]
                zonetype = shaperec.record[11]
                print("The point is in", name)
                geom = shapely.geometry.polygon.Polygon(boundary.points)
                geom_area = shapely.ops.transform(
                        partial(
                            pyproj.transform,
                            pyproj.Proj(init='EPSG:4326'),
                            pyproj.Proj(init='epsg:3857')),
                            shapely.geometry.shape(geom))
                area = geom_area.area
                
                area_of_loss = 0;
                
                for shaperec in shapefile.Reader(self.shape_mangroveloss).iterShapeRecords():
                    m_boundary = shaperec.shape # get a boundary polygon
                    m_boundary_shape = shapely.geometry.shape(m_boundary)
                    if m_boundary_shape.intersects(shapely.geometry.shape(boundary)):
                        m_geom = shapely.geometry.polygon.Polygon(m_boundary.points)
                        m_geom_area = shapely.ops.transform(
                            partial(
                                pyproj.transform,
                                pyproj.Proj(init='EPSG:4326'),
                                pyproj.Proj(init='epsg:3857')),
                            shapely.geometry.shape(m_geom))
                        area_of_loss = area_of_loss + m_geom_area.area
                
                
        self.list_zone.delete(1, tk.END)
        self.list_zone.insert(tk.END, 'Bairro:  ' + name)
        self.list_zone.insert(tk.END, 'Population: ' + str(population))
        self.list_zone.insert(tk.END, 'Area of Bairro (km^2): ' + str(round(area/(1000*1000))))
        self.list_zone.insert(tk.END, 'Lost Mangroves (m^2): ' + str(round(area_of_loss)))
        self.list_zone.insert(tk.END, 'Status: ' + str(zonetype))
        self.list_zone.itemconfig(tk.END, {'bg':'red'})

        self.list_zone.bind("<Double-Button-1>", lambda e: self.zone_type(name))




                
        


# =============================================================================
#  Generate Each Component of User Interface                
# =============================================================================
            
    def make_layer_buttons(self, root):
         # =======================================
            # MAP LAYERS
            #Notes: Need to add commands to each of the Checkbuttons that update the map appropriately
        
        frame_layer = tk.Frame(root)
        frame_layer.grid(column=0, row=0)
        
        lbl_layers = tk.Label(frame_layer, text='Map Layers', font=('Arial',24))
        lbl_layers.grid(column=0, row=0)
        
        # button1 = tk.Button(frame_layer, text='Base Map', command=lambda: self.replace_map_image(0))
        # button1.grid(column=0, row=1) 
        # button2 = tk.Button(frame_layer, text='Mangrove Extent', command=lambda: self.replace_map_image(1))
        # button2.grid(column=1, row=1) 
        # button3 = tk.Button(frame_layer, text='Mangrove Health', command=lambda: self.replace_map_image(2))
        # button3.grid(column=1, row=2)
        
        # zonebutton = tk.Checkbutton(frame_layer, text='Zones', variable=self.zonesetting, command=lambda: self.check_zones(self.shape_bairros))
        # zonebutton.grid(column=0, row=2)
        
        
        ZoneModes = [
        ("None", 0),
        ("Population Density", 1),
        ("Employment Percent", 2)
        ]

        i = 1
        for text, mode in ZoneModes:
            b = tk.Radiobutton(frame_layer, text=text,
                            variable=self.zonesetting, value=mode)
            b.grid(column=0, row=i)
            i+=1
            
        MapModes = [
        ("None", 0),
        ("Base Map", 1)
        ]

        i = 1
        for text, mode in ZoneModes:
            b = tk.Radiobutton(frame_layer, text=text,
                            variable=self.mapsetting, value=mode)
            b.grid(column=0, row=i)
            i+=1
            
        MangroveModes = [
        ("None", 0),
        ("Mangrove Extent", 1),
        ("Employment Percent", 2)
        ]

        i = 1
        for text, mode in ZoneModes:
            b = tk.Radiobutton(frame_layer, text=text,
                            variable=self.mangrovesetting, value=mode)
            b.grid(column=0, row=i)
            i+=1
            
        
        return frame_layer
    


    def make_map_window(self, root):
        # =======================================
        # MAP WINDOW
        #https://stackoverflow.com/questions/36328547/changing-the-shape-of-tkinter-widgets
        #http://effbot.org/tkinterbook/place.htm
        # =https://github.com/afourmy/pyGISS
        
        
        frame_map = tk.Frame(root)
        frame_map.grid(column=0, row=1)

        mapimg = MapWindow_v2.Map(frame_map,self.shape_bairros,background_image=self.map_base, color_range='POP')
        # mapimg = MapWindow_v2.Map(frame_map,self.shape_bairros,background_image=self.map_base)

        
        
        label_date = tk.Label(frame_map, text='September 2018', font=('Arial', 24), fg='red' )
        label_date.place(relx=1, x=-2, y=2, anchor='ne')
        label_real = tk.Label(frame_map, text='Real Data', font=('Arial', 24), fg='red' )
        label_real.place(relx=1, x=-2, y=35, anchor='ne')
        
        mapimg.bind("<Button-1>", self.print_coords)
        
        return frame_map, label_date, label_real, mapimg


    def make_info_display(self, root):
        # =======================================
        # INFORMATION DISPLAY
        
        frame_info = tk.Frame(root)
        frame_info.grid(column=1, row=1)
        
        lbl_info = tk.Label(frame_info, text='Data Display', font=('Arial',24))
        lbl_info.grid(column=0, row=0)
        
        mangrove_extent = 208080
        mangrove_growth = 2200 
        mangrove_loss = 7270
        mangrove_net = mangrove_growth - mangrove_loss
        mangrove_atrisk = 8560
        
        list_info = tk.Listbox(frame_info, width=50)
        list_info.insert(1, 'Mangrove Extent: ' + str(mangrove_extent) +' ha')
        list_info.insert(2, 'Area of Recent Growth: ' + str(mangrove_growth) + ' ha') 
        list_info.insert(3, 'Area of Recent Loss: ' + str(mangrove_loss) + ' ha') 
        list_info.insert(4, 'Area of At-Risk Mangroves: ' + str(mangrove_atrisk) +' ha') 
        list_info.insert(4, 'Net Change in Extent: ' + str(mangrove_net) +' ha') 
        list_info.insert(4, 'Area of At-Risk Mangroves: ' + str(mangrove_atrisk) +' ha') 
        list_info.grid(column=0, row=1) 
        
        
        
        lbl_zone = tk.Label(frame_info, text='Zone Information', font=('Arial',24))
        lbl_zone.grid(column=0, row=2)
        
        list_zone = tk.Listbox(frame_info, width=50)
        list_zone.insert(1, '')
        list_zone.insert(2, '') 
        # list_zone.insert(3, '') 
        list_zone.grid(column=0, row=3) 
        
        
        return frame_info, list_info, list_zone

        
    def make_control(self, root):
        # =======================================
        # CONTROL BUTTONS
        
        frame_control = tk.Frame(root)
        frame_control.grid(column=0, row=2)
        
        btn_zones = tk.Button(frame_control, text="Planning Zones")
        btn_zones.grid(column=0, row=0)
        btn_calculate = tk.Button(frame_control, text="Calculate")
        btn_calculate.grid(column=1, row=0)
        btn_future = tk.Button(frame_control, text="Show Simulated Future", command= lambda: self.show_future())
        btn_future.grid(column=2, row=0)
        return frame_control, btn_calculate, btn_future
    
# =============================================================================
#     Define Map Layer Button Commands
# =============================================================================
    
    def replace_map_image(self, mapsetting):
        self.mapsetting = mapsetting
        shapename = self.shapefilepaths[self.shapesetting]
        mapname = self.mapfilepaths[mapsetting]
        
        slaveitems = self.frame_map.slaves()
        for item in slaveitems:
            item.destroy()    
        griditems = self.frame_map.grid_slaves()
        for item in griditems:
            item.destroy()
             
        if self.zonesetting.get() == 1:
            self.mapimg = MapWindow_v2.Map(self.frame_map,shapename, background_image=mapname)
            self.mapimg.bind("<Button-1>", self.print_coords)
        else:
            load = pil.Image.open(self.mapfilepaths[mapsetting])
            load = load.resize((1300, 800), Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)
            img = tk.Label(self.frame_map, image=render)
            img.image = render
            img.grid(column=0, row=0)
            
        self.label_date.lift()
        self.label_real.lift()
        
        
    def replace_map_shape(self, shapesetting):
        self.shapesetting = shapesetting
        mapname = self.mapfilepaths[self.mapsetting]
        shapename = self.shapefilepaths[shapesetting]
        
        slaveitems = self.frame_map.slaves()
        for item in slaveitems:
            item.destroy()
            
        griditems = self.frame_map.grid_slaves()
        for item in griditems:
            item.destroy()
            
        self.mapimg = MapWindow_v2.Map(self.frame_map, shapename, background_image=mapname)
        self.mapimg.bind("<Button-1>", self.print_coords)
        
        self.label_date.lift()
        self.label_real.lift()
        

    def check_zones(self, shapename):
        varstate = self.zonesetting.get()
        mapname = self.mapfilepaths[self.mapsetting]
        
        slaveitems = self.frame_map.slaves()
        for item in slaveitems:
            item.destroy()
            
        griditems = self.frame_map.grid_slaves()
        for item in griditems:
            item.destroy()
        
        if varstate == 1:
           self.mapimg = MapWindow_v2.Map(self.frame_map, shapename, background_image=mapname)
           self.mapimg.bind("<Button-1>", self.print_coords)
        else:
            load = pil.Image.open(mapname)
            load = load.resize((1300, 800), Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)
            img = tk.Label(self.frame_map, image=render)
            img.image = render
            img.grid(column=0, row=0)
        
        self.label_date.lift()
        self.label_real.lift() 
        
# =============================================================================
#   Define Control Panel Button Commands  
# =============================================================================
                
    def change_tense_labels(self, newtense):
        self.tense = newtense
        
        if self.tense == 0:
            self.label_date.config(text='September 2018')
            self.label_real.config(text='Real Data')
        else:
            self.label_date.config(text='September 2028')
            self.label_real.config(text='SIMULATION [NOT ACTUAL]')
    
    def show_future(self):
        if self.tense == 0:
            self.change_tense_labels(1)
            self.btn_future.config(text='Show Present')
        else:
            self.change_tense_labels(0)
            self.btn_future.config(text='Show Simulated Future ')
            
            
        


if str.__eq__(__name__, '__main__'):
       
    window = tk.Tk()
    window.title('EVDT Interactive Simulation')
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=20)
    EVDT_Model = EVDT(window)
    window.mainloop()



