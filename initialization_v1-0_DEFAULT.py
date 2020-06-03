#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 16:44:58 2020

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
from tkinter import filedialog
import shutil

import sys
sys.path.insert(1, '/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/Auxillary Scripts')

import ShapefileFormatter
import MapWindow_v4 as MapWindow
import FutureCalculations_v1 as FutureCalculations
import userinterface_v2_5 as userinterface
from MapType_v2 import *
from fieldnamelookup import *

class EVDT_Initialization(tk.Frame):

    
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
                

        
        self.uoa_filepaths = []
        self.uoa_defaults = []
        self.map_filepaths = []
        self.overlay_filepaths = []
        self.overlay_colors = []
        self.overlay_color_titles = []
        self.root = root
        self.increment = 0
        self.make_frame(root)
        
        # test = self.append_text('/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/scratchpaper.py', 'testing')
        # print(test)
        

        
        
    def make_frame(self,root):
        
        frame = tk.Frame(root)
        frame.pack()
        
        if self.increment == 0:
            appendvariable = self.uoa_filepaths
            appenddefault = self.uoa_defaults

            label = tk.Label(frame, text='Step 1. Select Unit of Analysis Shapefiles', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import UOA Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=1)
            elif len(appendvariable) > len(appenddefault):
                
                
                
                importbutton = tk.Button(frame, text='Import Associated Default UOA Shapefile', 
                                       command= lambda: self.import_filepath(appenddefault, frame, self.make_frame))
                importbutton.grid(column=0, row=1)
                importbutton = tk.Button(frame, text='Generate Associated Default UOA Shapefile', 
                                       command= lambda: self.generate_default(appendvariable[-1], appenddefault, frame, self.make_frame))
                importbutton.grid(column=0, row=2)
            else:
                
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another UOA Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=2)
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
                
        elif self.increment == 1:            
            appendvariable = self.map_filepaths
        
            label = tk.Label(frame, text='Step 2. Select Background Map Images', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import Background Image', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=1)
            else:
                
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another Background Image', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=2)
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
                
        elif self.increment == 2:            
            appendvariable = self.overlay_filepaths
            appenddefault = self.overlay_colors
        
            label = tk.Label(frame, text='Step 3. Select Map Overlay Shapefiles', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import Overlay Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=1)
                
            elif len(appendvariable) > len(appenddefault):
                
                color_label = tk.Label(frame, text='Select field to be used for color visualization', font=('Arial',24))
                color_label.grid(column=0, row=1) 
                
                r = shapefile.Reader(appendvariable[-1])
                fieldlist = r.fields
                del fieldlist[0]
                fieldlist = list(list(zip(*fieldlist))[0])
                
                color_setting_name = tk.StringVar()
                color_setting_name.set(fieldlist[0])
                
                coloroptionlist = tk.OptionMenu(frame, color_setting_name,
                                   *fieldlist
                                   )
                coloroptionlist.grid(column=0, row=2)
                
                color_title_label = tk.Label(frame, text='Type full name of the field', font=('Arial',24))
                color_title_label.grid(column=0, row=3)
                
                color_entry = tk.Entry(frame)
                color_entry.grid(column=0, row=4)
                
                color_button = tk.Button(frame, text='Done', 
                                       command= lambda: self.append_color(color_setting_name.get(), color_entry.get(), frame, self.make_frame))
                color_button.grid(column=0, row=5)
                
                
            else:                
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another Overlay Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, self.make_frame))
                importbutton.grid(column=0, row=2)
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
        elif self.increment == 3:
            self.uoa_filepath.insert(0, [])
            self.map_filepaths.insert(0,[])
            self.overlay_filepaths.insert(0, [])
            for entry in self.overlay_colors:
                entry.append(0, [])
            for entry in self.overlay_color_titles:
                entry.append(0, [])
                
            userinterface.EVDT(self.root, 
                               uoa = [self.uoa_filepaths, self.uoa_defaults],
                               mapimgs = self.map_filepaths,
                               overlay = [self.overlay_filepaths, self.overlay_colors, self.overlay_color_titles])
                
    
    
    def import_filepath(self, appendvariable, frame, framefunc):
        filepath, = filedialog.askopenfilenames(title='Import shapefile')
        appendvariable.append(filepath)
            
        frame.destroy()        
        framefunc(self.root) 
            
    def generate_default(self, filepath, appendvariable, frame, framefunc):
        defaultfilepath = self.append_text(filepath, 'DEFAULT')
        shutil.copy(filepath, defaultfilepath)
        appendvariable.append(defaultfilepath)
        
        frame.destroy()
        framefunc(self.root)

   
    def append_text(self, filename, appendtext):
        return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [appendtext])
            
    
    def increment_frame(self, frame):
        self.increment += 1
        frame.destroy()
        self.make_frame(self.root)
        
        
    def append_color(self, colorfield, colortitle, frame, framefunc):
        self.overlay_colors.append(colorfield)
        self.overlay_color_titles.append(colortitle)
        frame.destroy()
        self.make_frame(self.root)
        
        

        
if str.__eq__(__name__, '__main__'):
       
    window = tk.Tk()
    window.title('EVDT Interactive Simulation')
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=20)
    EVDT_Initialization = EVDT_Initialization(window)
    window.mainloop()

        