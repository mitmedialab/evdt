import tkinter as tk
import pyproj
import shapefile
import shapely.geometry


class Map(tk.Canvas):

    projections = {
        'mercator': pyproj.Proj(init="epsg:3395"),
        'spherical': pyproj.Proj('+proj=ortho +lon_0=28 +lat_0=47')
        }

    def __init__(self, root, filepathname):
        super().__init__(root, bg='white', width=1300, height=800)
        self.proj = 'mercator'
        self.ratio = 1
        self.offset = (0, 0)
        self.bind('<ButtonPress-1>', self.print_coords)
        # self.bind('<Key>', self.testfun)
        # self.bind('<MouseWheel>', self.zoomer)
        # self.bind('<Button-4>', lambda e: self.zoomer(e, 1.3))
        # self.bind('<Button-5>', lambda e: self.zoomer(e, 0.7))
        self.bind('<ButtonPress-3>', lambda e: self.scan_mark(e.x, e.y))
        self.bind('<B3-Motion>', lambda e: self.scan_dragto(e.x, e.y, gain=1))
        menu = tk.Menu(root)
        self.draw_map(filepathname)
        # menu.add_command(label="Switch projection", command=self.switch_proj)
        root.config(menu=menu)
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
        print(self.offset)
        # height, width = self.winfo_height()/2, self.winfo_width()/2
        width, height = 943.0, 471.0
        self.scale('all', width, height, zoomlevel, zoomlevel)
        self.configure(scrollregion=self.bbox('all'))
        self.ratio *= float(zoomlevel)
        self.offset = (
            self.offset[0]*zoomlevel + width*(1 - zoomlevel),
            self.offset[1]*zoomlevel + height*(1 - zoomlevel)
        )
        print(self.offset)

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
                    fill='green3',
                    outline='black',
                    tags=('land',)
                )
        self.set_canvas_location(-43.58, -22.95, 0.03)


    def draw_water(self):
        x0, y0 = self.to_canvas_coordinates(-180, 84)
        x1, y1 = self.to_canvas_coordinates(180, -84)
        self.water_id = self.create_rectangle(
            x1, y1, x0, y0,
            outline='black',
            fill='deep sky blue',
            tags=('water',)
        )
       

    def print_coords(self, event):
        print(event.x, event.y)
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        print(*self.to_geographical_coordinates(event.x, event.y))
        print(event.x, event.y)

    # def zoomer(self, event, factor=None):
    #     if not factor:
    #         factor = 1.3 if event.delta > 0 else 0.7
    #     event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
    #     self.scale('all', event.x, event.y, factor, factor)
    #     self.configure(scrollregion=self.bbox('all'))
    #     self.ratio *= float(factor)
    #     self.offset = (
    #         self.offset[0]*factor + event.x*(1 - factor),
    #         self.offset[1]*factor + event.y*(1 - factor)
    #     )
    #     print(self.ratio)
    #     print(self.offset)


if str.__eq__(__name__, '__main__'):
    root_window = tk.Tk()
    root_window.title('PyGISS: A GIS software in less than 100 lines of Python')
    py_giss = Map(root_window, '/home/jackreid/Google Drive/School/Research/Space Enabled/Code/Mangroves/UI/FormatedShapefiles/Bairros.shp')
    root_window.mainloop()
