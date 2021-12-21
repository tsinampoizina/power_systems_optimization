# !/usr/bin/python3
import os
import pandas as pd
from dataclasses import make_dataclass

location = {} 
county = {} 
# metadata_path = "/Volumes/WD-DATA-100/power_optimisation_system/metadata/wind_metadata/"
# path = "/Volumes/WD-DATA-100/power_optimisation_system/raw_data/data_wind/"
metadata_path = "/Volumes/WD-DATA-100/power_optimisation_system/metadata/solar_metadata/"
path = "/Volumes/WD-DATA-100/power_optimisation_system/raw_data/data_solar/"

Site = make_dataclass("Site", [("site", str), ("county", str), ("years", list), ("lat", float), ("lon", float)])
# Site = make_dataclass("Site", [("site", str), ("county", str), ("years", list)])

counties = [d for d in os.listdir(path) if os.path.isdir(path+'/'+d)]
counties.sort()
print(len(counties))

df = pd.DataFrame()
for county in counties:
    county_path = path + county
    county_sites = os.listdir(county_path)
    county_sites.sort() 
    dfs = []
    for site in county_sites:
        site_path = county_path+'/'+site
        metadata_file = metadata_path + county + '/' + site + '/' + "capability.csv"
        site_years = os.listdir(site_path)
        lat_lon = pd.read_csv(metadata_file)
        site_years = [int(year[0:4]) for year in site_years]
        site_years.sort() 
        # print(os.listdir(site_path)) 
        dfs.append(Site(site, county, site_years, lat_lon['lat'][0] , lat_lon['lon'][0]))
    df_county = pd.DataFrame(dfs)
    df = df.append(df_county)
    # for site in os.listdir(path_cty):
    #     print(os.listdir(path_cty + site + '/'))
    #     location[site] = (0, 0)
    #     county[site] = cty
print(df)
df.to_csv("locations.csv")

