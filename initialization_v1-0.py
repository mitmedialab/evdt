#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates the EVDT_Initialization class which is a series of windows allowing for inputs into the EVDT model


Created on Tue May  5 16:44:58 2020

@author: jackreid
"""

import tkinter as tk
import tkinter.font
import tkinter.ttk
import shapefile
from tkinter import filedialog
import shutil

import userinterface_v2_5 as userinterface


class EVDT_Initialization(tk.Frame):

# =============================================================================
#     Initiating Import Interface
# =============================================================================
    
    
    def __init__(self, root):
        """INITIATE EVDT_INITIALIZATION CLASS
    
        Args:
            root: tk window or frame for the EVDT_Initialization and EVDT to sit in
               
        Returns:
            N/A
        """
        
        super().__init__(root, bg='white', width=1300, height=800)
                
        
        #Prepare the various output variables
        self.uoa_filepaths = []
        self.uoa_defaults = []
        self.uoa_names = []
        self.map_filepaths = []
        self.map_names = []
        self.overlay_filepaths = []
        self.overlay_colors = []
        self.overlay_color_titles = []
        self.overlay_names = []
        
        
        #Store other relevant variables
        self.root = root
        self.increment = 0
        
        
        #Generate the initial window
        self.make_frame(root)


# =============================================================================
#     Import Window Definition and Logic
# =============================================================================
        
    def make_frame(self,root):
        """GENERATE PRIMARY INPUT WINDOWS
    
        Args:
            root: tk window or frame for frame to sit in
               
        Returns:
            N/A
        """
        
        
        #Generate Frame
        frame = tk.Frame(root)
        frame.pack()
        
        
        #Generate UOA Input Window
        if self.increment == 0:
            appendvariable = self.uoa_filepaths
            appenddefault = self.uoa_defaults

            label = tk.Label(frame, text='Step 1. Select Unit of Analysis Shapefiles', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            
            #Initial Input
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import UOA Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1),
                                       )
                importbutton.grid(column=0, row=1)
                
            
            #Make sure there is a default for each shapefile
            elif len(appendvariable) > len(appenddefault):
                importbutton = tk.Button(frame, text='Import Associated Default UOA Shapefile', 
                                       command= lambda: self.import_filepath(appenddefault, frame))
                importbutton.grid(column=0, row=1)
                importbutton = tk.Button(frame, text='Generate Associated Default UOA Shapefile', 
                                       command= lambda: self.generate_default(appendvariable[-1], appenddefault, frame))
                importbutton.grid(column=0, row=2)
                
            
            #Allow for the import of additional shapefiles
            else:
                
                
                #Display list of currently imported shapefiles
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another UOA Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1)
                                       )
                importbutton.grid(column=0, row=2)
                
                #Move on to next input
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
                
                
        #Generate Background Image Input Window
        elif self.increment == 1:            
            appendvariable = self.map_filepaths
        
            label = tk.Label(frame, text='Step 2. Select Background Map Images', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            
            #Initial Input
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import Background Image', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1)
                                       )
                importbutton.grid(column=0, row=1)
                
                
            #Allow for the import of additional shapefiles
            else:
                
                
                #Display list of currently imported shapefiles
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another Background Image', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1)
                                       )
                importbutton.grid(column=0, row=2)
                
                #Move on to next input
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
                
                
        #Generate Overlay Shapefile Input Window
        elif self.increment == 2:            
            appendvariable = self.overlay_filepaths
            appenddefault = self.overlay_colors
        
            label = tk.Label(frame, text='Step 3. Select Map Overlay Shapefiles', font=('Arial',24))
            label.grid(column=0, row=0) 
            
            
            #Initial Input
            if len(appendvariable) == 0:
                importbutton = tk.Button(frame, text='Import Overlay Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1)
                                       )
                importbutton.grid(column=0, row=1)
                
                
            #Make sure there is a color selection for each shapefile
            elif len(appendvariable) > len(appenddefault):
                
                color_label = tk.Label(frame, text='Select field to be used for color visualization', font=('Arial',24))
                color_label.grid(column=0, row=1) 
                
                
                #Pull shapefile fields to be options
                r = shapefile.Reader(appendvariable[-1])
                fieldlist = r.fields
                del fieldlist[0]
                fieldlist = list(list(zip(*fieldlist))[0])
                
                #Allow for field selection
                color_setting_name = tk.StringVar()
                color_setting_name.set(fieldlist[0])
                coloroptionlist = tk.OptionMenu(frame, color_setting_name,
                                   *fieldlist
                                   )
                coloroptionlist.grid(column=0, row=2)
                
                #Input longform name of the field
                color_title_label = tk.Label(frame, text='Type full name of the field', font=('Arial',24))
                color_title_label.grid(column=0, row=3)
                color_entry = tk.Entry(frame)
                color_entry.grid(column=0, row=4)
                
                #Move on to next input
                color_button = tk.Button(frame, text='Done', 
                                       command= lambda: self.append_color(color_setting_name.get(), color_entry.get(), frame))
                color_button.grid(column=0, row=5)
                
                
            #Allow for the input of additional shapefiles
            else:                
                
                
                #Display list of currently imported shapefiles
                list_filepaths = tk.Listbox(frame, width=125)
                for entry in appendvariable:
                    list_filepaths.insert(tk.END, entry)
                list_filepaths.grid(column=0, row=1) 
                
                importbutton = tk.Button(frame, text='Import Another Overlay Shapefile', 
                                       command= lambda: self.import_filepath(appendvariable, frame, askname=1)
                                       )
                importbutton.grid(column=0, row=2)
                
                #Move on to the next input
                continuebutton = tk.Button(frame, text='Done', command= lambda: self.increment_frame(frame))
                continuebutton.grid(column=0, row=3)
                
        
        #Export all the imported filepaths to the EVDT model
        elif self.increment == 3:
            self.uoa_filepaths.insert(0, [])
            self.map_filepaths.insert(0,[])
            self.map_names.insert(0,'Nenhum')
            self.overlay_filepaths.insert(0, [])
            self.overlay_names.insert(0, 'Nenhum')
            for entry in self.overlay_colors:
                entry.insert(0, [])
            for entry in self.overlay_color_titles:
                entry.insert(0, [])
            
            frame.destroy()
            
            userinterface.EVDT(self.root, 
                               uoa = [self.uoa_filepaths, self.uoa_defaults, self.uoa_names],
                               mapimgs = [self.map_filepaths, self.map_names],
                               overlay = [self.overlay_filepaths, self.overlay_colors, self.overlay_color_titles, self.overlay_names])
                
    
# =============================================================================
#    Auxillary Functions
# =============================================================================    


    def import_filepath(self, appendvariable, frame, **kwargs):
        """IMPORT SHAPEFILE AND APPEND TO THE APPROPRIATE VARIABLE
    
        Args:
            appendvariable: variable for the filepath to be appended to
            frame: Tk frame that will need to be closed after import
            askname: optional flag. For 1, will generate a window asking for a longform name. Default is 0.
               
        Returns:
            N/A
        """
        
        #Import Filepath and append to appropriate variable
        filepath, = filedialog.askopenfilenames(title='Import shapefile')
        appendvariable.append(filepath)
            
        
        #Check if there is a need for a longform name, default is no
        if 'askname' in kwargs:
            askname=kwargs.pop('askname')
        else:
            askname = 0
            
        
        #Ask for longform name
        if askname == 1:
            frame.destroy()
            self.ask_for_name()
        #Destroy frame and move on to next input
        else:
            frame.destroy()        
            self.make_frame(self.root) 
            
            
    def generate_default(self, filepath, appendvariable, frame):
        """COPY A SHAPEFILE TO SERVE AS AN UNEDITED DEFAULT FOR THE EVDT MODEL
    
        Args:
            filepath: filepath of the shapefile to be copied
            appendvariable: variable for the filepath to be appended to
            frame: Tk frame that will need to be closed after import
               
        Returns:
            N/A
        """
        
        #Copy the shapefile and add "DEFAULT" to its filename
        defaultfilepath = self.append_text(filepath, 'DEFAULT')
        shutil.copy(filepath, defaultfilepath)
        appendvariable.append(defaultfilepath)
        
        #Destroy the frame and move on to the next input
        frame.destroy()
        self.make_frame(self.root)

   
    def append_text(self, filename, appendtext):
        """APPENDS TEXT TO THE END OF THE FILENAME (BEFORE THE EXTENSION)
    
        Args:
            filename: filename to append text to
            appendtext: text to append to the end of the filename (before the extension)
               
        Returns:
            String that is the input filename appended with "_appendtext"
        """
        return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [appendtext])
            
    
    def increment_frame(self, frame):
        """INCREMENTS THE STATE OF THE INPUT WINDOW (MOVES ONTO NEXT VARIABLE TO BE IMPORTED)
    
        Args:
            frame: Tk frame that will need to be closed after increment
               
        Returns:
            N/A
        """
        
        self.increment += 1
        frame.destroy()
        self.make_frame(self.root)
        
        
        
    def append_color(self, colorfield, colortitle, frame):
        """APPENDS COLOR FIELD AND COLOR TITLE TO OVERLAY VARIABLES AND RETURNS TO IMPORT WINDOW
    
        Args:
            colorfield: Name of the shapefile field to be used for coloring the overlay shapes
            colortitle: The longform name of the shapefile field
            frame: Tk frame that will need to be closed after increment
               
        Returns:
            N/A
        """
        
        self.overlay_colors.append([colorfield])
        self.overlay_color_titles.append([colortitle])
        frame.destroy()
        self.make_frame(self.root)
        
        
        
    def ask_for_name(self):
        """GENERATES WINNDOW TO INPUT A LONGFORM NAME ASSOCIATED WITH AN IMPORTED FILE
    
        Args:
            N/A
               
        Returns:
            N/A
        """
        
        #Generate new frame
        frame = tk.Frame(self.root)
        frame.pack()
        
        
        #Ask for longform name associated with the imported shapefile
        name_label = tk.Label(frame, text='Type full name of the entry', font=('Arial',24))
        name_label.grid(column=0, row=0)
        name_entry = tk.Entry(frame)
        name_entry.grid(column=0, row=1)
        name_button = tk.Button(frame, text='Done', 
                                       command= lambda: self.append_name(name_entry.get(), frame))
        name_button.grid(column=0, row=5)
        
        
        
    def append_name(self, entry, frame):
        """APPENDS LONGFORM NAME TO THE APPROPRIATE VARIABLE
    
        Args:
            entry: longform name to be appended
            frame: Tk frame that will need to be closed after increment
               
        Returns:
            N/A
        """
        
        #Determines appropriate longform name variable to append to
        if self.increment == 0:
            self.uoa_names.append(entry)
        elif self.increment == 1:
            self.map_names.append(entry)
        elif self.increment == 2:
            self.overlay_names.append(entry)
            
            
        #Destroy the frame and move on to the next input
        frame.destroy()
        self.make_frame(self.root)
            
        
        
# =============================================================================
#   Main Script
# =============================================================================  

        
if str.__eq__(__name__, '__main__'):
       
    window = tk.Tk()
    window.title('EVDT Interactive Simulation')
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=20)
    EVDT_Initialization = EVDT_Initialization(window)
    window.mainloop()

        