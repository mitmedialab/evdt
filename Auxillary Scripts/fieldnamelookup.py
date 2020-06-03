#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fieldnamelookup
Generates the fieldnamelookup class for systematically pulling from field template csvs

Created on Tue Apr 21 14:23:37 2020

@author: jackreid
"""

import csv

    
class fieldnamelookup:
    
    def __init__(self, fieldname, **kwargs):
        self.fieldname = []
        self.longname = []
        self.type = []
        self.choices = []
        self.category = []
        
        
        #Appropriately label ID field
        if fieldname.startswith('I_'):
            with open('./Auxillary Scripts/IDFields.csv') as csv_file:
                csvread = csv.DictReader(csv_file)
                for row in csvread:
                    if row['FieldName'] == fieldname:
                        self.fieldname = fieldname          #fieldname as recorded in the shapefile
                        self.longname = row['LongName']     #longform name as recorded in the csv
                        self.category = 'ID'                #category of field (economic, environmental, etc.)
                        self.type = 'ID'                    #type of field (ID, Action, Other)
                        
                        
        #Appropriately label Action field
        elif fieldname.startswith('A_'):
            with open('./Auxillary Scripts/ActionFields.csv') as csv_file:
                csvread = csv.DictReader(csv_file)
                for row in csvread:
                    if row['FieldName'] == fieldname:
                        self.fieldname = fieldname
                        self.longname = row['LongName']
                        self.category = row['Category']
                        self.type = 'Action'
                        values = list(row.values())
                        choices = values[3:len(values)]
                        self.choices = list(filter(None, choices))     #Options that this field can be set to
                        
                        
        #Appropriately label Other field
        else:
             with open('./Auxillary Scripts/OtherFields.csv') as csv_file:
                csvread = csv.DictReader(csv_file)
                for row in csvread:
                    if row['FieldName'] == fieldname:
                        self.fieldname = fieldname
                        self.longname = row['LongName']
                        self.category = row['Category']
                        self.type = 'Other'
    

if str.__eq__(__name__, '__main__'):
    test = fieldnamelookup('gibberish')