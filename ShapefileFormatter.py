#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:54:50 2019

@author: jackreid

This script contatins two a functions, both pertaining to editing and copying shapefiles

"""

def ShapefileFormatter(shpfilepath, datapath,fieldname, fieldabr, writepath):
    """Uses pandas to import an Excel matrix as a Dataframe and format it
    to pull out Median Household Income for each county in the US
    
    It then uses the pyshp library (also known as shapefile) to import a shapefile
    containing geometries of each state in the US. 
    
    Finally it saves a new shapefile that is a copy of the imported one, with 
    Median Household Income appended to the record of each county.
    
    [NOTE: CURRENTLY CONFIGURED TO LOOK FOR BAIRRO NAME MATCHES]
    
    Args:
        shpfilepath: file path to the input shapefile
        datapath: file path to the excel spreadsheet with the relevant data.
        fieldname: the column title in the spreadsheet of the data to be added
        fieldabr: the actual title of the field to be added to the shapefile
        writepath: destination and title of the output shapefile
                           
    Returns:
        r2: The output shapefile that was saved to write path.
        """
        
    import pandas as pd
    import shapefile
    
    #Import and Format the Excel Data
    df = pd.read_excel (datapath) 
    df_range = df.iloc[:,0:2] 
    df_range[fieldname] = df.loc[:,fieldname]
    
    # Read in original shapefile
    r = shapefile.Reader(shpfilepath)
    
    # Create a new shapefile in memory
    w = shapefile.Writer(writepath)
    
    # Copy over the existing fields
    fields = r.fields
    for name in fields:
        if type(name) == "tuple":
            continue
        else:
            args = name
            w.field(*args)
            
    # Add new field for data
    w.field(fieldabr, "N", 10)
    
    
    #Define a function to identify spreadsheet value based on name
    def dataextract(entry):
        name = entry['BAIRRO']
        print('LOOKING FOR:', name)
        # print(name)
        namerow =  df_range.loc[(df['NAME']==name)]
        print('NAMEROW IS:', namerow)
        if namerow.empty:
            namevalue = 0
            print('NAME NOT FOUND')
        else:
            namevalue = namerow.iloc[0,1] 
            print('VALUE IS:', namevalue)
        return namevalue
    
    
    # Copy over exisiting records and geometries, appending MHI to each record
    for shaperec in r.iterShapeRecords():
        appendvalue = dataextract(shaperec.record)
        shaperec.record.append(appendvalue)
        w.record(*shaperec.record)
        w.shape(shaperec.shape)
    
    # Close and save the altered shapefile
    w.close()
    return shapefile.Reader(writepath)

def ShapeFileCopier(shppath, writepath):
    """Reads and copies a shapefile to a new shapefile.
        Args:
           shpfilepath: file path to the input shapefile
           writepath: destination and title of the output shapefile
                           
        Returns:
            N/A
        """
        
    import shapefile
   
    r = shapefile.Reader(shppath)
    w = shapefile.Writer(writepath)
 
    # Copy over the existing fields
    fields = r.fields
    for name in fields:
        if type(name) == "tuple":
            continue
        else:
            args = name
            w.field(*args)
            
    #Copy over the existing shapes and records
    for shaperec in r.iterShapeRecords():
        w.record(*shaperec.record)
        w.shape(shaperec.shape)
    
    # Close and save the altered shapefile
    w.close()


