import tkinter as tk
import pyproj
import shapefile
import shapely.geometry
import PIL as pil
from PIL import ImageTk
from PIL import Image

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

        if 'background_image' in kwargs:
            imagename = kwargs.pop('background_image')
            load = pil.Image.open(imagename)
            load = load.resize((1300, 800), Image.ANTIALIAS)
            self.background = ImageTk.PhotoImage(load)
            self.create_image(0,0,image=self.background,anchor='nw')

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
  

    def draw_map(self, filepathname):
        self.delete('land', 'water')
        self.draw_water()
        sf = shapefile.Reader(filepathname)
        polygons = sf.shapes()
        for polygon in polygons:
            # convert shapefile geometries into shapely geometries
            # to extract the polygons of a multipolygon   
            polygon = shapely.geometry.shape(polygon)
            if polygon.geom_type == 'Polygon':
                polygon = [polygon]
            for land in polygon:
                self.create_polygon(
                    sum((self.to_canvas_coordinates(*c) for c in land.exterior.coords), ()),
                    fill='',
                    outline='red',
                    tags=('land',)
                )


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
