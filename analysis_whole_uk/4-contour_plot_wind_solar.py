#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
import scipy.interpolate

import time
from tqdm import tqdm
import pdb

from pathlib import Path
from collections import namedtuple

from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
from cartopy.feature import ShapelyFeature, OCEAN, LAKES
import cartopy
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader as ShapeReader, natural_earth

field = 'solar'
clevs = np.arange(60, 820, 20, dtype=float)
field_color = 'black'

# field = 'wind'
# clevs = np.arange(0, 31, 1, dtype=float)
# field_color = 'purple'

shapefile = natural_earth(category='cultural',
                          resolution='10m',
                          name='admin_0_countries')
subdiv = ShapeReader('subdiv_uk.shp') 

# Sort the geometries in the shapefile into UK or other
country_geos = []
other_land_geos = []
for record in ShapeReader(shapefile).records():
    if record.attributes['ADMIN'] in ['United Kingdom']:
        country_geos.append(record.geometry)
    else:
        other_land_geos.append(record.geometry)

# Define map projection to allow Cartopy to transform ``lat`` and ``lon`` values accurately into points on the
# matplotlib plot canvas.
# projection = ccrs.PlateCarree()
projection = ccrs.OSGB()

# Define a Cartopy Feature for the country borders and the land mask (i.e.,
# all other land) from the shapefile geometries, so they can be easily plotted
countries = ShapelyFeature(country_geos,
                           crs=ccrs.PlateCarree(),
                           facecolor='none',
                           edgecolor='black',
                           lw=0.25)
land_mask = ShapelyFeature(other_land_geos,
                           crs=ccrs.PlateCarree(),
                           facecolor='white',
                           edgecolor='black',
                           lw=0.5)

# Download the Natural Earth shapefile for the states/provinces at 10m resolution
shapefile = natural_earth(category='cultural',
                          resolution='10m',
                          name='admin_1_states_provinces')

# Extract the UK province borders
province_geos = [
    record.geometry
    for record in ShapeReader(shapefile).records()
    if record.attributes['admin'] == 'United Kingdom'
]

province_geos = [
    record.geometry
    for record in subdiv.records()
]

# Define a Cartopy Feature for the province borders, so they can be easily plotted
provinces = ShapelyFeature(province_geos,
                           crs=ccrs.PlateCarree(),
                           facecolor='none',
                           edgecolor='black',
                           lw=0.2)



fig = plt.figure(figsize=(12,6)) 
quarter = ['','q1','q2','q3','q4'] 
title = ['','Jan-Feb-Mar','Apr-May-Jun','Jul-Aug-Sep','Oct-Nov-Dec'] 
for i in [1,2,3,4]: 
    climatology_data_file = field + '_climatology_' + quarter[i]  + '.csv'
    plot_file = field + '_climatology_' + quarter[i]  + '.png'
    ax  = plt.subplot(1,4,i,projection =projection)   
    ax.set_title(title[i])


    df_solar = pd.read_csv(climatology_data_file)
    df_solar['lon_lat'] = list(zip(df_solar.lon, df_solar.lat))
    print(df_solar['rad'].describe()) 


# Define the contour levels
    xi = np.arange(-9.1,2.1,0.1)  
    yi = np.arange(50,61,0.1)  
    X, Y = np.meshgrid(xi,yi)

    zi = scipy.interpolate.griddata(list(df_solar['lon_lat']), df_solar['rad'], (X, Y), method='cubic')
    # cf = ax.contourf(xi, yi, zi, 15, linewidths=0.5, transform=projection,cmap='jet',extend='both')
    cf = ax.contourf(xi, yi, zi, levels=clevs, transform=ccrs.PlateCarree(),cmap='jet',extend='both',zorder=1)
    # cf = ax.tricontourf(df_solar.lon, df_solar.lat, df_solar.rad, levels=clevs, transform=ccrs.PlateCarree(),cmap='jet',extend='both',zorder=1)

    cax = plt.axes((0.1, 0.08, 0.8, 0.02))
    cbar = plt.colorbar(cf,
                        ax=ax,
                        cax=cax,
                        ticks=clevs[1:-1:2],
                        drawedges=True,
                        orientation='horizontal')
    cbar.ax.tick_params(labelsize=12)


# Add the OCEAN and LAKES features on top of the contour plot
    ax.add_feature(OCEAN.with_scale('10m'), edgecolor='black', lw=0.5, zorder=2)
    ax.add_feature(LAKES.with_scale('10m'), edgecolor='black', lw=0.5, zorder=2)
    # ax.add_feature(cartopy.feature.STATES, linestyle='-',lw=0.25,edgecolor='black') 
    ax.add_feature(countries,zorder=3)
    ax.add_feature(provinces,zorder=3)

# Add the land mask feature on top of the contour plot (higher zorder)
    ax.add_feature(land_mask, zorder=3)

# ax.scatter(df_solar['lon'], df_solar['lat'], c=df_solar['rad'], transform=ccrs.PlateCarree())
    ax.scatter(df_solar['lon'], df_solar['lat'], c=field_color, s=2, transform=ccrs.PlateCarree(), zorder=4)


    ax.set_aspect('equal') 
plt.savefig(plot_file, bbox_inches='tight')
plt.show()