#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:57:03 2020

@author: jackreid
"""
import shapefile
# import ShapefileFormatter
import tkinter as tk
from tkinter.ttk import Progressbar
import tkinter.font

shppath = './FormatedShapefiles/Bairros/Bairros_Custom.shp'
# # datapath = './Population.xlsx'
# writepath = './FormatedShapefiles/Bairros_with_Population.shp'

zoneshp = shapefile.Reader(shppath)
mangrovehealthshp = shapefile.Reader('./FormatedShapefiles/Mangroves/m_health.shp')


root = tk.Tk()
test = tk.StringVar()
test.set([])

print(root.winfo_rgb('black'))

# canvas = tk.Canvas(width=200, height=200)

progress = Progressbar(root, orient = 'horizontal', 
              length = 1000, mode = 'determinate') 
 
  
# Function responsible for the updation 
# of the progress bar value 
def bar(): 
    # import time 
    # progress['value'] = 20
    # root.update_idletasks() 
    # time.sleep(1) 
  
    # progress['value'] = 40
    # root.update_idletasks() 
    # time.sleep(1) 
  
    # progress['value'] = 50
    # root.update_idletasks() 
    # time.sleep(1) 
  
    # progress['value'] = 60
    # root.update_idletasks() 
    # time.sleep(1) 
  
    # progress['value'] = 80
    # root.update_idletasks() 
    # time.sleep(1) 
    # progress['value'] = 100
    i=0
    totalshapes = len(mangrovehealthshp.shapes())
    for shaperec in mangrovehealthshp.iterShapeRecords():
        i+=1
        print(shaperec.record)
        
        if i%100 == 0:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            progress['value'] = i/totalshapes*100
            root.update_idletasks()

  
progress.pack(pady = 10) 
  
# This button will initialize 
# the progress bar 
myfont = tkinter.font.Font(family="Arial", size=24)
b=tk.Button(root, text = 'Start', command = bar, font=myfont)
b.pack(pady = 10) 

w=tk.Scale(root, from_=50, to=500, orient='horizontal',)
w.bind("<ButtonRelease-1>",  lambda e: print(w.get()))
w.pack(pady = 10)

# canvas.pack()

root.mainloop()