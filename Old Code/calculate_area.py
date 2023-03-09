'''
A tool to calculate the area of the polygon geometries in a ESRI shapefile.

Arguments:
--config: Configuration file pointing to shapefile datasource

Dependencies:
    Python Shapefile Library - pyshp [https://code.google.com/p/pyshp/]
    
Usage:
    Run script:
        python calc_area.py -c <config_file>

@author: rmurray
'''
# import os
# import sys
# import ConfigParser
# import argparse

import shapefile


# Shapefile spec says POLYGON type == 5 || POLYGONZ == 15 (shouldnt have POLYGONZ but the regions shapefile has the z)
VALID_SHAPE_TYPES = [5, 15]


def poly_area2D(poly):
    '''
    An implementation of Green's theorem, an algorithm to calculate area of 
    a closed polgon. This works for convex and concave polygons that do not
    intersect oneself whose vertices are described by ordered pairs.

    Args:
        poly: The polygon expressed as a list of vertices, or 2D vector points
    '''

    # ensure we have a list; best to assert that it isnt a string as in python several types can
    # act as a list
    # assert not isinstance(poly, basestring) 

    total = 0.0
    N = len(poly)
    for i in range(N):
        v1 = poly[i]
        v2 = poly[(i+1) % N]
        total += v1[0]*v2[1] - v1[1]*v2[0]
    return abs(total/2)


def main():
    '''
    Main method; parse shapefile and loop through specific features calculating the area
    '''

    #include_attribute_file = false

    parser = argparse.ArgumentParser(description='calculate area of shapefile geometries')
    parser.add_argument('-c', '--config', dest='configFile')
    arguments = parser.parse_args()

    # ensure that all args are present
    if not arguments.configFile:
        raise Exception("Missing argument")

    if not os.path.isfile(arguments.configFile):
        raise Exception("Missing config file")

    # parse args
    configParser = ConfigParser.RawConfigParser()
    configParser.read([arguments.configFile])

    #grab config file params
    shapefile_path = configParser.get('shapefile', 'shapefile')
    attributefile_path = configParser.get('shapefile', 'attributefile')

    if not os.path.isfile(shapefile_path) and not os.path.isfile(attributefile_path):
        raise Exception("Cant find file")

    sf = shapefile.Reader( shp=open(shapefile_path, 'rb'), dbf=open(attributefile_path, 'rb') )

    # extract shapes and attribute data
    shapes = sf.shapes()
    records = sf.records()

    print('Found %i geometries in file' % len(shapes))
    print('Field header data is:' )
    print(sf.fields)

    # loop through shapes displaying data
    i = 0
    for shape in shapes:

        # only work with shape types we know will be a valid geometry
        if shape.shapeType in VALID_SHAPE_TYPES:

            print('--------')
            rec = sf.record(i)
            print('attributes: %s' % rec)
            print('bbox: %s' % shape.bbox)

            area_m2 = poly_area2D(shape.points)
            area_km2 = area_m2 / 1000000 # 1000000m2 in 1km2

            print('Shape polygon is %.2f m2' % area_m2)
            print('Shape polygon is %.6f km2' % area_km2)
            print('Shape polygon is %.0f km2' % area_km2)

        i = i+1


if __name__ == "__main__":
    main()
    print("** Le Fin. **")

