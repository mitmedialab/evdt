import tkinter as tk
import pyproj
import shapefile
import shapely.geometry
import PIL as pil
from PIL import ImageTk, Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

class Map(tk.Canvas):

    projections = {
        'mercator': pyproj.Proj(init="epsg:3857"),
        'spherical': pyproj.Proj('+proj=ortho +lon_0=28 +lat_0=47')
        }

    def __init__(self, root, filepathname, **kwargs):
        super().__init__(root, width=1300, height=800)
        self.proj = 'mercator'
        self.ratio = 1
        self.offset = (0, 0)
        # self.bind('<ButtonPress-1>', self.print_coords)
        self.bind('<ButtonPress-3>', lambda e: self.scan_mark(e.x, e.y))
        self.bind('<B3-Motion>', lambda e: self.scan_dragto(e.x, e.y, gain=1))
        self.set_canvas_location(-43.5765151113451, -22.9969539088035, 0.03)
        self.polyimages = []
        self.filepathname = filepathname

        if 'background_image' in kwargs:
            imagename = kwargs.pop('background_image')
            load = pil.Image.open(imagename)
            load = load.resize((1300, 800), Image.ANTIALIAS)
            self.background = ImageTk.PhotoImage(load)
            self.create_image(0,0,image=self.background,anchor='nw')

        if 'color_range' in kwargs:
            self.color_rangename = kwargs.pop('color_range')
        else:
            self.color_rangename = []
            
        self.draw_map(filepathname)
        self.pack(fill='both', expand=1)


        

    def to_canvas_coordinates(self, longitude, latitude):
        px, py = self.projections[self.proj](longitude, latitude)
        return px*self.ratio + self.offset[0], -py*self.ratio + self.offset[1]

    def to_geographical_coordinates(self, x, y):
        px, py = (x - self.offset[0])/self.ratio, (self.offset[1] - y)/self.ratio
        return self.projections[self.proj](px, py, inverse=True)
    
    def set_canvas_location(self, longitude, latitude, zoomlevel):
        locationx, locationy = self.to_canvas_coordinates(longitude, latitude)
        self.move('all', -locationx, -locationy)
        self.offset = (
            self.offset[0] - locationx,
            self.offset[1] - locationy
        )
        # height, width = self.winfo_height()/2, self.winfo_width()/2
        width, height = 943.0, 471.0
        self.scale('all', width, height, zoomlevel, zoomlevel)
        self.configure(scrollregion=self.bbox('all'))
        self.ratio *= float(zoomlevel)
        self.offset = (
            self.offset[0]*zoomlevel + width*(1 - zoomlevel),
            self.offset[1]*zoomlevel + height*(1 - zoomlevel)
        )
  
    def colorrange(self, shp, valuename):
                sf = shp
                values = []
                for record in sf.records():
                    values.append(record[valuename])
                    
                minim = min(values)
                maxim = max(values)
                valuerange = maxim - minim
                return valuerange, minim

        
        
    def draw_polygon(self, coordinates, **kwargs):
        # coordinates = list(zip(coordinates[0::2],coordinates[1::2]))

            
        if 'fill' in kwargs:
            fill = tuple(kwargs.pop('fill'))
            # print(fill)
            # print(type(fill))
        else:
             fill = 'green'
             fill = self.winfo_rgb(fill)
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            # print(type(alpha))
        else:
            alpha = 1
            alpha = int(alpha*255)
            
        fill = fill + (alpha,)  
        poly = Image.new('RGBA', (1300,800))
        pdraw = ImageDraw.Draw(poly)
        pdraw.polygon(coordinates,
                  fill,outline='red')
        newimage = (ImageTk.PhotoImage(poly))
        # x, y = [], []
        # x, y = coordinates[0::2], coordinates[1::2]
        # avgx, avgy = sum(x)/len(x), sum(y)/len(y)
        self.create_image(1,1, image=newimage, anchor='nw', tags=('land',))
        return newimage
        
    def draw_map(self, filepathname, **kwargs):
        self.delete('land', 'water')
        self.draw_water()
        sf = shapefile.Reader(filepathname)
        if self.color_rangename != []:
            valuerange, minim = self.colorrange(sf, self.color_rangename)
            colormap = cm.get_cmap('bwr', 12)
            
        for shaperec in sf.iterShapeRecords():
            # convert shapefile geometries into shapely geometries
            # to extract the polygons of a multipolygon
            polygon = shapely.geometry.shape(shaperec.shape)
            if polygon.geom_type == 'Polygon':
                polygon = [polygon]
            # print(polygon)
            for land in polygon:
                coordinates = sum((self.to_canvas_coordinates(*c) for c in land.exterior.coords), ())
                if self.color_rangename != []:
                    value = shaperec.record[self.color_rangename]
                    normvalue = (value - minim) / valuerange
                    fill1 = colormap(normvalue)[0:3]
                    fill = [int(x*255) for x in fill1]
                    alpha = 0.5
                else:
                    fill = self.winfo_rgb('green')
                    alpha = 0
                newimage = self.draw_polygon(coordinates, fill=fill, alpha=alpha)
                self.polyimages.append(newimage)
                # self.create_polygon(
                #     sum((self.to_canvas_coordinates(*c) for c in land.exterior.coords), ()),
                #     fill='green',
                #     outline='red',
                #     tags=('land',)
                # )


    def draw_water(self):
        x0, y0 = self.to_canvas_coordinates(-180, 84)
        x1, y1 = self.to_canvas_coordinates(180, -84)
        self.water_id = self.create_rectangle(
            x1, y1, x0, y0,
            outline='black',
            fill = '',
            tags=('water',)
        )
            
       
    # def print_coords(self, event):
    #     # print(event.x, event.y)
    #     event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
    #     print(self.to_geographical_coordinates(event.x, event.y))



if str.__eq__(__name__, '__main__'):
    root_window = tk.Tk()
    root_window.title('MapWindow')
    py_giss = Map(root_window, './FormatedShapefiles/Bairros.shp',background_image='./map.jpg')
    root_window.mainloop()
