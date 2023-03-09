#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVDT User Interface Base Script
Generates the EVDT Class and generates the User Interface


Created on Tue Jan  7 15:11:58 2020
@author: jackreid
"""
 
import tkinter as tk
import tkinter.font
import tkinter.ttk
import pyproj
import shapefile
from functools import partial
import shapely.ops
import shapely.geometry
import csv
import os

import sys
sys.path.insert(1, '/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/Auxillary Scripts')

import ShapefileFormatter
import MapWindow_v4 as MapWindow
import FutureCalculations_v1 as FutureCalculations
from MapType_v2 import *
from fieldnamelookup import *

class EVDT(tk.Canvas):

    
# =============================================================================
#     Initiating User Interface
# =============================================================================
    
              
    
    def __init__(self, root):
        """INITIATE EVDT CLASS
    
        Args:
            root: tk window or frame for the EVDT to sit in
               
        Returns:
            N/A
        """
        
        super().__init__(root, bg='white', width=1300, height=800)
        
        
        
    #Define filepaths and shapefile fields of interest
        
        #UNITS OF ANALYSIS (UOA)
        uoa_filepaths = [[], 
                          './FormatedShapefiles/Bairros/Bairros_Custom_restricted.shp',
                          './FormatedShapefiles/Protected Areas/Áreas_Protegidas_editable.shp',
                          './FormatedShapefiles/Planning Zones/Zonas_restricted.shp']
                
        
        default_uoa_filepath = ['./FormatedShapefiles/Bairros/Bairros_Custom_restricted_DEFAULT.shp',
                               './FormatedShapefiles/Protected Areas/Áreas_Protegidas_editable_default.shp',
                               './FormatedShapefiles/Planning Zones/Zonas_restricted_default.shp'
                               ]
        
        #MAP IMAGES
        map_filepaths = [[], "./Map Images/basemap.png", "./Map Images/map.jpg", "./Map Images/mangrove_health.png" ]
    
        #OVERLAYS
        overlay_names = [ [], './FormatedShapefiles/Mangroves/m_loss.shp', 
                         './FormatedShapefiles/Mangroves/m_health.shp',
                         ]
        overlay_colors = [ [ [], 'mangrovelo'], [[], 'mangroveHe']]
        overlay_color_titles =  [ [[], 'Perda de Manguezais'], [[], 'Saúde dos Manguezais'] ]
        
        
        #Create all setting variables and set to default
        self.uoa = MapType(uoa_filepaths, 
                     default = 1,
                     color_default = ['Nenhum', 'POPDEN', 'Nenhum', 'Nenhum'],
                     original_filepaths = default_uoa_filepath, 
                     maptype='shp')
        self.uoa.setting_index = tk.IntVar()
        self.uoa.setting_index.set(self.uoa.default)
        
        self.map_image = MapType(map_filepaths, 
                       default = 1,
                       maptype='img')
        self.map_image.setting_index = tk.IntVar()
        self.map_image.setting_index.set(self.map_image.default)
        
        self.overlay = MapType(overlay_names, 
              default = 0,
              color_metrics = overlay_colors, 
              color_default = [0, 1, 1],
              color_titles = overlay_color_titles, 
              maptype='shp')
        self.overlay.setting_index = tk.IntVar()
        self.overlay.setting_index.set(self.overlay.default)
        self.overlay.color_setting_index = tk.IntVar()
        self.overlay.color_setting_index.set(self.overlay.color_default[self.overlay.default])
        
        self.tense = 0
        self.markerflag = 0


        #Create each component of UI
        self.clickname = []
        self.clickevent = []
        self.frame_buttons = self.make_layer_buttons(root)
        self.frame_map, self.label_date, self.label_real, self.MAP = self.make_map_window(root)
        self.frame_info, self.list_info, self.list_uoa_boxes, self.list_tabparent = self.make_info_display(root)
        self.frame_control, self.btn_calculate, self.btn_future = self.make_control(root)
        
        

# =============================================================================
#  Define Each Component of User Interface                
# =============================================================================
            
    def make_layer_buttons(self, root):
        """CREATE MAP LAYER TOGGLE BUTTONS
    
        Args:
            root: tk window or frame for the buttons to to be situated in.
               
        Returns:
            frame_layer: the frame housing the buttons
        """
            
        #Make Frame
        frame_layer = tk.Frame(root)
        frame_layer.grid(column=0, row=0)
        
        
        #Set Padding Width for Columns of Frame
        gridpadding = 20
        
        
        #Make Unit of Analysis Label & Dropdown
        lbl_units = tk.Label(frame_layer, text='Unidade de Análise', font=('Arial',24))
        lbl_units.grid(column=0, row=0, ipadx=gridpadding)
        
        self.uoa.longname_modes = {
        "Bairros":1,
        "Áreas Protegidas":2,
        "Zonas de Planejamento":3
        }
        self.uoa.longname_modes_inverted = dict(map(reversed, self.uoa.longname_modes.items()))
        
        self.uoa.setting_name = tk.StringVar()
        self.uoa.setting_name.set(self.uoa.longname_modes_inverted[self.uoa.setting_index.get()])
        unitoptionlist = tk.OptionMenu(frame_layer, self.uoa.setting_name,
                           *list(self.uoa.longname_modes.keys()),
                           command=lambda _: self.replace_map_image())
        unitoptionlist.grid(column=0, row=1, ipadx=gridpadding)
        
        
        #Make UOA Fill Label (Dropdown Added During Map Window Creation)
        lbl_layers = tk.Label(frame_layer, text='Cor da zona', font=('Arial',24))
        lbl_layers.grid(column=1, row=0, ipadx=gridpadding)

            
        #Make Map Images Label & Dropdown
        lbl_layers = tk.Label(frame_layer, text='Imagem do Mapa', font=('Arial',24))
        lbl_layers.grid(column=2, row=0, ipadx=gridpadding)
        
        self.map_image.longname_modes = {
        "Nenhum":0,
        "Mapa Base":1
        }
        
        self.map_image.setting_name = tk.StringVar()
        self.map_image.setting_name.set(list(self.map_image.longname_modes.keys())
                                         [self.map_image.setting_index.get()])
        
        mapoptionlist = tk.OptionMenu(frame_layer, self.map_image.setting_name, 
                          *list(self.map_image.longname_modes.keys()), 
                          command=lambda _: self.replace_map_image())
        mapoptionlist.grid(column=2, row=1, ipadx=gridpadding)
        
        
        #Make Overlays Label & Dropdown
        lbl_layers = tk.Label(frame_layer, text='Overlays', font=('Arial',24))
        lbl_layers.grid(column=3, row=0, ipadx=gridpadding) 
        
        self.overlay.longname_modes = {
        "Nenhum":0,
        "Perda de Manguezais":1,
        "Saúde dos Manguezais": 2,
        }
        
        self.overlay.setting_name = tk.StringVar()
        self.overlay.setting_name.set(list(self.overlay.longname_modes.keys())
                                      [self.overlay.setting_index.get()])
        overlayoptionlist = tk.OptionMenu(frame_layer, self.overlay.setting_name, 
                          *list(self.overlay.longname_modes.keys()), 
                          command=lambda _: self.replace_map_image())
        overlayoptionlist.grid(column=3, row=1, ipadx=gridpadding)
        
        
        #Make Zoom Label, Entry, and Button
        zoomlabel = tk.Label(frame_layer, text='Zoom', font=('Arial',24))
        zoomlabel.grid(column=4, row=0, ipadx=gridpadding)
        self.zoomslider = tk.Scale(frame_layer, 
                                   from_=50, to=500, 
                                   orient='horizontal',
                                   tickinterval = 0,
                                   )
        self.zoomslider.set(100)
        self.zoomslider.bind("<ButtonRelease-1>",  lambda e: self.zoomer(factor=self.zoomslider.get()))
        self.zoomslider.grid(column=4, row=1, ipadx=gridpadding)


        return frame_layer
    
    
    def make_fill_list (self, root, shp):    
        """CREATE UOA FILL COLOR TOGGLE
    
        Args:
            root: tk frame for the dropdown to to be situated in.
               
        Returns:
            zoneoptionlist: the dropdown list
        """
        
        #Identify fields, longnames, and categories to be added to the dropdown
        shortfieldlist = [[]]
        longfieldlist = [[]]
        categorylist = []
        for field in shp.fields:
            fieldname = field[0]
            testfield = fieldnamelookup(fieldname)
            if testfield.fieldname != []:
                shortfieldlist.append(testfield.fieldname)
                longfieldlist.append(testfield.longname)
                categorylist.append(testfield.category)
            
            
        #Create a index:field dictionary and a index:longname dictionary (and inverses)
        self.uoa.color_field_modes = dict(list(enumerate(shortfieldlist)))
        self.uoa.color_field_modes[0] = 'Nenhum'
        self.uoa.color_field_modes_inverted = dict(map(reversed, self.uoa.color_field_modes.items()))
        
        self.uoa.color_longname_modes = dict(list(enumerate(longfieldlist)))
        self.uoa.color_longname_modes[0] = 'Nenhum'
        self.uoa.color_longname_modes_inverted = dict(map(reversed, self.uoa.color_longname_modes.items()))


        #Create dictionary for field:category
        uniquecategories = list(set(categorylist))
        uniquecategories.sort()
        self.catdict=dict()
        for entry in uniquecategories:
            self.catdict[entry] = []
        
        for field in shp.fields:
            fieldname = field[0]
            selectedfield = fieldnamelookup(fieldname)
            if selectedfield.fieldname != []:
                self.catdict[selectedfield.category].append(selectedfield.longname)
                
        
        #Create UOA Color Fill Dropdown
        self.uoa.color_setting_name = tk.StringVar()
        self.uoa.color_setting_name.set(self.uoa.color_longname_modes
                                        [self.uoa.color_field_modes_inverted
                                         [self.uoa.color_default
                                          [self.uoa.setting_index.get()]]])
        
        uoa_color_optionlist = tk.Menubutton(root, textvariable=self.uoa.color_setting_name, 
                                       indicatoron=False)
        
        topMenu = tk.Menu(uoa_color_optionlist, tearoff=False)
        uoa_color_optionlist.configure(menu=topMenu)

        for key in sorted(self.catdict.keys()):
            menu = tk.Menu(topMenu)
            topMenu.add_cascade(label=key, menu=menu)
            for value in self.catdict[key]:
                menu.add_radiobutton(label=value, variable = self.uoa.color_setting_name, 
                                     value=value,
                                     command=lambda: self.replace_map_image() )
        
        uoa_color_optionlist.grid(column=1, row=1)
    
        #Return dropdown for future reference
        return uoa_color_optionlist    
    
    
    def make_map_window(self, root):
        """CREATE MAP WINDOW
            https://stackoverflow.com/questions/36328547/changing-the-shape-of-tkinter-widgets
            http://effbot.org/tkinterbook/place.htm
            https://github.com/afourmy/pyGISS
    
        Args:
            root: tk window or frame for the buttons to to be situated in.
               
        Returns:
            frame_map: frame that houses the map
            label_date: label indicated date of the display
            label_real: label indicated reality or simulated of the display
            mapimg: Map canvas
        """
        
        
        #Make Frame
        frame_map = tk.Frame(root)
        frame_map.grid(column=0, row=1)\
            
        
        #Select specific UOA shapefile
        shps = [self.uoa.shps[self.uoa.setting_index.get()]]
        
        
        #Make Color Fill Dropdown Menu
        self.uoa_color_optionlist =  self.make_fill_list(self.frame_buttons, shps[0])
        
        
        #Select map image and UOA color fill
        background_image = self.map_image.filepaths[self.map_image.setting_index.get()]
        color_range =  self.uoa.color_field_modes[self.uoa.color_longname_modes_inverted
                                                  [self.uoa.color_setting_name.get()]]
        color_title = self.uoa.color_setting_name.get()
        
        
        #Create Map and bind commands to it
        MAP = MapWindow.Map(frame_map,shps,
                               background_image = background_image, 
                               color_range= [color_range],
                               color_title=color_title)
        MAP.bind("<Button-1>", self.print_coords)
        MAP.bind("<Double-Button-1>", lambda e: self.uoa_type(self.clickname))

        
        #Date and Data Labels in top right corner
        label_date = tk.Label(frame_map, text='Setembro 2018', font=('Arial', 24), fg='red' )
        label_date.place(relx=1, x=-2, y=2, anchor='ne')
        label_real = tk.Label(frame_map, text='Dados Reais', font=('Arial', 24), fg='red' )
        label_real.place(relx=1, x=-2, y=35, anchor='ne')
        
        
        return frame_map, label_date, label_real, MAP


    def make_info_display(self, root):
        """CREATE INFORMATION DISPLAY
    
        Args:
            root: tk window or frame for the buttons to to be situated in.
               
        Returns:
            frame_info: frame housing the information display
            list_info: listbox of "at-large" information
            list_zone: listbox of zone-specific information
        """
        
        
        #Make Frame
        frame_info = tk.Frame(root)
        frame_info.grid(column=1, row=1)
        
        
        #Make At-Large Information Header
        lbl_info = tk.Label(frame_info, text='Exibição de Dados', font=('Arial',24))
        lbl_info.grid(column=0, row=0)
        
        
        #### REPLACE WITH ACTUAL CALCULATIONS ####
        mangrove_extent = 208080
        mangrove_growth = 2200 
        mangrove_loss = 7270
        mangrove_net = mangrove_growth - mangrove_loss
        mangrove_atrisk = 8560
        
        
        #Make At-Large Information Display
        list_info = tk.Listbox(frame_info, width=50)
        list_info.insert(1, 'Extensão dos Manguezais: ' + str(mangrove_extent) +' ha')
        list_info.insert(2, 'Área de Crescimento Recente: ' + str(mangrove_growth) + ' ha') 
        list_info.insert(3, 'Área de Perda Recente: ' + str(mangrove_loss) + ' ha') 
        list_info.insert(4, 'Área de Manguezais em Risco: ' + str(mangrove_atrisk) +' ha') 
        list_info.insert(5, 'Mudança nos Manguezais: ' + str(mangrove_net) +' ha') 
        list_info.grid(column=0, row=1) 
        
        
        #Make Label and Tabs for the UOA Info Box
        lbl_zone = tk.Label(frame_info, text='Informações da Unidade', font=('Arial',24))
        lbl_zone.grid(column=0, row=2)
        list_tabparent = tk.ttk.Notebook(frame_info)
        list_tabparent.grid(column=0, row=3)
        list_uoa_boxes = self.make_uoa_info_display(frame_info, list_tabparent)
        
        
        return frame_info, list_info, list_uoa_boxes, list_tabparent


    def make_uoa_info_display (self, frame_info, list_tabparent):
        """CREATE UOA TEXTUAL DATA DISPLAY TABS
    
        Args:
            frame_info: tk frame for the display box tabs to to be situated in.
            list_tabparent: the tk Notebook that the tabs reside in
               
        Returns:
            list_zone_boxes: collection of display box tabs
        """
        
        
        #Create a display box tab for each category
        list_uoa_boxes = dict()
        for key in sorted(self.catdict.keys()):
            shortkey = key[0:3]
            list_uoa_boxes[key] = tk.Listbox(list_tabparent, width=50)
            list_uoa_boxes[key].insert(1, '')
            list_uoa_boxes[key].bind("<Double-Button-1>", lambda e: self.uoa_type(self.clickname))
            list_tabparent.add(list_uoa_boxes[key], text = shortkey)
        
        
        #Add in the mandatory tabs that might not be added automatically
        mandatorytabs = ['Geografia', 'ID', 'Diversos']
        for entry in mandatorytabs:
            if list_uoa_boxes.get(entry, 'False') == 'False':
                list_uoa_boxes[entry] = tk.Listbox(list_tabparent, width=50)
                list_uoa_boxes[entry].insert(1, '')
                list_uoa_boxes[entry].bind("<Double-Button-1>", lambda e: self.uoa_type(self.clickname))
                list_tabparent.add(list_uoa_boxes[entry], text = entry[0:5])
            
            
        #Return the display boxes for future reference
        return list_uoa_boxes
    
    def make_control(self, root):
        """CREATE CONTROL BUTTONS
    
        Args:
            root: tk window or frame for the buttons to to be situated in.
               
        Returns:
            frame_control: frame housing the control buttons
            btn_calculate: the button that initializes calculations
            btn_future: the button that switches display to the future
        """
        
        #Make Frame
        frame_control = tk.Frame(root)
        frame_control.grid(column=0, row=2)
        
        
        #Make Control Buttons
        zoomdefault = tk.Button(frame_control, text='Restaurar Zoom',
                                command=lambda: self.replace_map_image(restore_zoom_default=1)
                                )
        zoomdefault.grid(column=0, row=0)
        btn_zones = tk.Button(frame_control, text="Restaurar Original", 
                              command= self.restore_defaults)
        btn_zones.grid(column=1, row=0)
        btn_calculate = tk.Button(frame_control, text="Calcular", 
                                  command=lambda: self.calculations(root))
        btn_calculate.grid(column=2, row=0)
        btn_future = tk.Button(frame_control, text="Mostrar Futuro Simulado", 
                               command= lambda: self.show_future())
        btn_future.grid(column=3, row=0)
        
        
        return frame_control, btn_calculate, btn_future
    
    
    
# =============================================================================
#     Define Map Button Commands
# =============================================================================
    
    def replace_map_image(self, **kwargs):
        """UPDATE MAP TO CURRENT SETTINGS
    
        Args:
            N/A
            [Note, this function depends primarily on the current values for 
            mapsetting, zone_color_metricsetting, and mangrovesetting]
               
        Returns:
            N/A
        """
        
        
        #Check if the UOA has changed
        flag1 = 0
        if self.uoa.longname_modes[self.uoa.setting_name.get()] != self.uoa.setting_index.get():
            self.uoa.setting_index.set(self.uoa.longname_modes[self.uoa.setting_name.get()])
            flag1 = 1 #set to indicate that the UOA Color Fill Dropdown needs to be updated
                                                
           
        #Pull shapefiles and mapname based on settings
        uoa_name = [self.uoa.shps[self.uoa.setting_index.get()]]

        
       #Replace UOA Color Fill Option List If Needed
        if flag1 == 1:
            self.uoa_color_optionlist.destroy()
            self.uoa_color_optionlist = self.make_fill_list(self.frame_buttons, uoa_name[0])
            for key in self.list_uoa_boxes.keys():
                self.list_uoa_boxes[key].destroy()
            self.list_uoa_boxes = self.make_uoa_info_display(self.frame_info, self.list_tabparent)
            
            
        #Update Map Image and Overlay Settings
        self.map_image.setting_index.set(self.map_image.longname_modes[self.map_image.setting_name.get()])
        self.overlay.setting_index.set(self.overlay.longname_modes[self.overlay.setting_name.get()])
        self.overlay.color_setting_index.set(self.overlay.color_default[self.overlay.setting_index.get()])

        
        #Pull settings into more usable formats
        uoa_color = self.uoa.color_field_modes[self.uoa.color_longname_modes_inverted[self.uoa.color_setting_name.get()]]
        uoa_color_title = self.uoa.color_setting_name.get()
        overlay_name = self.overlay.shps[self.overlay.setting_index.get()]
        overlay_color = (self.overlay.color_metrics[self.overlay.setting_index.get()]
                         [self.overlay.color_setting_index.get()])
        overlay_color_title = (self.overlay.color_titles[self.overlay.setting_index.get()]
                               [self.overlay.color_setting_index.get()])
        map_image_name = self.map_image.filepaths[self.map_image.setting_index.get()]
        
        if 'restore_zoom_default' in kwargs:
            restore_zoom_default_flag = kwargs.pop('restore_zoom_default')
        else:
            restore_zoom_default_flag = 0
            
        if restore_zoom_default_flag == 1:
             offset_and_ratio = [self.MAP.default_offset[0], self.MAP.default_offset[1], self.MAP.default_ratio]
        else:
             offset_and_ratio = [self.MAP.offset[0], self.MAP.offset[1], self.MAP.ratio]

        
        #Delete exisiting map
        slaveitems = self.frame_map.slaves()
        for item in slaveitems:
            item.destroy()    
        griditems = self.frame_map.grid_slaves()
        for item in griditems:
            item.destroy()
            
            
        #Generate New Map (Minus mangroves)
        if self.map_image.setting_index.get() == 0:
            if self.uoa.color_longname_modes_inverted[self.uoa.color_setting_name.get()] == 0:
                self.MAP = MapWindow.Map(self.frame_map,uoa_name,
                                         offset_and_ratio=offset_and_ratio)
            else:
                self.MAP = MapWindow.Map(self.frame_map,uoa_name, 
                                            color_range=[uoa_color],
                                            color_title=uoa_color_title,
                                            offset_and_ratio=offset_and_ratio)
        else:
            if self.uoa.color_longname_modes_inverted[self.uoa.color_setting_name.get()] == 0:
                self.MAP = MapWindow.Map(self.frame_map,uoa_name, 
                                            background_image=map_image_name,
                                            offset_and_ratio=offset_and_ratio)
            else:
                self.MAP = MapWindow.Map(self.frame_map,uoa_name, 
                                            background_image=map_image_name, 
                                            color_range=[uoa_color],
                                            color_title=uoa_color_title,
                                            offset_and_ratio=offset_and_ratio)
                
                
        #Bind commands to the map
        self.MAP.bind("<Button-1>", self.print_coords)       
        self.MAP.bind("<Double-Button-1>", lambda e: self.uoa_type(self.clickname))
        
        
        #Add Mangrove Layer (if appropriate)
        if self.overlay.setting_index.get() != 0:
            self.MAP.addshapes(overlay_name, outline='black', 
                                  color_range=overlay_color,
                                  color_title=overlay_color_title)


        #Restore labels to top of stack
        self.label_date.lift()
        self.label_real.lift()
        
        
    def zoomer(self, **kwargs):
        """ZOOMS THE MAP IN THE AND OUT
    
        Args:
            N/A
            [Note, this function depends primarily on the current values for 
            clickevent and the kwarg "factor" which controls how much to zoom in or our]
               
        Returns:
            N/A
        """
        
        #Check if a clickevent exisits. If not, generates an error window for user
        if self.clickevent == []:
            zoom_error_window = tk.Toplevel(self)
            zoom_error_window.title('Zoom Error')
            zoom_error_window.geometry("+650+100")
            lbl_text = tk.Label(zoom_error_window, 
                                text='Clique na localização do mapa antes de pressionar o botão de zoom', 
                                font=('Arial',16))
            lbl_text.grid(column=1, row=0)
            
            
            #Reset Zoom Slider to 100
            self.zoomslider.set(100)
            
            
        else:
            event = self.clickevent
            
            
            #Pull and format the factor appropriately
            if 'factor' in kwargs:
                factor = kwargs.pop('factor')
                factor = int(factor)
                factor = factor/100
            else:
                factor = 1.3
                
            
            #Develop Transformation
            if factor > 0:
                event.x, event.y = self.MAP.canvasx(event.x), self.MAP.canvasy(event.y)
                self.MAP.scale('all', event.x, event.y, factor, factor)
                self.MAP.configure(scrollregion=self.MAP.bbox('all'))
                self.MAP.ratio *= float(factor)
                self.MAP.offset = (
                    self.MAP.offset[0]*factor + event.x*(1 - factor),
                    self.MAP.offset[1]*factor + event.y*(1 - factor)
                    )
                
                
                #Select Appropriate Settings                
                uoa_name = [self.uoa.shps[self.uoa.setting_index.get()]]
                map_image_name = self.map_image.filepaths[self.map_image.setting_index.get()]
                uoa_color = self.uoa.color_field_modes[self.uoa.color_longname_modes_inverted[self.uoa.color_setting_name.get()]]
                uoa_color_title = self.uoa.color_setting_name.get()
                overlay_name = self.overlay.shps[self.overlay.setting_index.get()]
                overlay_color = (self.overlay.color_metrics[self.overlay.setting_index.get()]
                                 [self.overlay.color_setting_index.get()])
                overlay_color_title = (self.overlay.color_titles[self.overlay.setting_index.get()]
                                       [self.overlay.color_setting_index.get()])
                  
                
                #Redraw map at appropriate zoom and focus
                if map_image_name != []:
                    self.MAP.draw_background(map_image_name)
                self.MAP.draw_map(uoa_name, color_range=[uoa_color])
                     
                
                #Redraw overlays at appropriate zoom and focus
                if self.overlay.setting_index.get() != 0:
                    self.MAP.addshapes(overlay_name, outline='black', 
                                          color_range=overlay_color,
                                          color_title=overlay_color_title)
                    
                
                #Replace Map Marker
                self.map_marker(self.MAP, event.x, event.y)
                
                
                #Reset Zoom Slider to 100
                self.zoomslider.set(100)
                
        
# =============================================================================
#   Define Map Canvas Controls  
# =============================================================================
    def print_coords(self, event):
        """IDENTIFY LOCATION OF CLICK AND UNDERTAKE APPROPRIATE FUNCTIONS
    
        Args:
            event: a click event on the map canvas
            
        Returns:
            N/A
        """
        
        
        #Identify canvas and geographic coordinates
        event.x, event.y = self.MAP.canvasx(event.x), self.MAP.canvasy(event.y)
        geox, geoy = self.MAP.to_geographical_coordinates(event.x, event.y)
        print(geox, geoy)
        
       
        #Put Visual Marker on Map at Location of Click
        self.map_marker(self.MAP, event.x, event.y)
        
    
        #Select Appropriate Zone and Calculate Required Information
        name = []
        self.ID = []
        self.Action = []
        for shaperec in self.uoa.shps[self.uoa.setting_index.get()].iterShapeRecords():
            boundary = shaperec.shape # get a boundary polygon
            if shapely.geometry.Point((geox, geoy)).within(shapely.geometry.shape(boundary)): # make a point and see if it's in the polygon

                for field in self.uoa.shps[self.uoa.setting_index.get()].fields:
                    fieldoutput = fieldnamelookup(field[0])
                    if fieldoutput.fieldname !=[]:
                        if fieldoutput.type == 'ID':
                            self.ID = fieldoutput
                        elif fieldoutput.type == 'Action':
                            self.Action = fieldoutput
                    
                if self.ID != []:
                
                    #Pull data from shapefile
                    name = str(shaperec.record[self.ID.fieldname])
                    print("The point is in", name)
                    
                    #Calculate area of zone
                    geom = shapely.geometry.polygon.Polygon(boundary.points)
                    geom_area = shapely.ops.transform(
                            partial(
                                pyproj.transform,
                                pyproj.Proj(init='EPSG:4326'),
                                pyproj.Proj(init='epsg:3857')),
                                shapely.geometry.shape(geom))
                    area = geom_area.area
                    
                    #Calculate area of mangrove loss in zone
                    area_of_loss = 0;
                    for shaperec2 in self.overlay.shps[1].iterShapeRecords():
                        m_boundary = shaperec2.shape # get a boundary polygon
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
             
                    for entry in self.list_uoa_boxes.keys():
                        self.list_uoa_boxes[entry].delete(0, tk.END)

                    for field in self.uoa.shps[self.uoa.setting_index.get()].fields:
                        fieldoutput = fieldnamelookup(field[0])
                        if fieldoutput.fieldname !=[]:
                            if fieldoutput.type == 'Other':
                                self.list_uoa_boxes[fieldoutput.category].insert(tk.END,
                                                      fieldoutput.longname + ': ' + str(shaperec.record[fieldoutput.fieldname]))

                    
                    self.list_uoa_boxes['Geografia'].insert(tk.END, 'Área de Bairro (km^2): ' + str(round(area/(1000*1000))))
                    self.list_uoa_boxes['Geografia'].insert(tk.END, 'Perda de Manguezais (m^2): ' + str(round(area_of_loss)))
                    
                    self.list_uoa_boxes['ID'].insert(0, self.ID.longname +': ' + name)
                    if self.Action != []:
                        self.list_uoa_boxes[self.Action.category].insert(tk.END, self.Action.longname + 
                                                                         ': ' + str(shaperec.record[self.Action.fieldname]))
                        self.list_uoa_boxes[self.Action.category].itemconfig(tk.END, {'bg':'yellow'})

                    #Add Selection Functionality to Zone Information Display
                    self.clickname = name
                else:
                    self.clickname = []
                
            self.clickevent = event
        
    def map_marker(self, MAP, coordx, coordy):
        #Put Visual Marker on Map at Location of Click
        markerwidth = 5
        markercoords = [(coordx-markerwidth, coordy-markerwidth),
                        (coordx+markerwidth, coordy-markerwidth),
                        (coordx+markerwidth, coordy+markerwidth),
                        (coordx-markerwidth, coordy+markerwidth)
                        ]
        MAP.delete( 'marker')
        MAP.create_polygon(markercoords,
                                fill='orange',
                                outline='black',
                                tags=('marker')
                                )


        
# =============================================================================
#   Define Data Display Functions  
# =============================================================================
              
    def uoa_type(self,name):
        """CREATE WINDOW WITH ZONE TYPE OPTIONS
    
        Args:
            name: Name of zone to be changed
               
        Returns:
            N/A
        """
        
        #Create Window
        if name != [] and self.Action !=[]:
            #Creat window and label
            uoa_window = tk.Toplevel(self)
            windowtext = 'Definir ' + self.Action.longname + ' de ' + self.uoa.longname_modes_inverted[self.uoa.setting_index.get()] 
            uoa_window.title(windowtext)
            uoa_window.geometry("+1200+750")
            lbl_text = tk.Label(uoa_window, text=windowtext,font=('Arial',24))
            lbl_text.grid(column=1, row=0)
            
            
            #Generate Dropdown
            uoa_type_optionvar = tk.StringVar()
            uoa_type_optionvar.set(self.Action.choices[0])
            uoa_type_optionlist = tk.OptionMenu(uoa_window, uoa_type_optionvar,
                                           *self.Action.choices,
                                            command=lambda _: self.change_uoa_type(name, uoa_type_optionvar.get(), uoa_window))
            uoa_type_optionlist.grid(column=0, row=1)
            
             
    def change_uoa_type(self,name,newtype, parent):
        """CHANGE UOA TYPE ON SHAPEFILE AND UPDATE DISPLAY
    
        Args:
            name: name of the zone to be changed
            newtype: type to change the zonetype to
            parent: window generated by uoa_type
               
        Returns:
            N/A
        """
        
        #Save Changed Zone Type(s) to a temporary file
        r1 = self.uoa.shps[self.uoa.setting_index.get()]
        w1 = shapefile.Writer("./temp.shp")
        
        
        # Copy over the existing fields to temporary file
        fields = r1.fields
        for fieldname in fields:
            if type(fieldname) == "tuple":
                continue
            else:
                args = fieldname
                w1.field(*args) 
                
                
        # Copy over exisiting records and geometries, editing the one specific record and field
        for shaperec in r1.iterShapeRecords():
            testname = shaperec.record[self.ID.fieldname]
            if name == testname:
                shaperec.record[self.Action.fieldname] = newtype 
            w1.record(*shaperec.record)
            w1.shape(shaperec.shape)
            
            
        # Close and save the altered shapefile
        w1.close()
        
        
        #Copy the temporary file back over the original shapefile
        ShapefileFormatter.ShapeFileCopier('./temp', self.uoa.filepaths[self.uoa.setting_index.get()])
        
        
        #Reload all of the edited shapefile
        self.uoa.shps[self.uoa.setting_index.get()] = shapefile.Reader(self.uoa.filepaths[self.uoa.setting_index.get()])


        #Delete the temporary file
        if os.path.exists("./temp.dbf"):
            os.remove("./temp.dbf")
        else:
            print("temp.dbf does not exist")
        if os.path.exists("./temp.shp"):
            os.remove("./temp.shp")
        else:
            print("temp.shp does not exist")
        if os.path.exists("./temp.shx"):
            os.remove("./temp.shx")
        else:
            print("temp.shx does not exist")
                
            
        #Update UOA Information Display       
        self.list_uoa_boxes[self.Action.category].delete(0, tk.END)
        self.list_uoa_boxes[self.Action.category].insert(tk.END, self.Action.longname + ': ' + str(newtype))
        self.list_uoa_boxes[self.Action.category].itemconfig(tk.END, {'bg':'yellow'})

        
        #Update the Map
        self.replace_map_image()

        
        #Close Window
        parent.destroy()
        


# =============================================================================
#   Define Control Panel Button Commands  
# =============================================================================
       
    def restore_defaults(self):
        """RESTORES DEFAULT ZONE TYPES
    
        Args:
            N/A
            [Note: The default filepath is specified as self.defaultzonefilepath]
               
        Returns:
            N/A
            
        """
       
        #Copy default zone shapefile over the currently used shapefile
        for (filepath, original) in zip(self.uoa.filepaths, self.uoa.original_filepaths):
            if (filepath != []) and (original != []):
                ShapefileFormatter.ShapeFileCopier(original, filepath)
        
        #Reload all of the zoneshapefiles
        self.uoa.shps = []
        for shpname in self.uoa.filepaths:
            if shpname == []:
                self.uoa.shps.append([])
            else:
                self.uoa.shps.append(shapefile.Reader(shpname))
        
        self.replace_map_image()
         
    def change_tense_labels(self, newtense):
        """CHANGE TENSE ON MAP LABELS
    
        Args:
            newtense: The sense to be chaanged to (0 = present, 1 = future)
               
        Returns:
            N/A
        """
        
        self.tense = newtense
        
        if self.tense == 0:
            self.label_date.config(text='Setembro 2018')
            self.label_real.config(text='Dados Reais')            
        else:
            self.label_date.config(text='Setembro 2028')
            self.label_real.config(text='SIMULAÇÃO [NÃO É ATUAL]')
            
    def calculations(self, root):
        """CALCULATE FUTURE BASED ON USER INPUTS
        [CURRENTLY INCOMPLETE]
    
        Args:
            N/A
               
        Returns:
            N/A
            
        """
        self.overlay.shps_present = self.overlay.shps
        self.overlay.shps_future = []
        self.overlay.shps_future.append(self.overlay.shps[0])
        self.overlay.shps_future.append(self.overlay.shps[1])

        self.uoa.shps_present = self.uoa.shps
        self.uoa.shps_future = self.uoa.shps
        
        self.mangrovehealth_future = FutureCalculations.mangrovehealthchange(self, self.zones.shps[1], self.overlays.shps[2])
        self.overlay.shps_future.append(self.mangrovehealth_future)
        
        self.show_future()

        
    
    def show_future(self):
        """DISPLAY CALCULATED VALUES FOR THE FUTURE
    
        Args:
            N/A
               
        Returns:
            N/A
            
        """
        if self.tense == 0:
            try: 
                self.overlay.shps_future
            except AttributeError:
                x = (self.winfo_screenwidth() // 2) 
                y = (self.winfo_screenheight() // 2)
                futureerrorwindow = tk.Toplevel(self)
                futureerrorwindow.title('Futuro Error')
                futureerrorwindow.geometry("+%d+%d" % (x, y))
                lbl_text = tk.Label(futureerrorwindow, 
                                    text='Execute os cálculos antes de mostrar o futuro', 
                                    font=('Arial',16))
                lbl_text.grid(column=1, row=0)
            else:
                self.btn_future.config(text='Mostrar Presente')
                self.overlay.shps = self.overlay.shps_future
                self.uoa.shps = self.uoa.shps_future
                self.replace_map_image()
                self.change_tense_labels(1)
            
               



        else:
            self.btn_future.config(text='Mostrar Futuro Simulado')
            
            self.overlay.shps = self.overlay.shps_present
            self.uoa.shps = self.uoa.shps_present
            self.replace_map_image()
            self.change_tense_labels(0)


            
        

# =============================================================================
#   Main Script
# =============================================================================
if str.__eq__(__name__, '__main__'):
       
    window = tk.Tk()
    window.title('EVDT Interactive Simulation')
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=20)
    EVDT_Model = EVDT(window)
    window.mainloop()



