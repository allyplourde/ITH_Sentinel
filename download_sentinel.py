#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_sentinel.py

Script to select Sentinel imagery from Copernicus and download

Dependencies:
    -Python3
    -sentinelsat
    -Account with Copernicus

"""

import os
import sys
import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from sentinelsat import SentinelAPI
from getpass import getpass

# connect to copernicus
user = input("Please enter your Coperniscus Username:\t")
password = getpass("Password: ")
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

# set working directory
wrkdir = "path/to/directory"  
os.chdir(wrkdir)

#ITH-South
####    ulx,  uly,  lrx,   lry
roi = [-133, 69.0, -133.9, 68.3]

# define the dates of imagery to fetch
startdate = pd.to_datetime("October 15, 2021")
days = 15
dates = startdate + pd.to_timedelta(np.arange(days), "D")

#convert spat to well known text (assumes bb is in ulx uly, lrx lry)
lon =[roi[0], roi[2], roi[2], roi[0]]
lat =[roi[1], roi[1], roi[3], roi[3]]
geom = Polygon(zip(lon, lat)) #create the polygon from calculated coordinates
footprint = geom.to_wkt()

# query, see link below for fields
# https://sentinelsat.readthedocs.io/en/master/api_overview.html#opensearch-example
products = api.query(footprint,
                     date = (dates[0].strftime('%Y%m%d'), dates[-1].strftime('%Y%m%d')),
                     platformname = 'Sentinel-1',
                     producttype = 'SLC',
                     sensoroperationalmode = 'IW',
                     orbitdirection = 'ASCENDING')


#Convert the results to a geopandas dataframe
gpdf = api.to_geodataframe(products)

print("The query returned {} hits".format(len(gpdf)))

ok = input("Would you like to export the query results (can be opened in QGIS) ?...\n  \
            Press 'y' to export results or any other key to continue: ")
if ok.upper() == "Y":
    # export the query results to a geopackage (can be opened in QGIS)
    gpdf.to_file('products_tile4.gpkg', layer='prod', driver="GPKG")

ok = input("Each image will take 5-10 minutes to produce... Press 'y' to continue or any other key to cancel: ")
if ok.upper() != "Y":
    print("Operation cancelled by user")
    sys.exit()
    
for i in range(len(gpdf)):

    print("Working on "+gpdf.title[i]+".......")
    
    #download the file
    #api.download(gpdf.uuid[i])
