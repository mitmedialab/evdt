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
import pyproj
import shapefile
from functools import partial
import shapely.ops
import shapely.geometry

import ShapefileFormatter
import MapWindow_v4 as MapWindow
import FutureCalculations_v1 as FutureCalculations
from MapType import *

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
        #ZONES
        zone_filepaths = [[], 
                          './FormatedShapefiles/Bairros/Bairros_Custom_restricted.shp',
                          './FormatedShapefiles/Protected Areas/Áreas_Protegidas_base.shp',
                          './FormatedShapefiles/Planning Zones/Zonas_base.shp']
                
        zone_color_metrics = [ [], 
                              [ [], 'POPDEN', 'EmpRate', 'AgriRate', 'Zone_TypeN'],
                              [ [] ],
                              [ [] ]
                              ]
        zonecolortitles = [ [], 
                           [ [], 'Densidade Populacional (pop/km^2)', 
                            'Taxa de Emprego (emp/pop)', 
                            'Taxa de Emprego Agrícola (agrí/emp)', 
                            'Estado de Conservação'],
                           [ []],
                           [ []]
                           ]
        defaultzonefilepath = ['./FormatedShapefiles/Bairros/Bairros_Custom_restricted_DEFAULT.shp',
                               
                               ]
        
        
        #MAP IMAGES
        mapfilepaths = [[], "./basemap.png", "./map.jpg", "./mangrove_health.png" ]
    
        #MANGROVES
        mangrovenames = [ [], './FormatedShapefiles/Mangroves/m_loss.shp', 
                         './FormatedShapefiles/Mangroves/m_health.shp',
                         ]
        mangrovecolors = [ [ [], 'mangrovelo'], [[], 'mangroveHe']]
        mangrovecolortitles =  [ [[], 'Perda de Manguezais'], [[], 'Saúde dos Manguezais'] ]
        
        #Create all setting variables and set to default
        
        self.zones = MapType(zone_filepaths, 
                     default = 1,
                     color_metrics = zone_color_metrics, 
                     color_default = [0, 1, 0, 0],
                     color_titles = zonecolortitles, 
                     original_filepaths = defaultzonefilepath, 
                     maptype='shp')
        
        self.zones.setting = tk.IntVar()
        self.zones.setting.set(self.zones.default)
        self.zones.color_setting = tk.IntVar()
        self.zones.color_setting.set(self.zones.color_default[self.zones.default])
        
        self.mapimgs = MapType(mapfilepaths, 
                       default = 1,
                       maptype='img')
        
        
        self.mapimgs.setting = tk.IntVar()
        self.mapimgs.setting.set(self.mapimgs.default)
        
        
        
        self.overlays = MapType(mangrovenames, 
              default = 0,
              color_metrics = mangrovecolors, 
              color_default = [0, 1, 1],
              color_titles = mangrovecolortitles, 
              maptype='shp')
        
        self.overlays.setting = tk.IntVar()
        self.overlays.setting.set(self.overlays.default)
        self.overlays.color_setting = tk.IntVar()
        self.overlays.color_setting.set(self.overlays.color_default[self.overlays.default])
        
        
        self.tense = 0

        #Create each component of UI
        self.clickname = []
        self.clickevent = []
        self.frame_map, self.label_date, self.label_real, self.mapimg = self.make_map_window(root)
        self.frame_buttons = self.make_layer_buttons(root)
        self.frame_info, self.list_info, self.list_zone = self.make_info_display(root)
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

        #Make Unit of Analysis Buttons
        lbl_units = tk.Label(frame_layer, text='Unidade de Análise', font=('Arial',24))
        lbl_units.grid(column=0, row=0)
        self.UnitModes = {
        "Nenhum": 0,
        "Bairros":1,
        "Unidades de Conservação":2,
        "Zonas de Planejamento":3
        }
        self.unitoptionvar = tk.StringVar()
        self.unitoptionvar.set(list(self.UnitModes.keys())[self.zones.setting.get()])
        unitoptionlist = tk.OptionMenu(frame_layer, self.unitoptionvar,
                           *list(self.UnitModes.keys()),
                           command=lambda _: self.replace_map_image())
        unitoptionlist.grid(column=0, row=1)
        
        
        #Make Zone Fill Buttons
        lbl_layers = tk.Label(frame_layer, text='Cor da zona', font=('Arial',24))
        lbl_layers.grid(column=1, row=0)
        self.ZoneModes = {
        "Nenhum":0,
        "Densidade Populacional":1,
        "Taxa de Emprego": 2,
        "Taxa de Emprego Agrícola": 3,
        "Estado de Conservação": 4
        }
        self.zoneoptionvar = tk.StringVar()
        self.zoneoptionvar.set(list(self.ZoneModes.keys())[self.zones.color_setting.get()])
        zoneoptionlist = tk.OptionMenu(frame_layer, self.zoneoptionvar, 
                          *list(self.ZoneModes.keys()), 
                          command=lambda _: self.replace_map_image())
        zoneoptionlist.grid(column=1, row=1)
            
        #Make Map Images Buttons
        lbl_layers = tk.Label(frame_layer, text='Imagem do Mapa', font=('Arial',24))
        lbl_layers.grid(column=2, row=0)
        self.MapModes = {
        "Nenhum":0,
        "Mapa Base":1
        }
        self.mapoptionvar = tk.StringVar()
        self.mapoptionvar.set(list(self.MapModes.keys())[self.mapimgs.setting.get()])
        
        mapoptionlist = tk.OptionMenu(frame_layer, self.mapoptionvar, 
                          *list(self.MapModes.keys()), 
                          command=lambda _: self.replace_map_image())
        mapoptionlist.grid(column=2, row=1)
        
        #Make Overlays Layer Buttons
        lbl_layers = tk.Label(frame_layer, text='Overlays', font=('Arial',24))
        lbl_layers.grid(column=3, row=0) 
        self.MangroveModes = {
        "Nenhum":0,
        "Perda de Manguezais":1,
        "Saúde dos Manguezais": 2,
        }
        self.mangroveoptionvar = tk.StringVar()
        self.mangroveoptionvar.set(list(self.MangroveModes.keys())[self.overlays.setting.get()])
        mangroveoptionlist = tk.OptionMenu(frame_layer, self.mangroveoptionvar, 
                          *list(self.MangroveModes.keys()), 
                          command=lambda _: self.replace_map_image())
        mangroveoptionlist.grid(column=3, row=1)
        
        #Make Zoom Entry and Button
        zoombutton = tk.Button(frame_layer, text='Zoom',
                               command=lambda: self.zoomer(factor=zoomentry.get()))
        zoombutton.grid(column=4, row=0)
        zoomentry = tk.Entry(frame_layer)
        zoomentry.grid(column=4, row=1)
        zoomlabel = tk.Label(frame_layer, 
                             text = '%',
                             font=('Arial',14))
        zoomlabel.grid(column=5, row=1)
                               
        
        return frame_layer
    

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
        frame_map.grid(column=0, row=1)
        
        #Make Map and Bindings
        shps = [self.zones.shps[self.zones.setting.get()]]
        background_image = self.mapimgs.filepaths[self.mapimgs.setting.get()]
        color_range = self.zones.color_metrics[self.zones.setting.get()][self.zones.color_setting.get()]
        color_title = self.zones.color_titles[self.zones.setting.get()][self.zones.color_setting.get()]
        mapimg = MapWindow.Map(frame_map,shps,
                               background_image = background_image, 
                               color_range= [color_range],
                               color_title=color_title)
        mapimg.bind("<Button-1>", self.print_coords)
        mapimg.bind("<Double-Button-1>", lambda e: self.zone_type(self.clickname))

        # mapimg.bind('<MouseWheel>', self.zoomer)
        # mapimg.bind('<Button-4>', lambda e: self.zoomer(e, 1.3))
        # mapimg.bind('<Button-5>', lambda e: self.zoomer(e, 0.7))
        
        #Date and Data Labels in top corner
        label_date = tk.Label(frame_map, text='Setembro 2018', font=('Arial', 24), fg='red' )
        label_date.place(relx=1, x=-2, y=2, anchor='ne')
        label_real = tk.Label(frame_map, text='Dados Reais', font=('Arial', 24), fg='red' )
        label_real.place(relx=1, x=-2, y=35, anchor='ne')
        
        return frame_map, label_date, label_real, mapimg


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
        
        #Generate Initial Zone Information Data Display
        lbl_zone = tk.Label(frame_info, text='Informações do Bairro', font=('Arial',24))
        lbl_zone.grid(column=0, row=2)
        list_zone = tk.Listbox(frame_info, width=50)
        list_zone.insert(1, '')
        list_zone.insert(2, '') 
        list_zone.grid(column=0, row=3) 
        list_zone.bind("<Double-Button-1>", lambda e: self.zone_type(self.clickname))

        
        return frame_info, list_info, list_zone

        
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
        btn_zones = tk.Button(frame_control, text="Restaurar Original", 
                              command= self.restore_defaults)
        btn_zones.grid(column=0, row=0)
        btn_calculate = tk.Button(frame_control, text="Calcular", 
                                  command=lambda: self.calculations(root))
        btn_calculate.grid(column=1, row=0)
        btn_future = tk.Button(frame_control, text="Mostrar Futuro Simulado", 
                               command= lambda: self.show_future())
        btn_future.grid(column=2, row=0)
        return frame_control, btn_calculate, btn_future
    
# =============================================================================
#     Define Map Layer Button Commands
# =============================================================================
    
    def replace_map_image(self):
        """UPDATE MAP TO CURRENT SETTINGS
    
        Args:
            N/A
            [Note, this function depends primarily on the current values for 
            mapsetting, zone_color_metricsetting, and mangrovesetting]
               
        Returns:
            N/A
        """
        
        if self.UnitModes[self.unitoptionvar.get()] != self.zones.setting.get():
            self.zones.color_setting.set(self.zones.color_default[self.UnitModes[self.unitoptionvar.get()]])
            self.zones.setting.set(self.UnitModes[self.unitoptionvar.get()])

            
            #REPLACE THE ZONE COLOR FILL OPTION LIST!
            
        else:
            self.zones.color_setting.set(self.ZoneModes[self.zoneoptionvar.get()])
            
            
        self.mapimgs.setting.set(self.MapModes[self.mapoptionvar.get()])
        self.overlays.setting.set(self.MangroveModes[self.mangroveoptionvar.get()])
        self.overlays.color_setting.set(self.overlays.color_default[self.overlays.setting.get()])

        #Pull all inputs based on settings
        # shapename = [self.shapefilepaths[self.shapesetting.get()]]
        shapename = [self.zones.shps[self.zones.setting.get()]]
        mapname = self.mapimgs.filepaths[self.mapimgs.setting.get()]
        zonecolor = self.zones.color_metrics[self.zones.setting.get()][self.zones.color_setting.get()]
        zonecolortitle = self.zones.color_titles[self.zones.setting.get()][self.zones.color_setting.get()]
        mangrovename = self.overlays.shps[self.overlays.setting.get()]
        mangrovecolor = self.overlays.color_metrics[self.overlays.setting.get()][self.overlays.color_setting.get()]
        mangrovecolortitle = self.overlays.color_titles[self.overlays.setting.get()][self.overlays.color_setting.get()]
        

        #Delete exisiting map
        slaveitems = self.frame_map.slaves()
        for item in slaveitems:
            item.destroy()    
        griditems = self.frame_map.grid_slaves()
        for item in griditems:
            item.destroy()
            
        #Generate New Map (Minus mangroves)
        if self.mapimgs.setting.get() == 0:
            if self.zones.color_setting.get() == 0:
                self.mapimg = MapWindow.Map(self.frame_map,shapename)
            else:
                self.mapimg = MapWindow.Map(self.frame_map,shapename, 
                                            color_range=[zonecolor],
                                            color_title=zonecolortitle)
        else:
            if self.zones.color_setting.get() == 0:
                self.mapimg = MapWindow.Map(self.frame_map,shapename, 
                                            background_image=mapname)
            else:
                self.mapimg = MapWindow.Map(self.frame_map,shapename, 
                                            background_image=mapname, 
                                            color_range=[zonecolor],
                                            color_title=zonecolortitle)
                
        self.mapimg.bind("<Button-1>", self.print_coords)       
        self.mapimg.bind("<Double-Button-1>", lambda e: self.zone_type(self.clickname))
        
        # self.mapimg.bind('<MouseWheel>', self.zoomer)
        # self.mapimg.bind('<Button-4>', lambda e: self.zoomer(e, 1.3))
        # self.mapimg.bind('<Button-5>', lambda e: self.zoomer(e, 0.7))
        

        #Add Mangrove Layer (if appropriate)
        if self.overlays.setting.get() != 0:
            self.mapimg.addshapes(mangrovename, outline='black', 
                                  color_range=mangrovecolor,
                                  color_title=mangrovecolortitle)

        #Restore labels to top of stack
        self.label_date.lift()
        self.label_real.lift()
        
    def zoomer(self, **kwargs):
        if self.clickevent == []:
            zoomerrorwindow = tk.Toplevel(self)
            zoomerrorwindow.title('Zoom Error')
            zoomerrorwindow.geometry("+650+100")
            lbl_text = tk.Label(zoomerrorwindow, 
                                text='Clique na localização do mapa antes de pressionar o botão de zoom', 
                                font=('Arial',16))
            lbl_text.grid(column=1, row=0)
        else:
            event = self.clickevent
            
            if 'factor' in kwargs:
                factor = kwargs.pop('factor')
                factor = int(factor)
                factor = factor/100
            else:
                factor = 1.3 #if event.delta > 0 else 0.7
            if factor > 0:
                event.x, event.y = self.mapimg.canvasx(event.x), self.mapimg.canvasy(event.y)
                self.mapimg.scale('all', event.x, event.y, factor, factor)
                self.mapimg.configure(scrollregion=self.mapimg.bbox('all'))
                self.mapimg.ratio *= float(factor)
                self.mapimg.offset = (
                    self.mapimg.offset[0]*factor + event.x*(1 - factor),
                    self.mapimg.offset[1]*factor + event.y*(1 - factor)
                    )
                
                
                shapename = [self.zones.shps[self.zones.setting.get()]]
                mapname = self.mapimgs.filepaths[self.mapimgs.setting.get()]
                zonecolor = self.zones.color_metrics[self.zones.setting.get()][self.zones.color_setting.get()]
                # zonecolortitle = self.zones.color_titles[self.zones.setting.get()][self.zones.color_setting.get()]
                mangrovename = self.overlays.shps[self.overlays.setting.get()]
                mangrovecolor = self.overlays.color_metrics[self.overlays.setting.get()][self.overlays.color_setting.get()]
                mangrovecolortitle = self.overlays.color_titles[self.overlays.setting.get()][self.overlays.color_setting.get()]
                  
            
                if mapname != []:
                    self.mapimg.draw_background(mapname)
                    
                self.mapimg.draw_map(shapename, color_range=[zonecolor])
                     
                if self.overlays.setting.get() != 0:
                    self.mapimg.addshapes(mangrovename, outline='black', 
                                          color_range=mangrovecolor,
                                          color_title=mangrovecolortitle)
        
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
        event.x, event.y = self.mapimg.canvasx(event.x), self.mapimg.canvasy(event.y)
        geox, geoy = self.mapimg.to_geographical_coordinates(event.x, event.y)
        print(geox, geoy)
        
        name = []
        #Select Appropriate Zone and Calculate Required Information
        for shaperec in self.zones.shps[1].iterShapeRecords():
            boundary = shaperec.shape # get a boundary polygon
            if shapely.geometry.Point((geox, geoy)).within(shapely.geometry.shape(boundary)): # make a point and see if it's in the polygon
                #Pull data from shapefile
                name = shaperec.record[1] # get the second field of the corresponding record
                population = shaperec.record['POP']
                zonetype = shaperec.record['Zone_Type']
                emp = shaperec.record['Emp']
                agri= shaperec.record['Agri']
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
                for shaperec in self.overlays.shps[1].iterShapeRecords():
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
        if name != []:
            #Update Zone Information Display
            if str(zonetype) == 'Conservation':
                bg = 'green'
                zonetypep = 'Proteção Integral'
            elif str(zonetype) == 'Semi-Protected':
                    bg = 'yellow'
                    zonetypep = 'Uso Sustentável'
            elif str(zonetype) == 'Unprotected':
                bg = 'red'
                zonetypep = 'Não protegido'
                
            self.list_zone.insert(tk.END, 'Bairro:  ' + name)
            self.list_zone.insert(tk.END, 'População: ' + str(population))
            self.list_zone.insert(tk.END, 'Área de Bairro (km^2): ' + str(round(area/(1000*1000))))
            self.list_zone.insert(tk.END, 'Perda de Manguezais (m^2): ' + str(round(area_of_loss)))
            self.list_zone.insert(tk.END, '2017 Emprego Total: ' + str(emp))
            self.list_zone.insert(tk.END, '2017 Emprego Agrícola: ' + str(agri))
            self.list_zone.insert(tk.END, 'Status: ' + str(zonetypep))

            self.list_zone.itemconfig(tk.END, {'bg':bg})
    
            #Add Selection Functionality to Zone Information Display
            self.clickname = name
        else:
            self.clickname = []
            
        self.clickevent = event
        

        
# =============================================================================
#   Define Data Display Functions  
# =============================================================================
              
    def zone_type(self,name):
        """CREATE WINDOW WITH ZONE TYPE OPTIONS
    
        Args:
            name: Name of zone to be changed
               
        Returns:
            N/A
        """
        
        if name != []:
            #Creat window and label
            zone_window = tk.Toplevel(self)
            zone_window.title('Definir Status de Conservação')
            zone_window.geometry("+1200+750")
            lbl_text = tk.Label(zone_window, text='Definir Status de Conservação', font=('Arial',24))
            lbl_text.grid(column=1, row=0)
            
            #Create each option
            button1 = tk.Button(zone_window, text='Conservação', command=lambda: self.change_zone_type(name, 'Conservation',zone_window))
            button1.grid(column=0, row=1) 
            button2 = tk.Button(zone_window, text='Uso Sustentável', command=lambda: self.change_zone_type(name, 'Semi-Protected',zone_window))
            button2.grid(column=1, row=1) 
            button3 = tk.Button(zone_window, text='Não conservado', command=lambda: self.change_zone_type(name, 'Unprotected',zone_window))
            button3.grid(column=2, row=1)

             
    def change_zone_type(self,name,newtype, parent):
        """CHANGE ZONE TYPE ON SHAPEFILE AND UPDATE DISPLAY
    
        Args:
            name: name of the zone to be changed
            newtype: type to change the zonetype to
            parent: window generated by zone_type
               
        Returns:
            N/A
        """
        
        #Save Changed Zone Type(s) to a temporary file
        r1 = self.zones.shps[self.zones.setting.get()]
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
                if newtype == 'Conservation':
                    numz = 0
                elif newtype == 'Semi-Protected':
                    numz = 1
                elif newtype == 'Unprotected':
                    numz = 2
                shaperec.record['Zone_TypeN'] = numz
            w1.record(*shaperec.record)
            w1.shape(shaperec.shape)
        # Close and save the altered shapefile
        w1.close()
        
        #Copy the temporary file back over the original shapefile
        ShapefileFormatter.ShapeFileCopier('./temp', self.zones.filepaths[self.zones.setting.get()])
        
        #Reload all of the zone shapefiles
        self.zones.shps[self.zones.setting.get()] = shapefile.Reader(self.zones.filepaths[self.zones.setting.get()])


        if str(newtype) == 'Conservation':
            bg = 'green'
            zonetypep = 'Conservação'
        elif str(newtype) == 'Semi-Protected':
            bg = 'yellow'
            zonetypep = 'Uso Sustentável'
        elif str(newtype) == 'Unprotected':
                bg = 'red'
                zonetypep = 'Não conservado'
                
        #Update Zone Information Display
        self.list_zone.delete(tk.END)
        self.list_zone.insert(tk.END, 'Status: ' + zonetypep)
        
                
        self.list_zone.itemconfig(tk.END, {'bg':bg})
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
        for (filepath, original) in zip(self.zones.filepaths, self.zones.original_filepaths):
            if (filepath != []) and (original != []):
                ShapefileFormatter.ShapeFileCopier(original, filepath)
        
        #Reload all of the zoneshapefiles
        self.zones.shps = []
        for shpname in self.zones.filepaths:
            if shpname == []:
                self.zones.shps.append([])
            else:
                self.zones.shps.append(shapefile.Reader(shpname))
        
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
        self.overlays.shps_present = self.overlays.shps
        self.overlays.shps_future = []
        self.overlays.shps_future.append(self.overlays.shps[0])
        self.overlays.shps_future.append(self.overlays.shps[1])

        self.zones.shps_present = self.zones.shps
        self.zones.shps_future = self.zones.shps
        
        self.mangrovehealth_future = FutureCalculations.mangrovehealthchange(self, self.zones.shps[1], self.overlays.shps[2])
        self.overlays.shps_future.append(self.mangrovehealth_future)
        
        self.show_future()

        
    
    def show_future(self):
        """DISPLAY CALCULATED VALUES FOR THE FUTURE
    
        Args:
            N/A
               
        Returns:
            N/A
            
        """
        #### ADD ACTUAL CALULATIONS HERE ####
        if self.tense == 0:
            self.btn_future.config(text='Mostrar Presente')
            self.overlays.shps = self.overlays.shps_future
            self.zones.shps = self.zones.shps_future
            self.replace_map_image()
            self.change_tense_labels(1)



        else:
            self.btn_future.config(text='Mostrar Futuro Simulado')
            
            self.overlays.shps = self.overlays.shps_present
            self.zones.shps = self.zones.shps_present
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



