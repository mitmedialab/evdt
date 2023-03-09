#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:11:58 2020

@author: jackreid
"""

import tkinter as tk
import PIL as pil
from PIL import ImageTk
from tkinter.font import Font
import MapWindow

window = tk.Tk()
window.title('EVDT Interactive Simulation')
# window.overrideredirect(True)
# window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))
default_font = tk.font.nametofont("TkDefaultFont")
default_font.configure(size=20)


# =======================================
# MAP LAYERS
#Notes: Need to add commands to each of the Checkbuttons that update the map appropriately

frame_layers = tk.Frame(window)
frame_layers.grid(column=0, row=0)

lbl_layers = tk.Label(frame_layers, text='Map Layers', font=('Arial',24))
lbl_layers.grid(column=0, row=0)

var1 = tk.IntVar() 
var1.set(1)
tk.Button(frame_layers, text='Base Map').grid(column=0, row=1) 
var2 = tk.IntVar() 
var2.set(0)
tk.Button(frame_layers, text='Transit').grid(column=0, row=2)
var3 = tk.IntVar() 
var3.set(0)
tk.Button(frame_layers, text='Mangrove Extent').grid(column=1, row=1) 
var4 = tk.IntVar() 
var4.set(0)
tk.Button(frame_layers, text='Mangrove Health').grid(column=1, row=2) 

# =======================================
# MAP WINDOW
#https://stackoverflow.com/questions/36328547/changing-the-shape-of-tkinter-widgets
#http://effbot.org/tkinterbook/place.htm
# =https://github.com/afourmy/pyGISS


# window2 = tk.Tk()
# window2.title('test')

frame_map = tk.Frame(window)
frame_map.grid(column=0, row=1)

# testcanvas = tk.Canvas(frame_map)

mapimg = MapWindow.Map(frame_map,'/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/FormatedShapefiles/Bairros.shp')

# load = pil.Image.open("/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/map.jpg")
# render = ImageTk.PhotoImage(load)
# img = tk.Label(frame_map, image=render)
# img.image = render
# img.grid(column=0, row=0)

# label_date = tk.Label(frame_map, text='September 2018', font=('Arial', 24), fg='red' )
# label_date.place(relx=1, x=-2, y=2, anchor='ne')
# label_real = tk.Label(frame_map, text='Real Data', font=('Arial', 24), fg='red' )
# label_real.place(relx=1, x=-2, y=35, anchor='ne')


# =======================================
# INFORMATION DISPLAY

frame_info = tk.Frame(window)
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

# =======================================
# CONTROL BUTTONS

frame_control = tk.Frame(window)
frame_control.grid(column=0, row=2)

btn_zones = tk.Button(frame_control, text="Planning Zones")
btn_zones.grid(column=0, row=0)
btn_calculate = tk.Button(frame_control, text="Calculate")
btn_calculate.grid(column=1, row=0)
btn_future = tk.Button(frame_control, text="Show Simulated Future")
btn_future.grid(column=5, row=0)




window.mainloop()