import pandas as pd
from bs4 import BeautifulSoup
import re
from glob import glob
from pathlib import Path
import intake
from importlib.resources import files
import os
import matplotlib.pyplot as plt
import requests
import fsspec
import xarray as xr
import numpy as np
import pooch

import cook_inlet_catalogs as cic


base_dir = files(cic)
distkey = "distance [km]"
simplecache_options = {"simplecache": {"cache_storage": cic.utils.cache_dir, "same_names": True}}

def ctd_profiles_2005_noaa(slug, simplecache):
    
    metadata = dict(project_name = "CTD profiles 2005 - NOAA",
        overall_desc = "CTD Profiles (NOAA): across Cook Inlet",
        time = "One-off CTD profiles in June and July 2005",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles from NOAA.""",
    )

    # new_cols = [col for col in cols if col not in ["mon/day/yr", "hh:mm"]]
    
    # make catalog
    
    # Each entry in the catalog is a single CTD from one of the two files.
    urls = ["https://researchworkspace.com/files/39886023/noaa_north.txt",
            "https://researchworkspace.com/files/39886022/noaa_south.txt"]

    # skipping bottom depth, sigma, press
    cols = ["Cruise", "Station", "Type", "mon/day/yr", "hh:mm", "Lon (°E)",	"Lat (°N)", 
            "Temperature [C]", "tran [v]", "fluor [v]", "Depth [m]",  "Salinity [psu]",]
    csv_kwargs = dict(encoding = "ISO-8859-1", sep="\t",
                    usecols=cols, dtype={"Station": str, 'mon/day/yr': str, 'hh:mm': str}
                    )
                    #   index_col=["date_time","Depth [m]"]
    
    cat = intake.entry.Catalog(metadata=metadata)

    dataset_ids = []
    all_readers = []
    for url in urls:
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
            
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})

        new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
        reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])
        all_readers.append(reader_dates_parsed)

        # split into single CTD cast units by station
        df = reader_dates_parsed.read()
        hover_cols = cic.utils.get_hover_cols(df)
        stations = sorted(df.cf["station"].unique())

        for station in stations:
            ddf = cic.utils.select_station(df, station)

            # select transect/date to get metadata
            reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
            # title = f"{station} {ddf.cf['T'].iloc[0]} {ddf.cf['longitude'].iloc[0]} {ddf.cf['latitude'].iloc[0]}"
            reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
            reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
            dataset_ids.append(station)
            cat[station] = reader1station
            cat.aliases[station] = station

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_usgs_boem(slug, simplecache):
    metadata = dict(project_name = "CTD profiles - USGS BOEM",
        overall_desc = "CTD Profiles (USGS BOEM): across Cook Inlet",
        time = "One-off CTD profiles from 2016 to 2021 in July",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = ["2016", "2017", "2018", "2019", "2021"],
        map_description = "CTD Profiles",
        summary = """USGS Cook Inlet fish and bird survey CTD profiles.
        
CTD profiles collected in Cook Inlet from 2016-2021 by Mayumi Arimitsu as part of BOEM sponsored research on fish and bird distributions in Cook Inlet. The profiles are collected in July for the years 2016-2021.

The scientific project is described here: https://www.usgs.gov/centers/alaska-science-center/science/cook-inlet-seabird-and-forage-fish-study#overview.
"""
    )
    
    # make catalog
    url = "https://researchworkspace.com/files/42202136/Arimitsu_CookInlet_CTD.csv"
    usecols = ['date_time', 'station_number', 'location', 'ctd_latitude',
       'ctd_longitude', 'pressure', 'temp', 'C0Sm', 'DzdtM', 'Par',
       'Sbeox0MgL', 'Sbeox0PS', 'SvCM', 'CStarAt0', 'CStarTr0', 'salt',
       'FlECOAFL', 'TurbWETntu0', 'Ph', 'OxsatMgL'
       ]
    csv_kwargs = dict(parse_dates=[0], usecols=usecols, na_values=["-999"], dtype={"station_number": str})
    # csv_kwargs = dict(parse_dates=[0], index_col=["date_time","pressure"], usecols=usecols)


    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)

    # split into single CTD cast units by station
    df = initial_reader.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = initial_reader.apply(cic.utils.select_station, station)
        # title = f"{station} {ddf.cf['T'].iloc[0]} {ddf.cf['longitude'].iloc[0]} {ddf.cf['latitude'].iloc[0]}"
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    




def ctd_profiles_ecofoci(slug, simplecache):
    metadata = dict(project_name = "CTD profiles - EcoFOCI",
        overall_desc = "CTD Profiles (EcoFOCI): Shelikof Strait",
        time = "CTD profiles from 1981 to 2012",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Casts taken as part of the EcoFOCI project.

EcoFOCI project page: https://www.ecofoci.noaa.gov/

Area data page: https://data.pmel.noaa.gov/pmel/erddap/tabledap/Shelikof_line8_3695_0ada_d066.html

PMEL ERDDAP: https://data.pmel.noaa.gov/pmel/erddap/index.html

Map of related project work: https://www.pmel.noaa.gov/foci/foci_moorings/foci_moormap2.shtml

Image here: https://www.pmel.noaa.gov/foci/foci_moorings/images/gulf_of_alaska_mooring_map.png

"""
    )
    
    # make catalog
    url = "https://data.pmel.noaa.gov/pmel/erddap/tabledap/Shelikof_line8_3695_0ada_d066.csvp?id%2Ccast%2Ccruise%2Ctime%2Clongitude%2Clatitude%2Cdepth%2Cocean_temperature_1%2Cocean_practical_salinity_1&time%3E=1981-03-31T19%3A51%3A00Z%09&time%3C=2012-04-27T16%3A16%3A00Z"
    # usecols = ['date_time', 'station_number', 'location', 'ctd_latitude',
    #    'ctd_longitude', 'pressure', 'temp', 'C0Sm', 'DzdtM', 'Par',
    #    'Sbeox0MgL', 'Sbeox0PS', 'SvCM', 'CStarAt0', 'CStarTr0', 'salt',
    #    'FlECOAFL', 'TurbWETntu0', 'Ph', 'OxsatMgL'
    #    ]
    csv_kwargs = dict()
    # csv_kwargs = dict(parse_dates=[0], usecols=usecols, na_values=["-999"], dtype={"station_number": str})
    # csv_kwargs = dict(parse_dates=[0], index_col=["date_time","pressure"], usecols=usecols)


    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)

    # split into single CTD cast units by station
    df = initial_reader.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = initial_reader.apply(cic.utils.select_station, station)
        # title = f"{station} {ddf.cf['T'].iloc[0]} {ddf.cf['longitude'].iloc[0]} {ddf.cf['latitude'].iloc[0]}"
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_piatt_speckman_1999(slug, simplecache):
    metadata = dict(project_name = "Piatt Speckman 1995-99",
        overall_desc = "CTD Profiles (Piatt Speckman)",
        time = "One-off CTD profiles April to September 1999",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )

    url = "https://researchworkspace.com/files/42400652/Piatt1999.csv"
    names = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon', 'Lat', 'Bot. Depth',
        'Depth [m]', 'Temperature [C]', 'Salinity [psu]', 'Sigma',
        'Backscatter', 'CHL', 'empty']
    usecols = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon', 'Lat', 'Bot. Depth',
        'Depth [m]', 'Temperature [C]', 'Salinity [psu]', 'Backscatter', 'CHL']
    csv_kwargs = dict(encoding = 'unicode_escape', names=names, header=0, usecols=usecols,
                      dtype={"Station": str, 'mon/day/yr': str, 'hh:mm': str})
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])

    # split into single CTD cast units by station
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
        reader1station.metadata =  {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_kbay_osu_2007(slug, simplecache):
    metadata = dict(project_name = "Kbay OSU 2007",
        overall_desc = "CTD Profiles (Kbay OSU 2007)",
        time = "One-off CTD profiles September 2007",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )

    url = "https://researchworkspace.com/files/39888023/kbay_odv.txt"
    names = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Pressure [dB]', 'Temperature [C]',
       'Conductivity', 'Chlorophyll', 'Turbidity', 'Oxygen [%]', 'Par',
       'Depth', 'Salinity [PSU]', 'Sigma-theta', 'Decent Rate']
    usecols = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Temperature [C]',
       'Conductivity', 'Chlorophyll', 'Turbidity', 'Oxygen [%]', 'Par',
       'Depth', 'Salinity [PSU]', 'Decent Rate']
    csv_kwargs = dict(encoding = 'unicode_escape', sep="\t",
                      dtype={"Station": str, 'mon/day/yr': str, 'hh:mm': str},
                    #   parse_dates={"date_time": ["mon/day/yr","hh:mm"]}, 
                      header=0, names=names, usecols=usecols)
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options

    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])

    # split into single CTD cast units by station
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
        reader1station.metadata =  {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_kb_small_mesh_2006(slug, simplecache):
    metadata = dict(project_name = "KB small mesh 2006",
        overall_desc = "CTD Profiles (KB small mesh 2006)",
        time = "One-off CTD profiles May 2006",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )

    url = "https://researchworkspace.com/files/42200009/KBsmallmesh.csv"
    names = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Press', 'Temperature [C]', 'fluor [v]',
       'tran [v]', 'sbeoxv', 'PAR', 'Depth [m]', 'Salinity [psu]', 'Sigma',
       'oxconc', 'oxper [%]']
    usecols = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Temperature [C]', 'fluor [v]',
       'tran [v]', 'sbeoxv', 'PAR', 'Depth [m]', 'Salinity [psu]', 
       'oxconc', 'oxper [%]']
    csv_kwargs = dict(encoding = 'unicode_escape',
                      dtype={"Station": str, 'mon/day/yr': str, 'hh:mm': str},
                    #   parse_dates={"date_time": ["mon/day/yr","hh:mm"]}, 
                    #   index_col=["date_time", "Depth [m]"],
                      header=0, names=names, usecols=usecols)
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options

    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])

    # split into single CTD cast units by station
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_kachemack_kuletz_2005_2007(slug, simplecache):
    metadata = dict(project_name = "Kachemak Kuletz 2005-2007",
        overall_desc = "CTD Profiles (Kachemak Kuletz 2005-2007)",
        time = "One-off CTD profiles June-July 2005 and July 2006 and 2007",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )
    
    url = "https://researchworkspace.com/files/42403574/Kuletz.csv"

    csv_kwargs = dict(parse_dates=["date_time"], dtype={"Station": str}
                    #   index_col=["date_time", "Depth [m]"],
                      )
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)

    # split into single CTD cast units by station
    df = initial_reader.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        ddf = cic.utils.select_station(df, station)
        # select transect/date to get metadata
        reader1station = initial_reader.apply(cic.utils.select_station, station)
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_emap_2002(slug, simplecache):
    metadata = dict(project_name = "CTD profiles - EMAP 2002",
        overall_desc = "CTD Profiles (EMAP 2002)",
        time = "One-off CTD profiles June to August 2002",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )

    url = "https://researchworkspace.com/files/42199527/emap.csv"
    names = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Depth [m]', 'Press', 'Temperature [C]',
       'Salinity [psu]', 'Sigma', 'O2sat [%]', 'obs [ntu]', 'tobs [ntu]',
       'chl [mg/m3]']
    usecols = ['Cruise', 'Station', 'Type', 'mon/day/yr', 'hh:mm', 'Lon',
       'Lat', 'Bot. Depth [m]', 'Depth [m]', 'Temperature [C]',
       'Salinity [psu]', 'O2sat [%]', 'obs [ntu]', 'tobs [ntu]',
       'chl [mg/m3]']
    csv_kwargs = dict(encoding = 'unicode_escape',
                    #   parse_dates={"date_time": ["mon/day/yr","hh:mm"]}, 
                    #   index_col=["date_time", "Depth [m]"],
                    dtype={"Station": str, 'mon/day/yr': str, 'hh:mm': str},
                      header=0, names=names, usecols=usecols)
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options

    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])

    # split into single CTD cast units by station
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    # these are outside the model domain
    stations_to_remove = [32, 34, 35, 36, 38, 40, 41, 45, 46, 
                          50, 51, 53, 54, 55, 56, 58, 59,
                          60, 61, 62, 63, 64,
                          70,71,72,73,74,75]
    stations = list(set(stations) - set(stations_to_remove))

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        # select transect/date to get metadata
        ddf = cic.utils.select_station(df, station)
        reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_profiles_emap_2008(slug, simplecache):
    metadata = dict(project_name = "CTD profiles - EMAP 2008",
        overall_desc = "CTD Profiles (EMAP 2008)",
        time = "One-off CTD profiles August to October 2008",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "profile",
        header_names = None,
        map_description = "CTD Profiles",
        summary = """CTD Profiles in Cook Inlet""",
    )

    url = "https://researchworkspace.com/files/42199537/Cook_EMAP_CTD-data_08.csv"
    usecols = ['StationID', 'Lat', 'Lon', 'Temperature', 'Date', 'Time',"Depth (m)",
       'Salinity (PSU)', 'Oxygen (mg/L)']
    csv_kwargs = dict(dtype={"StationID": str, "Date": str, "Time": str},
                # parse_dates={"date_time": ["Date","Time"]}, 
                    #   index_col=["date_time","Depth (m)"],
                      usecols=usecols)
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    # df = pd.read_csv(url, **csv_kwargs)    
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.rename(columns={"Date": "date", "Time": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])

    # split into single CTD cast units by station
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    stations = sorted(df.cf["station"].unique())

    cat = intake.entry.Catalog(metadata=metadata)
    for station in stations:
        # select transect/date to get metadata
        ddf = cic.utils.select_station(df, station)
        reader1station = reader_dates_parsed.apply(cic.utils.select_station, station)
        reader1station.metadata = {"plots": {"data": cic.utils.line_depth_dict(df.cf["Z"].name, [df.cf["temp"].name, df.cf["salt"].name], hover_cols=hover_cols)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        cat[station] = reader1station
        cat.aliases[station] = station
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_towed_otf_kbnerr(slug, simplecache):
    metadata = dict(project_name = "CTD Towed 2003 - OTF KBNERR",
        overall_desc = "Towed CTD (OTF KBNERR): central Cook Inlet",
        time = "July 2003, 5min sampling frequency",
        included = True,
        notes = "Two files that were about 30 minutes long were not included (mic071203 and mic072803_4-5). These data were not included in the NWGOA model/data comparison. Resampled from 5sec to 5min sampling frequency.",
        maptype = "box",
        featuretype = "trajectoryProfile",
        header_names = None,
        map_description = "Towed CTD Profiles",
        summary = """Towed CTD Profiles.

Short, high resolution towed CTD in the middle of Cook Inlet at nominal 4 and 10m depths
"""
    )

    urls = ["https://researchworkspace.com/files/42202371/mic071303_subsampled.csv",
            "https://researchworkspace.com/files/42202372/mic071903_subsampled.csv",
            "https://researchworkspace.com/files/42202373/mic072003_subsampled.csv",
            "https://researchworkspace.com/files/42202374/mic072103_subsampled.csv",
            "https://researchworkspace.com/files/42202375/mic072203_subsampled.csv",
            "https://researchworkspace.com/files/42202376/mic072403_subsampled.csv",
            "https://researchworkspace.com/files/42202377/mic072503_subsampled.csv",
            "https://researchworkspace.com/files/42202378/mic072603_subsampled.csv",
            "https://researchworkspace.com/files/42202379/mic072803_65-8_subsampled.csv",
            "https://researchworkspace.com/files/42202380/mic072903_subsampled.csv",
            "https://researchworkspace.com/files/42202381/mic073003_subsampled.csv",]
    csv_kwargs = dict(parse_dates=[0])

    cat = intake.entry.Catalog(metadata=metadata)

    for url in urls:
        name = Path(url).stem
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options

        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        initial_reader = initial_reader.assign(station=name)
        df = initial_reader.read()
        hover_cols = cic.utils.get_hover_cols(df, distance=True)
        title = str(df.cf["T"].iloc[0])
        plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, title=title, hover_cols=hover_cols)
        
        initial_reader.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                            "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs),
                            "map": cic.utils.map_dict(df.cf["longitude"].name, df.cf["latitude"].name),}}
        initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))

        cat[name] = initial_reader
        cat.aliases[name] = name
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_towed_ferry_noaa_pmel(slug, simplecache):
    metadata = dict(project_name = "CTD Towed 2004-2008 Ferry in-line - NOAA PMEL",
        overall_desc = "Underway CTD (NOAA PMEL): Towed on ferry",
        time = "Continuous 2004 to 2008, 5min sampling frequency",
        included = True,
        notes = "The ferry regularly traveled outside of the domain of interest and those times are not included. Data was resampled from 30s to 5min sampling frequency.",
        maptype = "box",
        featuretype = "trajectory",
        map_description = "Towed CTD Paths",
        summary = """
An oceanographic monitoring system aboard the Alaska Marine Highway System ferry Tustumena operated for four years in the Alaska Coastal Current (ACC) with funding from the Exxon Valdez Oil Spill Trustee Council's Gulf Ecosystem Monitoring Program, the North Pacific Research Board and the National Oceanic and Atmospheric Administration. An electronic public display aboard the ferry educated passengers about the local oceanography and mapped the ferry's progress. Sampling water at 4 m, the underway system measured: (1) temperature and salinity (used in the present report), and (2) nitrate,
(3) chlorophyll fluorescence, (4) colored dissolved organic matter fluorescence, and (5) optical beam transmittance (not used in report).

Nominal 4 meter depth.

NORTH PACIFIC RESEARCH BOARD PROJECT FINAL REPORT
Alaskan Ferry Oceanographic Monitoring in the Gulf of Alaska
NPRB Project 707 Final Report
Edward D. Cokelet and Calvin W. Mordy.
https://www.nodc.noaa.gov/archive/arc0031/0070122/1.1/data/0-data/Final_Report_NPRB_0707.pdf

Exxon Valdez Oil Spill Gulf Ecosystem
Monitoring and Research Project Final Report
Biophysical Observations Aboard Alaska Marine Highway System Ferries
Gulf Ecosystem Monitoring and Research Project 040699
Final Report
Edward D. Cokelet, Calvin W. Mordy, Antonio J. Jenkins, W. Scott Pegau
https://www.nodc.noaa.gov/archive/arc0031/0070122/1.1/data/0-data/Final_Report_GEM_040699.pdf

Archive: https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.nodc%3A0070122/html

![pic](https://www.nodc.noaa.gov/archive/arc0031/0070122/1.1/about/0070122_map.jpg)
"""
    )
    
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    years = ["2004", "2005", "2006", "2007", "2008"]
    url = "https://researchworkspace.com/files/42202265/Tustumena_t_s_chl_cdom_tr_final_data_subsetted.nc"
    cat = intake.entry.Catalog(metadata=metadata)
    if simplecache:
        url = f"simplecache://::{url}"
        data = intake.readers.datatypes.HDF5(url, simplecache_options)
    else:
        data = intake.readers.datatypes.HDF5(url)
    # data = intake.readers.datatypes.HDF5(url)
    # data = intake.readers.datatypes.NetCDF3(url)
    initial_reader = data.to_reader("xarray:Dataset", chunks={})
    with fsspec.open(url) as f:
        ds = xr.open_dataset(f)

        lonkey, latkey = ds.cf["longitude"].name, ds.cf["latitude"].name
        hover_cols = cic.utils.get_hover_cols(ds, distance=False)
        plot_kwargs = {"x": lonkey, "y": latkey, "flip_yaxis": True, "hover_cols": hover_cols}
        for year in years:
            for month in months:
                # not all month-years present in data
                if cic.utils.select_ds_year_month(ds, year, month)["T_30_EQ_AX"].size == 0:
                    continue

                # select dataset for year-month
                reader1station = initial_reader.apply(cic.utils.select_ds_year_month, year, month)

                name = f"{year}-{month}"
                reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(ds.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                                    "temp": cic.utils.scatter_dict(ds.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs),}}
                reader1station.metadata.update(cic.utils.add_metadata(cic.utils.select_ds_year_month(ds, year, month), metadata["maptype"], metadata["featuretype"], url))
                cat[name] = reader1station
                cat.aliases[name] = name
        # cat["all"] = initial_reader
        # When "all" is available, get overall metadata directly
        overall_metadata = {"maxLatitude": float(ds.cf["latitude"].max()), "maxLongitude": float(ds.cf["longitude"].max()),
                            "minLatitude": float(ds.cf["latitude"].min()), "minLongitude": float(ds.cf["longitude"].min()),
                            "maxTime": ds.cf["T"].max().dt.strftime('%Y-%m-%d %H:%M').item(), 
                            "minTime": ds.cf["T"].min().dt.strftime('%Y-%m-%d %H:%M').item(), 
                            "key_variables": [ds.cf["temp"].name, ds.cf["salt"].name]}
        cat.metadata.update(overall_metadata)
        # set up plotting overall map, which uses general key names 
        cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
        cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
        cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_towed_gwa(slug, simplecache):
    metadata = dict(project_name = "CTD Towed 2017-2019 - GWA",
        overall_desc = "Underway CTD (GWA): Towed CTD",
        time = "Approximately monthly in summer from 2017 to 2020, 5min sampling frequency",
        included = True,
        notes = "Made all longitudes negative west values, converted some local times, 2019 and 2020 only have temperature, ship track outside domain is not included, resampled from 2min to 5min.",
        maptype = "box",
        featuretype = "trajectory",
        header_names = ["2017", "2018", "2019", "2020"],
        map_description = "Flow through on Ship of Opportunity",
        summary = f"""Environmental Drivers: Continuous Plankton Recorders, Gulf Watch Alaska

This project is a component of the integrated Long-term Monitoring of Marine Conditions and Injured Resources and Services submitted by McCammon et. al. Many important species, including herring, forage outside of Prince William Sound for at least some of their life history (salmon, birds and marine mammals for example) so an understanding of the productivity of these shelf and offshore areas is important to understanding and predicting fluctuations in resource abundance. The Continuous Plankton Recorder (CPR) has sampled a continuous transect extending from the inner part of Cook Inlet, onto the open continental shelf and across the shelf break into the open Gulf of Alaska monthly through spring and summer since 2004. There are also data from 2000-2003 from a previous transect. The current transect intersects with the outer part of the Seward Line and provides complementary large scale data to compare with the more local, finer scale plankton sampling on the shelf and in PWS. Resulting data will enable us to identify where the incidences of high or low plankton are, which components of the community are influenced, and whether the whole region is responding in a similar way to meteorological variability. Evidence from CPR sampling over the past decade suggests that the regions are not synchronous in their response to ocean climate forcing. The data can also be used to try to explain how the interannual variation in ocean food sources creates interannual variability in PWS zooplankton, and when changes in ocean zooplankton are to be seen inside PWS. The CPR survey is a cost-effective, ship-of-opportunity based sampling program supported in the past by the EVOS TC that includes local involvement and has a proven track record.

Nominal 7m depth, 2017-2020. 2017 and 2018 have salinity and temperature, 2019 and 2020 have only temperature.

Project overview: https://gulf-of-alaska.portal.aoos.org/#metadata/87f56b09-2c7d-4373-944e-94de748b6d4b/project
"""
    )
    
    urls = ["https://researchworkspace.com/files/42202335/CPR_physical_data_2017_subsetted.csv",
            "https://researchworkspace.com/files/42202337/CPR_physical_data_2018_subsetted.csv",
            "https://researchworkspace.com/files/42202339/CPR_physical_data_2019_subsetted.csv",
            "https://researchworkspace.com/files/42202341/CPR_physical_data_2020_subsetted.csv",
            ]

    csv_kwargs = dict(parse_dates=[0])
    cat = intake.entry.Catalog(metadata=metadata)
    for url in urls:
        year = Path(url).stem.split("_")[-2]
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        df = pd.read_csv(url, **csv_kwargs)
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        # loop over months
        for month in sorted(set(df.cf["T"].dt.month)):
            # select month as station
            reader1station = initial_reader.apply(cic.utils.select_df_month, month)
            reader1station = reader1station.apply(cic.utils.calculate_distance)
            ddf = cic.utils.select_df_month(df, month)
            hover_cols = cic.utils.get_hover_cols(ddf, distance=False)
            name = f"{str(ddf.cf['T'].dt.date[0])}"
            lonkey, latkey = df.cf["longitude"].name, df.cf["latitude"].name
            plot_kwargs = dict(x=lonkey, y=latkey, flip_yaxis=False, title=name, hover_cols=hover_cols)

            reader1station.metadata = {"plots": {"temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
            reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
            if int(year) in [2017,2018]:
                hover_cols = cic.utils.get_hover_cols(ddf, distance=False)
                plot_kwargs["hover_cols"] = hover_cols
                reader1station.metadata["plots"].update({"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),})
                reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))

            cat[name] = reader1station
            cat.aliases[name] = name
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_towed_gwa_temp(slug, simplecache):
    metadata = dict(project_name = "Temperature towed 2011-2016 - GWA",
                    overall_desc = "Underway CTD (GWA): Towed, temperature only",
                    time = "Approximately monthly in summer from 2011 to 2016, 5min sampling frequency",
                    included = True,
                    notes = "Converted some local times, ship track outside domain is not included.",
                    maptype = "box",
                    featuretype = "trajectory",
                    header_names = ["2011", "2012", "2013", "2014", "2015", "2016"],
                    map_description = "Flow through on Ship of Opportunity",
                    summary = f"""Temperature only: Environmental Drivers: Continuous Plankton Recorders, Gulf Watch Alaska.

This project is a component of the integrated Long-term Monitoring of Marine Conditions and Injured Resources and Services submitted by McCammon et. al. Many important species, including herring, forage outside of Prince William Sound for at least some of their life history (salmon, birds and marine mammals for example) so an understanding of the productivity of these shelf and offshore areas is important to understanding and predicting fluctuations in resource abundance. The Continuous Plankton Recorder (CPR) has sampled a continuous transect extending from the inner part of Cook Inlet, onto the open continental shelf and across the shelf break into the open Gulf of Alaska monthly through spring and summer since 2004. There are also data from 2000-2003 from a previous transect. The current transect intersects with the outer part of the Seward Line and provides complementary large scale data to compare with the more local, finer scale plankton sampling on the shelf and in PWS. Resulting data will enable us to identify where the incidences of high or low plankton are, which components of the community are influenced, and whether the whole region is responding in a similar way to meteorological variability. Evidence from CPR sampling over the past decade suggests that the regions are not synchronous in their response to ocean climate forcing. The data can also be used to try to explain how the interannual variation in ocean food sources creates interannual variability in PWS zooplankton, and when changes in ocean zooplankton are to be seen inside PWS. The CPR survey is a cost-effective, ship-of-opportunity based sampling program supported in the past by the EVOS TC that includes local involvement and has a proven track record.

Nominal 7m depth, 2011-2016.

Project overview: https://gulf-of-alaska.portal.aoos.org/#metadata/87f56b09-2c7d-4373-944e-94de748b6d4b/project
"""
    )
    
    urls = ["https://researchworkspace.com/files/42202616/CPR_TemperatureData_2011_subsetted.csv",
            "https://researchworkspace.com/files/42202618/CPR_TemperatureData_2012_subsetted.csv",
            "https://researchworkspace.com/files/42202620/CPR_TemperatureData_2013_subsetted.csv",
            "https://researchworkspace.com/files/42202622/CPR_TemperatureData_2014_subsetted.csv",
            "https://researchworkspace.com/files/42202624/CPR_TemperatureData_2015_subsetted.csv",
            "https://researchworkspace.com/files/42202626/CPR_TemperatureData_2016_subsetted.csv",]
    csv_kwargs = dict(parse_dates=[0])

    cat = intake.entry.Catalog(metadata=metadata)
    for url in urls:
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        df = pd.read_csv(url, **csv_kwargs)
        hover_cols = cic.utils.get_hover_cols(df, distance=False)
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        for month in sorted(set(df.cf["T"].dt.month)):
            # select month as station
            reader1station = initial_reader.apply(cic.utils.select_df_month, month)
            reader1station = reader1station.apply(cic.utils.calculate_distance)
            ddf = cic.utils.select_df_month(df, month)
            name = f"{str(ddf.cf['T'].dt.date[0])}"
            plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, flip_yaxis=False, title=name, hover_cols=hover_cols)
            reader1station.metadata = {"plots": {"temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
            reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
            cat[name] = reader1station
            cat.aliases[name] = name
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_transects_barabara_to_bluff_2002_2003(slug, simplecache):
    metadata = dict(project_name = "Barabara to Bluff 2002-2003",
        overall_desc = "CTD transects: Barabara to Bluff",
        time = "2002-2003",
        included = True,
        notes = "",
        maptype = "line",
        featuretype = "trajectoryProfile",
        header_names = None,
        map_description = "CTD Transects",
        summary = f"""Repeat CTD transect from Barabara to Bluff Point in Cook Inlet from 2002 to 2003.
"""
    )

    url = "https://researchworkspace.com/files/42396691/barabara.csv"
    csv_kwargs = dict(parse_dates=["date_time"])#, index_col="date_time") 
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    df = pd.read_csv(url, **csv_kwargs)
    df = cic.utils.calculate_distance(df)  
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    hover_cols = cic.utils.get_hover_cols(df, distance=True)

    # each file is a transect so this is easier than usual for transects
    cat = intake.entry.Catalog(metadata=metadata)
    for cruise in np.arange(1,12):
        # df[df["Cruise"] == f"Cruise {cruise}"]
        cruise = str(cruise)  # this is necessary for yaml conversion
        name = f"Cruise {cruise}"
        ddf = cic.utils.select_df_by_column(df, "Cruise", name)

        # select month as station
        reader1station = initial_reader.apply(cic.utils.select_df_by_column, "Cruise", name)
        reader1station = reader1station.apply(cic.utils.calculate_distance)
        title = f"{name}: {str(ddf.cf['T'].iloc[0])}"
        plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, title=title, hover_cols=hover_cols)

        reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                            "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))

        cat[name] = reader1station
        cat.aliases[name] = name
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")    


def ctd_transects_cmi_kbnerr(slug, simplecache):
    metadata = dict(project_name = "CTD Transects 2004-2006 - CMI KBNERR",
        overall_desc = "CTD Transects, Moored CTD (CMI KBNERR): Six repeat, one single transect, one moored CTD",
        time = "From 2004 to 2006",
        included = True,
        notes = "Used in the NWGOA model/data comparison.",
        maptype = "line",
        header_names = ["Cruise_00", "Cruise_01", "Cruise_02", "Cruise_03", "Cruise_05", "Cruise_06", "Cruise_07",
                        "Cruise_08", "Cruise_09", "Cruise_10", "Cruise_11", "Cruise_12", "Cruise_13", "Cruise_14", "Cruise_15", "Cruise_16", "Kbay_timeseries", "sue_shelikof"],
        map_description = "CTD Transects",
        summary = f"""Seasonality of Boundary Conditions for Cook Inlet, Alaska

During 2004 to 2006 we collected hydrographic measurements along transect lines crossing: 1) Kennedy Entrance and Stevenson Entrance from Port Chatham to Shuyak Island; 2) Shelikof Strait from Shuyak Island to Cape Douglas; 3) Cook Inlet from Red River to Anchor Point; 4) Kachemak Bay from Barbara Point to Bluff Point, and 5) the Forelands from East Foreland to West Foreland. During the third year we added two additional lines; 6) Cape Douglas to Cape Adams, and 7) Magnet Rock to Mount Augustine. The sampling in 2006 focused on the differences in properties during the spring and neap tide periods.

CTD profiles 2004-2005 - CMI UAF seems to be transect 5 of this project.

Part of the project:
Seasonality of Boundary Conditions for Cook Inlet, Alaska
Steve Okkonen Principal Investigator
Co-principal Investigators: Scott Pegau Susan Saupe
Final Report
OCS Study MMS 2009-041
August 2009
Report: https://researchworkspace.com/files/39885971/2009_041.pdf

<img src="https://user-images.githubusercontent.com/3487237/233167915-c0b2b0e1-151e-4cef-a647-e6311345dbf9.jpg" alt="alt text" width="300"/>
"""
    )
    
    urls = ["https://researchworkspace.com/files/42202067/cmi_full_v2.csv",
            "https://researchworkspace.com/files/39886046/Kbay_timeseries.txt",
            "https://researchworkspace.com/files/39886061/sue_shelikof.txt",
            ]

    csv_kwargs = []
    csv_kwargs.append(dict(parse_dates=[0]))
    csv_kwargs.append(dict(encoding = "ISO-8859-1", sep="\t", dtype={"mon/day/yr": str,"hh:mm": str}))#, parse_dates={"date_time": ["mon/day/yr","hh:mm [utc]"]}))
    csv_kwargs.append(dict(encoding = "ISO-8859-1", sep="\t", dtype={"mon/day/yr": str,"hh:mm": str}))#, parse_dates={"date_time": ["mon/day/yr","hh:mm"]}))

    cat = intake.entry.Catalog(metadata=metadata)

    # sue_shelikof
    name, ind = "sue_shelikof", 2
    featuretype = "trajectoryProfile"
    # process_function = "ctd_transects_cmi_kbnerr_sue_shelikof"
    # df = pd.read_csv(urls[ind], **csv_kwargs[ind])

    if simplecache:
        urls[ind] = f"simplecache://::{urls[ind]}"
        csv_kwargs[ind]["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(urls[ind])
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs[ind])
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])
    reader_dates_parsed = reader_dates_parsed.apply(cic.utils.calculate_distance)
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df, distance=True)
    plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols)

    reader_dates_parsed.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                        "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
    reader_dates_parsed.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], featuretype, urls[ind]))

    cat[name] = reader_dates_parsed
    cat.aliases[name] = name


    # Kbay_timeseries
    name, ind = "Kbay_timeseries", 1
    featuretype = "trajectoryProfile"
    # df = pd.read_csv(urls[ind], **csv_kwargs[ind])
    if simplecache:
        urls[ind] = f"simplecache://::{urls[ind]}"
        csv_kwargs[ind]["storage_options"] = simplecache_options
    data = intake.readers.datatypes.CSV(urls[ind])
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs[ind])
    initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm [utc]": "time"})
    new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])
    reader_dates_parsed = reader_dates_parsed.apply(cic.utils.calculate_distance)
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df)
    plot_kwargs = dict(x=df.cf["T"].name, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols)

    reader_dates_parsed.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                        "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
    reader_dates_parsed.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], featuretype, urls[ind]))

    cat[name] = reader_dates_parsed
    cat.aliases[name] = name

    
    # cmi_full_v2
    name, ind = "cmi_full_v2", 0
    featuretype = "trajectoryProfile"
    cruises = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    lines = [1,2,3,4,6,7]
    if simplecache:
        urls[ind] = f"simplecache://::{urls[ind]}"
        csv_kwargs[ind]["storage_options"] = simplecache_options
    df = pd.read_csv(urls[ind], **csv_kwargs[ind])
    hover_cols = cic.utils.get_hover_cols(df, distance=True)

    data = intake.readers.datatypes.CSV(urls[ind])
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs[ind])
    
    for cruise in cruises:
        for line in lines:
            name_line = f"Cruise_{str(cruise).zfill(2)}-Line_{line}"
            reader_station = initial_reader.apply(cic.utils.select_df_cruise_line, cruise, line)
            reader_station = reader_station.apply(cic.utils.calculate_distance)
            ddf = cic.utils.select_df_cruise_line(df, cruise, line)
            # some cruise-line combinations don't exist
            if len(ddf.dropna())==0:
                continue
            title = f"Cruise {str(cruise)}, Line {line} ({str(ddf.cf['T'].dt.date.iloc[0])})"
            plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols, title=title)
            reader_station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                                "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
            reader_station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], featuretype, urls[ind]))
            
            cat[name_line] = reader_station
            cat.aliases[name_line] = name_line
    
    
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def ctd_transects_cmi_uaf(slug, simplecache):
    metadata = dict(project_name = "CTD profiles 2004-2005 - CMI UAF",
        overall_desc = "CTD Transect (CMI UAF): from East Foreland Lighthouse",
        time = "10 cruises, approximately monthly for summer months, in 2004 and 2005",
        included = True,
        notes = "Used in the NWGOA model/data comparison.",
        maptype = "line",
        featuretype = "trajectoryProfile",
        header_names = None,
        map_description = "CTD Transects",
        summary = """Seasonality of Boundary Conditions for Cook Inlet, Alaska: Transect (3) at East Foreland Lighthouse.

9 CTD profiles at stations across 10 cruises in (approximately) the same locations. Approximately monthly for summer months, 2004 and 2005.

Part of the project:
Seasonality of Boundary Conditions for Cook Inlet, Alaska
Steve Okkonen Principal Investigator
Co-principal Investigators: Scott Pegau Susan Saupe
Final Report
OCS Study MMS 2009-041
August 2009
Report: https://researchworkspace.com/files/39885971/2009_041.pdf
"""
    )
    
    url = "https://researchworkspace.com/files/39886038/all_forelands_ctd.txt"
    cols = ["Cruise", "Station", "Month", "Day", "Year", "Hour", "Minute", "Longitude", "Latitude", 
            "Depth [m]", "Temperature",	"Salinity", "flag"]
    csv_kwargs = dict(sep="\t", usecols=cols, dtype={"Month": "str", "Year": "str", "Day": "str", "Hour": "str", "Minute": "str"})
    # df = pd.read_csv(url, **csv_kwargs)
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options

    cat = intake.entry.Catalog(metadata=metadata)

    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    new_dates_column = initial_reader.apply(cic.utils.parse_year_month_day_hour_minute)
    reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=["Month","Day","Year","Hour","Minute"])
    df = reader_dates_parsed.read()
    hover_cols = cic.utils.get_hover_cols(df, distance=True)
            
    # we can just know this
    cruises = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for cruise in cruises:

        # select cruise to get metadata
        ddf = cic.utils.select_df_by_column(df, "Cruise", cruise)
        ddf = cic.utils.calculate_distance(ddf)
        # ddf = cic.utils.select_df_by_column(df.copy(), "Cruise", cruise)
        name = f"Cruise-{str(cruise).zfill(2)}"
        reader1station = reader_dates_parsed.apply(cic.utils.select_df_by_column, "Cruise", cruise)
        reader1station = reader1station.apply(cic.utils.calculate_distance)

        title = f"{str(ddf.cf['T'].iloc[0].date())}"

        plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols, title=title)
        reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                            "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        
        cat[name] = reader1station
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def ctd_transects_gwa(slug, simplecache):
    metadata = dict(project_name = "CTD profiles 2012-2021 - GWA",
                    overall_desc = "CTD Transects (GWA): Six repeat transects in Cook Inlet",
                    time = "Quarterly repeats from 2012 to 2021",
                    included = True,
                    notes = "Not used in the NWGOA model/data comparison.",
                    maptype = "line",
                    featuretype = "trajectoryProfile",
                    map_description = "CTD Transects",
                    summary = """
The Kachemak Bay Research Reserve (KBRR) and NOAA Kasitsna Bay Laboratory jointly work to complete oceanographic monitoring in Kachemak Bay and lower Cook Inlet, in order to provide the physical data needed for comprehensive restoration monitoring in the Exxon Valdez oil spill (EVOS) affected area. This project utilized small boat oceanographic and plankton surveys at existing KBRR water quality monitoring stations to assess spatial, seasonal and inter-annual variability in water mass movement. In addition, this work leveraged information from previous oceanographic surveys in the region, provided environmental information that aided a concurrent Gulf Watch benthic monitoring project, and benefited from a new NOAA ocean circulation model for Cook Inlet.

Surveys are conducted annually along five primary transects; two in Kachemak Bay and three in lower Cook Inlet, Alaska. Oceanographic data were collected via vertical CTD casts from surface to bottom, zooplankton and phytoplankton tows were made in the upper water column, and seabird and marine mammal observations were performed opportunistically. We also collect meteorological data and water quality measurements in Homer Harbor and Anchor Point year-round at stations as part of our National Estuarine Research Reserve (NERR) System-wide Monitoring program in Seldovia and Homer harbors, and in ice-free months at a mooring near the head of Kachemak Bay.

Project files and further description can be found here: https://gulf-of-alaska.portal.aoos.org/#metadata/4e28304c-22a1-4976-8881-7289776e4173/project
    """
    )
    
    header_names = ["transect_3", "transect_4", "transect_6", "transect_7", "transect_9", "transect_AlongBay"]
    
    urls = [
        "https://researchworkspace.com/files/42203150/CookInletKachemakBay_CTD_2012_subsetted.csv",
            "https://researchworkspace.com/files/42203152/CookInletKachemakBay_CTD_2013_subsetted.csv",
            "https://researchworkspace.com/files/42203153/CookInletKachemakBay_CTD_2014_subsetted.csv",
            "https://researchworkspace.com/files/42203154/CookInletKachemakBay_CTD_2015_subsetted.csv",
            "https://researchworkspace.com/files/42203155/CookInletKachemakBay_CTD_2016_subsetted.csv",
            "https://researchworkspace.com/files/42203156/CookInletKachemakBay_CTD_2017_subsetted.csv",
            "https://researchworkspace.com/files/42203157/CookInletKachemakBay_CTD_2018_subsetted.csv",
            "https://researchworkspace.com/files/42203158/CookInletKachemakBay_CTD_2019_subsetted.csv",
            "https://researchworkspace.com/files/42203159/CookInletKachemakBay_CTD_2020_subsetted.csv",
            "https://researchworkspace.com/files/42203160/CookInletKachemakBay_CTD_2021_subsetted.csv",
            "https://researchworkspace.com/files/42203161/CookInletKachemakBay_CTD_2022_subsetted.csv",
            # added for CIOFS3 project
            "https://researchworkspace.com/files/42735311/CoofkInletKachemakBay_CTD_2023.csv",
            "https://researchworkspace.com/files/45011378/CookInletKachemakBay_CTD_2024.csv",
    ]
    
    cat = intake.entry.Catalog(metadata=metadata)

    for url in urls:

        if "2023" in url or "2024" in url:
            csv_kwargs = dict(dtype={'Transect': 'str'}, header=1, usecols=lambda col: col != "Station")
        else:
            csv_kwargs = dict(parse_dates=[0], dtype={'Transect': 'str', 'Visit': 'str'})


        # year = Path(url).stem.split("_")[-2]
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        df = pd.read_csv(url, **csv_kwargs)
        # import pdb; pdb.set_trace()

        if "2023" in url or "2024" in url:
            usecols = list(df.columns)
            # df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%Y-%m-%d %H:%M")
            # df = df.drop(columns=["Time"])
            df = df.rename(columns={"Date": "Visit"})
            # # Move "datetime" to the first column
            # cols = ['datetime'] + [col for col in df.columns if col != 'datetime']
            # df = df[cols]
            # replace "lambda" in csv_kwargs
            csv_kwargs["usecols"] = usecols
            # #sort
            # df = df.sort_values(by=["datetime"])

        hover_cols = cic.utils.get_hover_cols(df, distance=True)
    
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)

        
        # "Visit" and "Transect" uniquely identify each transect
        for i in set(df.set_index(["Visit", "Transect"]).index):
            visit, transect = i
            name = f"transect_{transect}-{visit}"
            ddf = cic.utils.select_df_visit_transect(df, i)
            initial_reader = initial_reader.apply(cic.utils.rename_Date_Visit)
            reader1station = initial_reader.apply(cic.utils.select_df_visit_transect, i)
            reader1station = reader1station.apply(cic.utils.calculate_distance)

            plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols, title=name)
            reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                                "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
            reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
            cat[name] = reader1station
            cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")
            

def ctd_transects_misc_2002(slug, simplecache):
    metadata = dict(project_name = "CTD transects 2002",
        overall_desc = "CTD transects (2002)",
        time = "2002",
        included = True,
        notes = "",
        maptype = "line",
        featuretype = "trajectoryProfile",
        header_names = None,
        map_description = "CTD Transects",
        summary = f"""Miscellaneous CTD transects in Cook Inlet from 2002
"""
    )
    
    urls = ["https://researchworkspace.com/files/42186319/Bear_Jul-02.csv",
            "https://researchworkspace.com/files/42186397/Cohen.csv",
            "https://researchworkspace.com/files/42199559/Glacier.csv",
            "https://researchworkspace.com/files/42199566/Peterson_Jul-02.csv",
            "https://researchworkspace.com/files/42199989/pogibshi_Jul-02.csv",
            "https://researchworkspace.com/files/42200000/PtAdam_jul-02.csv",]
    
    csv_kwargs = dict()#parse_dates={"date_time": ["Date","Time (local 24 hr)"]})#, index_col="date_time") 
    cat = intake.entry.Catalog(metadata=metadata)

    # each file is a transect so this is easier than usual for transects
    for url in urls:
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        initial_reader = initial_reader.rename(columns={"Date": "date", "Time (local 24 hr)": "time"})
        new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
        reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time'])
        reader_dates_parsed = reader_dates_parsed.apply(cic.utils.calculate_distance)
        reader_dates_parsed = reader_dates_parsed.apply(cic.utils.convert_tz_AK_UTC)
        df = reader_dates_parsed.read()
        hover_cols = cic.utils.get_hover_cols(df, distance=True)
        name = Path(url).stem

        plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols)
        reader_dates_parsed.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                            "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
        reader_dates_parsed.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))
        
        cat[name] = reader_dates_parsed
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def ctd_transects_otf_kbnerr(slug, simplecache):
    metadata = dict(project_name = "CTD profiles 2003-2006 - OTF KBNERR",
        overall_desc = "CTD Transect (OTF KBNERR): Repeated from Anchor Point",
        time = "Daily in July, 2003 to 2006",
        included = True,
        notes = "These data were not included in the NWGOA model/data comparison",
        maptype = "line",
        featuretype = "trajectoryProfile",
        header_names = ["2003", "2004", "2005", "2006"],
        map_description = "CTD Transects",
        summary = """CTD Transect Across Anchor Point, for GEM Project 030670.

This project used a vessel of opportunity to collect physical oceanographic and fisheries data at six stations along a transect across lower Cook Inlet from Anchor Point (AP) to the Red River delta each day during July. Logistical support for the field sampling was provided in part by the Alaska Department of Fish and Game which has chartered a drift gillnet vessel annually to fish along this transect providing inseason projections of the size of sockeye salmon runs entering Cook Inlet. This project funded collection of physical oceanographic data on board the chartered vessel to help identify intrusions of the Alaska Coastal Current (ACC) into Cook Inlet and test six hypotheses regarding effects of changing oceanographic conditions on migratory behavior and catchability of sockeye salmon entering Cook Inlet. In 2003-2007, a conductivity-temperature-depth profiler was deployed at each station. In 2003-2005, current velocities were estimated along the transect using a towed acoustic Doppler current profiler, and salmon relative abundance and vertical distribution was estimated using towed fisheries acoustic equipment.

Willette, T.M., W.S. Pegau, and R.D. DeCino. 2010. Monitoring dynamics of the Alaska coastal current and development of applications for management of Cook Inlet salmon - a pilot study. Exxon Valdez Oil Spill Gulf Ecosystem Monitoring and Research Project Final Report (GEM Project 030670), Alaska Department of Fish and Game, Commercial Fisheries Division, Soldotna, Alaska.

Report: https://evostc.state.ak.us/media/2176/2004-040670-final.pdf
Project description: https://evostc.state.ak.us/restoration-projects/project-search/monitoring-dynamics-of-the-alaska-coastal-current-and-development-of-applications-for-management-of-cook-inlet-salmon-040670/
"""
    )

    urls = ["https://researchworkspace.com/files/39890736/otf2003_sbe19.txt",
            "https://researchworkspace.com/files/39890793/otf2003_sbe25.txt",
            "https://researchworkspace.com/files/39886054/otf2004.txt",
            "https://researchworkspace.com/files/39886055/otf2005.txt",
            "https://researchworkspace.com/files/39886053/otf2006.txt"]
    cat = intake.entry.Catalog(metadata=metadata)

    csv_kwargs = dict(encoding = "ISO-8859-1", sep="\t", #parse_dates={"date_time": ["mon/day/yr","hh:mm"]},
                    dtype={'Depth [m]': 'float64', 'O2 [%sat]': 'float64', 'Station': 'float64'})
    # minlon, minlat, maxlon, maxlat = -152.438333, 59.825, -152.151667, 59.87333
    for url in urls:
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        # df = pd.read_csv(url, **csv_kwargs)
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        initial_reader = initial_reader.rename(columns={"mon/day/yr": "date", "hh:mm": "time"})
        new_dates_column = initial_reader.apply(cic.utils.parse_date_time)
        reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=['date', 'time', 'Pressure [m]', 'Sigma-é00', 'Pressure ', 'Density [sigma]'], errors="ignore")
        df = reader_dates_parsed.read()
        hover_cols = cic.utils.get_hover_cols(df, distance=True)
        plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols)
        for day in np.arange(1,31):
            day = int(day)
            year = Path(url).stem.split("otf")[1].split("_")[0]
            name = f"{year}-07-{str(day).zfill(2)}"
            reader1station = reader_dates_parsed.apply(cic.utils.select_df_year_day_of_july, year, day)
            reader1station = reader1station.apply(cic.utils.calculate_distance)
            # ddf = reader1station.read()
            ddf = cic.utils.select_df_year_day_of_july(df, year, day)
            if len(ddf.dropna(subset=df.cf["T"].name)) == 0:
                continue
            # if len(ddf.reset_index(drop=True).dropna(subset="date_time")) == 0:
            #     continue

            reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                                "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
            reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
            
            cat[name] = reader1station
            cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def ctd_transects_uaf(slug, simplecache):
    metadata = dict(project_name = "CTD time series UAF",
        overall_desc = "CTD Transects (UAF): Repeated in central Cook Inlet",
        time = "26-hour period on 9-10 August 2003",
        included = True,
        notes = "Year for day 2 was corrected from 2004 to 2003. Not used in the NWGOA model/data comparison.",
        maptype = "line",
        featuretype = "trajectoryProfile",
        header_names = None,
        map_description = "CTD Transects",
        summary = f"""Observations of hydrography and currents in central Cook Inlet, Alaska during diurnal
and semidiurnal tidal cycles

Surface-to-bottom measurements of temperature, salinity, and transmissivity, as well as measurements of surface currents (vessel drift speeds) were acquired along an east-west section in central Cook Inlet, Alaska during a 26-hour period on 9-10 August 2003. These measurements are used to describe the evolution of frontal features (tide rips) and physical properties along this section during semidiurnal and diurnal tidal cycles. The observation that the amplitude of surface currents is a function of water depth is used to show that strong frontal features occur in association with steep bathymetry. The positions and strengths of these fronts vary with the semidiurnal tide. The presence of freshwater gradients alters the phase and duration of tidal currents across the section. Where mean density-driven flow is northward (along the eastern shore and near Kalgin Island), the onset of northward tidal flow (flood tide) occurs earlier and has longer duration than the onset and duration of northward tidal flow where mean density-driven flow is southward (in the shipping channel). Conversely, where mean density-driven flow is southward (in the shipping channel), the onset of southward tidal flow (ebb tide) occurs earlier and has longer duration than the onset and duration of southward tidal flow along the eastern shore and near Kalgin Island. 

Observations of hydrography and currents in central Cook Inlet, Alaska during diurnal
and semidiurnal tidal cycles
Stephen R. Okkonen
Institute of Marine Science
University of Alaska Fairbanks
Report: https://www.circac.org/wp-content/uploads/Okkonen_2005_hydrography-and-currents-in-Cook-Inlet.pdf
"""
    )

    csv_kwargs = dict(parse_dates=["date_time"])
    url = "https://researchworkspace.com/files/42202256/TS%20downcasts.csv"
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    df = pd.read_csv(url, **csv_kwargs)
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    hover_cols = cic.utils.get_hover_cols(df, distance=True)
    plot_kwargs = dict(x=distkey, y=df.cf["Z"].name, flip_yaxis=True, hover_cols=hover_cols)
    
    transects = [1,2,3,4,5,6,7,8,9]
    cat = intake.entry.Catalog(metadata=metadata)

    for transect in transects:
        name = f"Transect_{str(transect).zfill(2)}"
        reader1station = initial_reader.apply(cic.utils.select_df_by_column, "transect", transect)
        reader1station = reader1station.apply(cic.utils.calculate_distance)
        # ddf = getattr(chr.src.process, slug)(df, transect)
        ddf = cic.utils.select_df_by_column(df, "transect", transect)
        title = f"{str(ddf.cf['T'][0])}"
        plot_kwargs["title"] = title

        reader1station.metadata = {"plots": {"salt": cic.utils.scatter_dict(df.cf["salt"].name, cmap=cic.cmap["salt"], **plot_kwargs),
                            "temp": cic.utils.scatter_dict(df.cf["temp"].name, cmap=cic.cmap["temp"], **plot_kwargs)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        
        cat[name] = reader1station
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def moorings_kbnerr_historical(slug, simplecache):
    metadata = dict(project_name = "Historical moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)",
        overall_desc = "Moorings (KBNERR): Historical, Kachemak Bay",
        time = "From 2001 to 2003, variable",
        included = True,
        notes = "These are accessed from Research Workspace.",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Moorings",
        summary = f"""Historical moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)
    
More information: https://accs.uaa.alaska.edu/kbnerr/
"""
    )

    urls = ["https://researchworkspace.com/files/42202441/kacbcwq_subsetted.csv",
            "https://researchworkspace.com/files/42202443/kacdlwq_subsetted.csv",
            "https://researchworkspace.com/files/42202445/kachowq_subsetted.csv",
            "https://researchworkspace.com/files/42202447/kacpgwq_subsetted.csv",
            "https://researchworkspace.com/files/42202449/kacsewq_subsetted.csv",
    ]
    csv_kwargs = dict(parse_dates=[0])#, index_col="DateTimeStamp")
    cat = intake.entry.Catalog(metadata=metadata)
    
    for url in urls:
        name = Path(url).stem.rstrip("_subsetted")
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
        df = pd.read_csv(url, **csv_kwargs)
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        hover_cols = cic.utils.get_hover_cols(df)
        plot_kwargs = dict(x=df.cf["T"].name, y=[df.cf["temp"].name, df.cf["salt"].name], subplots=False, hover_cols=hover_cols)
        initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
        initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))
        cat[name] = initial_reader
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def hfradar(slug, simplecache):
    metadata = dict(project_name = "HF Radar - UAF",
        overall_desc = "HF Radar (UAF)",
        time = "2002-2009",
        included = True,
        notes = "These are accessed from Research Workspace where they have already been processed.",
        maptype = "box",
        featuretype = "grid",
        header_names = ["Lower CI/System B, 2006-2007: Weekly Subtidal Means",
                        "Lower CI/System B, 2006-2007: Tidal Constituents",
                        "Upper CI/System A, 2002-2003: Weekly Subtidal Means",
                        "Upper CI/System A, 2002-2003: Tidal Constituents",
                        "Upper CI/System A, 2009: Weekly Subtidal Means",
                        "Upper CI/System A, 2009: Tidal Constituents",
                        ],
        map_description = "HF Radar Data Areas",
        summary = f"""HF Radar from UAF.

Files are:

* Upper Cook Inlet (System A): 2002-2003 and 2009
* Lower Cook Inlet (System B): 2006-2007

Data variables available include tidally filtered and weekly averaged along with tidal constituents calculated from hourly data.

Several new datasets were derived in 2024 with the CIOFS freshwater project which narrow the full time datasets (lower-ci_system-B_2006-2007.nc and upper-ci_system-A_2002-2003.nc) in time to just 2003 and 2006, respectively, before running processing in Research Workspace and are otherwise identical. See processing notebook https://researchworkspace.com/file/44879475/add_variables_to_notebooks_limited_time_range.ipynb:
* lower-ci_system-B_2006_subtidal_daily_mean.nc
* lower-ci_system-B_2006_tidecons_base.nc
* lower-ci_system-B_2006_subtidal_weekly_mean.nc
* upper-ci_system-A_2003_subtidal_daily_mean
* upper-ci_system-A_2003_tidecons_base
* upper-ci_system-A_2003_subtidal_weekly_mean.nc
    
Some of the data is written up in reports:

* https://espis.boem.gov/final%20reports/5009.pdf
* https://www.govinfo.gov/app/details/GOVPUB-I-47b721482d69e308aec1cca9b3e51955

![pic](https://researchworkspace.com/files/40338104/UAcoverage.gif)
"""
    )

    urls = ["https://researchworkspace.com/files/42712165/lower-ci_system-B_2006-2007.nc",
            "https://researchworkspace.com/files/42712210/lower-ci_system-B_2006-2007_subtidal_weekly_mean.nc",
            "https://researchworkspace.com/files/42712190/lower-ci_system-B_2006-2007_tidecons_base.nc",
            "https://researchworkspace.com/files/44879883/lower-ci_system-B_2006_subtidal_daily_mean.nc",
            "https://researchworkspace.com/files/44879885/lower-ci_system-B_2006_tidecons_base.nc",
            "https://researchworkspace.com/files/44879896/lower-ci_system-B_2006_subtidal_weekly_mean.nc",
            "https://researchworkspace.com/files/42712163/upper-ci_system-A_2002-2003.nc",
            "https://researchworkspace.com/files/42712206/upper-ci_system-A_2002-2003_subtidal_weekly_mean.nc",
            "https://researchworkspace.com/files/42712182/upper-ci_system-A_2002-2003_tidecons_base.nc",
            "https://researchworkspace.com/files/44879877/upper-ci_system-A_2003_subtidal_daily_mean.nc",
            "https://researchworkspace.com/files/44879879/upper-ci_system-A_2003_tidecons_base.nc",
            "https://researchworkspace.com/files/44879894/upper-ci_system-A_2003_subtidal_weekly_mean.nc",
            "https://researchworkspace.com/files/42712167/upper-ci_system-A_2009.nc",
            "https://researchworkspace.com/files/42712214/upper-ci_system-A_2009_subtidal_weekly_mean.nc",
            "https://researchworkspace.com/files/42712200/upper-ci_system-A_2009_tidecons_base.nc",
            ]

    cat = intake.entry.Catalog(metadata=metadata)
    # dynamic should be True to use in notebooks but False for when compiling for docs
    more_kwargs = dict(width=700, height=550, geo=True, tiles=True, dynamic=True, xlabel="Longitude", ylabel="Latitude")

    for url in urls:

        # details for options here for simplecache or not: https://github.com/intake/intake/issues/825
        # of_local = fsspec.open_local(f"simplecache://::{url}", mode="rb")
        url = f"simplecache://::{url}"
        # ds = xr.open_dataset(of_local)
        # data = intake.readers.datatypes.HDF5(url, storage_options={"cache_type": "all"})
        if simplecache:
            data = intake.readers.datatypes.HDF5(url, simplecache_options)
        else:
            data = intake.readers.datatypes.HDF5(url)
        initial_reader = data.to_reader("xarray:Dataset", chunks={})#, open_local=True)
        ds = initial_reader.read()
        plot_kwargs = dict(x=ds.cf["longitude"].name, y=ds.cf["latitude"].name, flip_yaxis=False, rasterize=False, 
                            hover=True)

        if "tidecons" in url:
            name = Path(url).stem.split("_base")[0]
            initial_reader.metadata = {"plots": {"tidecons": cic.utils.quadmesh_dict("tidecons", cmap="cmo.tarn", **plot_kwargs, **more_kwargs)}}

        # picking out the full time resolution files so can use them in OMSA
        # this was "_all" in the previous version
        elif "tidecons" not in url and "subtidal" not in url:
            name = Path(url).stem
            initial_reader.metadata = {"plots": {"east": cic.utils.quadmesh_dict(var="u", cmap=cic.cmap["u"], 
                                                                    vmax=round(float(ds.u.max())), symmetric=False, 
                                                                    **plot_kwargs, **more_kwargs),
                                "north": cic.utils.quadmesh_dict(var="v", cmap=cic.cmap["u"], 
                                                                    vmax=round(float(ds.v.max())), symmetric=False, 
                                                                    **plot_kwargs, **more_kwargs),
                                }}
            initial_reader.metadata["key_variables"] = ["east","north"]

        else:  # "subtidal" in url
            name = Path(url).stem
            initial_reader.metadata = {"plots": {"speed": cic.utils.quadmesh_dict(var="speed_subtidal", cmap=cic.cmap["speed"], 
                                                                    vmax=round(float(ds["speed_subtidal"].max())), symmetric=False, 
                                                                    **plot_kwargs, **more_kwargs),
                                "direction": cic.utils.vector_dict(ds.cf["longitude"].name, ds.cf["latitude"].name, 
                                                                    "direction_subtidal", "speed_subtidal", **more_kwargs),}}
            initial_reader.metadata["key_variables"] = ["east","north"]

        initial_reader.metadata.update(cic.utils.add_metadata(ds, metadata["maptype"], metadata["featuretype"], url))
        cat[name] = initial_reader
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def make_erddap_catalog(slug, project_name, overall_desc, time, included, notes, maptype, featuretype,
                        header_names, map_description, summary, stations, open_kwargs,
                        simplecache):
    metadata = dict(project_name = project_name, overall_desc = overall_desc, time = time, included = included,
                    notes = notes, maptype = maptype, featuretype = featuretype, header_names = header_names,
                    map_description = map_description, summary = summary)
    import intake_erddap
    vars = ["sea_water_temperature", "sea_water_practical_salinity",
            "sea_surface_temperature",
            "water_surface_above_station_datum",
            "sea_surface_height_above_sea_level_geoid_local_station_datum",
            "sea_surface_height_above_sea_level_geoid_mllw"]
    inputs = dict(search_for=stations, 
                                 query_type="union",
                                 name=slug,
                                 description=overall_desc,
                                 use_source_constraints=True,
                                 start_time = "1999-01-01T00:00:00Z",
                                 open_kwargs=open_kwargs,
                                 dropna=True,
                                 mask_failed_qartod=True,
                                 variables=vars,
                                #  variable_names=["sea_water_temperature"]  can't do these because are treated equivalent to searching for station names the way it is set up now and are all added together
                                #  metadata=metadata,
    )
    if simplecache:
        inputs.update(cache_kwargs=simplecache_options)

    cat = intake_erddap.ERDDAPCatalogReader(server="https://erddap.aoos.org/erddap", **inputs).read()
    
    for dataset_id in list(cat):
        
        # read in info url instead of pinging the actual data
        ddf = pd.read_csv(cat[dataset_id].metadata["info_url"])
        # this creates an empty DataFrame with column names of the variables in the dataset
        # these can be checked with cf-pandas to fill in variable names in the metadata plots
        ddf = pd.DataFrame(columns=ddf[ddf["Row Type"] == "variable"]["Variable Name"])
        extra_keys = ["ssh","temp","salt","u","v","speed"]
        # import pdb; pdb.set_trace()
        out = [(key, ddf.cf[key].name) for key in extra_keys if key in ddf.cf.keys()]
        vars_to_use, var_names = zip(*out)
        hover_cols = cic.utils.get_hover_cols(ddf, distance=False, extra_keys=extra_keys)
        plot_kwargs = dict(x=ddf.cf["T"].name, y=var_names, hover_cols=hover_cols, subplots=False)#True)

        cat.get_entity(dataset_id).metadata.update({"maptype": maptype,
                                "featuretype": featuretype,
                                "plots": {"data": cic.utils.line_time_dict(**plot_kwargs),},
                                "urlpath": cat[dataset_id].metadata["tabledap"],
                                "key_variables": vars_to_use,
                                "variables": var_names},)

    cat.metadata.update(metadata)
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def moorings_aoos_cdip(slug, simplecache):
    metadata = dict(project_name = "Moorings from Alaska Ocean Observing System (AOOS)/ Coastal Data Information Program (CDIP)",
        overall_desc = "Moorings (CDIP): Lower and Central Cook Inlet, Kodiak Island",
        time = "From 2011 to 2023, variable",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Moorings",
        summary = f"""Moorings from AOOS/CDIP
"""
    )
    stations = ["aoos_204", 
                "edu_ucsd_cdip_236",
                "central-cook-inlet-175"]
    # need response of "csv" so that column names match from info_url to data column names
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug=slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)


def moorings_circac(slug, simplecache):
    metadata = dict(project_name = "Mooring from CIRCAC",
        overall_desc = "Mooring (CIRCAC): Central Cook Inlet Mooring",
        time = "Two weeks in August 2006, 15 min sampling",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Time Series Location",
        summary = f"""Central Cook Inlet Mooring from: Seasonality of Boundary Conditions for Cook Inlet, Alaska

CIRCAC is the Cook Inlet Regional Citizens Advisory Council. It was funded by MMS (pre-BOEM), OCS Study MMS 2009-041 funneled through the Coastal Marine Institute (University of Alaska Fairbanks).

This mooring was damaged so it was removed.

Part of the project:
Seasonality of Boundary Conditions for Cook Inlet, Alaska
Steve Okkonen Principal Investigator
Co-principal Investigators: Scott Pegau Susan Saupe
Final Report
OCS Study MMS 2009-041
August 2009
Report: https://researchworkspace.com/files/39885971/2009_041.pdf

<img src="https://user-images.githubusercontent.com/3487237/233167915-c0b2b0e1-151e-4cef-a647-e6311345dbf9.jpg" alt="alt text" width="300"/>

"""
        )
    
    url = "https://researchworkspace.com/files/39886029/xto_mooring_2006.txt"

    csv_kwargs = dict(sep="\t", parse_dates=["Date UTC"])
    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options
    lon, lat = -(151 + 30.3/60), 60 + 45.7/60

    cat = intake.entry.Catalog(metadata=metadata)
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    # add location columns
    initial_reader = initial_reader.assign(longitude_deg=lon)
    initial_reader = initial_reader.assign(latitude_deg=lat)
    # df = pd.read_csv(url, **csv_kwargs)
    df = initial_reader.read()
    hover_cols = cic.utils.get_hover_cols(df)
    plot_kwargs = dict(x=df.cf["T"].name, y=[df.cf["temp"].name, df.cf["salt"].name], subplots=False, hover_cols=hover_cols)
    initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
    initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))
    cat[slug] = initial_reader
    cat.aliases[slug] = slug

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def moorings_kbnerr(slug, simplecache):
    metadata = dict(project_name = "Moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)",
        overall_desc = "Moorings (KBNERR): Lower Cook Inlet Mooring",
        time = "Aug to Oct 2006 and June 2007 to Feb 2008, 15 min sampling",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Time Series Location",
        summary = f"""Lower Cook Inlet Mooring from: Seasonality of Boundary Conditions for Cook Inlet, Alaska

CIRCAC is the Cook Inlet Regional Citizens Advisory Council. It was funded by MMS (pre-BOEM), OCS Study MMS 2009-041 funneled through the Coastal Marine Institute (University of Alaska Fairbanks).

Part of the project:
Seasonality of Boundary Conditions for Cook Inlet, Alaska
Steve Okkonen Principal Investigator
Co-principal Investigators: Scott Pegau Susan Saupe
Final Report
OCS Study MMS 2009-041
August 2009
Report: https://researchworkspace.com/files/39885971/2009_041.pdf

<img src="https://user-images.githubusercontent.com/3487237/233167915-c0b2b0e1-151e-4cef-a647-e6311345dbf9.jpg" alt="alt text" width="300"/>

""")

    urls = ["https://researchworkspace.com/files/39886044/chrome_bay_mooring_deployment_1.txt",
            "https://researchworkspace.com/files/39886045/chrome_bay_mooring_deployment_2.txt"]
    names = ["Deployment1", "Deployment2"]
    csv_kwargs = dict(sep="\t", parse_dates=[0])

    cat = intake.entry.Catalog(metadata=metadata)
    lon, lat = -(151 + 50.860/60), 59 + 12.161/60
    for url, name in zip(urls, names):
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options
    
        data = intake.readers.datatypes.CSV(url)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        # add location columns
        initial_reader = initial_reader.assign(longitude_deg=lon)
        initial_reader = initial_reader.assign(latitude_deg=lat)
        df = initial_reader.read()
        hover_cols = cic.utils.get_hover_cols(df)
        plot_kwargs = dict(x=df.cf["T"].name, y=[df.cf["temp"].name, df.cf["salt"].name], subplots=False, hover_cols=hover_cols)
        initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
        initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))
        cat[name] = initial_reader
        cat.aliases[name] = name

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")
    
    
def moorings_kbnerr_bear_cove_seldovia(slug, simplecache):
    metadata = dict(project_name = "Moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)",
        overall_desc = "Moorings (KBNERR): Kachemak Bay: Bear Cove, Seldovia",
        time = "From 2004 to present day, variable",
        included = True,
        notes = "These are accessed through AOOS portal/ERDDAP server.",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Moorings",
        summary = f"""Moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)
    
Station mappings from AOOS/ERDDAP to KBNERR station list:
* nerrs_kacsdwq :: kacsdwq
* nerrs_kacsswq :: kacsswq

* cdmo_nerrs_bearcove :: This is a different station than kacbcwq, which was active 2002-2003 while this is in 2015. They are also in different locations.
    
More information: https://accs.uaa.alaska.edu/kbnerr/
""")

    stations = ["cdmo_nerrs_bearcove",
                "nerrs_kacsdwq",
                "nerrs_kacsswq"]
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)
    
    
def moorings_kbnerr_homer(slug, simplecache):
    metadata = dict(project_name = "Moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)",
        overall_desc = "Moorings (KBNERR): Kachemak Bay, Homer stations",
        time = "From 2003 to present day, variable",
        included = True,
        notes = "These are accessed through AOOS portal/ERDDAP server.",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Moorings",
        summary = f"""Moorings from Kachemak Bay National Estuarine Research Reserve (KBNERR)
    
Station mappings from AOOS/ERDDAP to KBNERR station list:
* nerrs_kachdwq :: kachdwq
* homer-dolphin-surface-water-q :: kachswq
* nerrs_kach3wq :: kach3wq
    
More information: https://accs.uaa.alaska.edu/kbnerr/
"""
    )

    stations = ["nerrs_kachdwq",
                "homer-dolphin-surface-water-q",
                "nerrs_kach3wq",]
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)


def moorings_noaa(slug, simplecache):
    metadata = dict(project_name = "Moorings from NOAA",
                    overall_desc = "Moorings (NOAA): across Cook Inlet",
                    time = "From 1999 (and earlier) to 2023, variable",
                    included = True,
                    notes = "",
                    maptype = "point",
                    featuretype = "timeSeries",
                    header_names = None,
                    map_description = "Moorings",
                    summary = f"""Moorings from NOAA

Geese Island, Sitkalidak Island, Bear Cove, Anchorage, Kodiak Island, Alitak, Seldovia, Old Harbor, Boulder Point, Albatross Banks, Shelikof Strait
"""
    )
    stations = ["geese-island-gps-tide-buoy", # ssh
                "sitkalidak-island-gps-tide-bu", # ssh
                "noaa_nos_co_ops_9455595", # ssh
                "noaa_nos_co_ops_9455920", # ssh
                # "noaa_nos_co_ops_kdaa2",  # not in our system anymore
                "noaa_nos_co_ops_9457292",
                "noaa_nos_co_ops_9457804",
                "noaa_nos_co_ops_9455500",
                "old-harbor-1",
                "boulder-point",
                # "wmo_46078",  # outside domain
                "wmo_46077",]
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)


def moorings_nps(slug, simplecache):
    metadata = dict(project_name = "Moorings from National Parks Service (NPS)",
        overall_desc = "Moorings (NPS): across Alaska",
        time = "From 2018 to 2019, variable",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeries",
        header_names = None,
        map_description = "Moorings",
        summary = f"""Moorings from NPS
"""
    )
    stations = ["chinitna-bay-ak-tide-station-945",
                "aguchik-island-ak-tide-station-9",]
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)


def moorings_uaf(slug, simplecache):
    metadata = dict(project_name = "Moorings from University of Alaska Fairbanks (UAF)",
                    overall_desc = "Moorings (UAF): Kodiak Island, Peterson Bay",
                    time = "From 2013 to present, variable",
                    included = True,
                    notes = "",
                    maptype = "point",
                    featuretype = "timeSeries",
                    header_names = None,
                    map_description = "Moorings",
                    summary = f"""Moorings from UAF
"""
    )

    stations = ["uaf_ocean_acidification_resea_ko",
                "kodiak-burke-o-lator-kodiak-ak",
                "peterson-bay-ak-gnss-r",]
    open_kwargs = {"parse_dates": [0], "response": "csv", "skiprows": [1]}#, "index_col": "time"}
    
    make_erddap_catalog(slug, **metadata, simplecache=simplecache, stations=stations, open_kwargs=open_kwargs)


# def adcp_moored_tidal(slug, simplecache):
#     # simplecache doesn't work for adcps
#     metadata = dict(project_name = "Moored ADCP - Tidal UPDATEALL",
#         overall_desc = "Moored ADCP (Tidal): across Alaska",
#         time = "From 2000 to 2023, variable",
#         included = True,
#         notes = "",
#         maptype = "point",
#         featuretype = "timeSeriesProfile",
#         header_names = None,
#         map_description = "Moored ADCPs",
#         summary = f"""Moored ADCPs from various sources, all tidal INCLUDE URLS""")
    
#     urls = ["https://mhkdr.openei.org/files/575/cia.mwm1_adv-4m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.mwm1_dn-10m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.mwm1_up-10m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.mwm2_adv-4m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.mwm2_dn-10m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.mwm2_up-10m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.theom_sig500-10m.b1.zip",
#             "https://mhkdr.openei.org/files/575/cia.theom_adv-5m.b1.zip"]
    
    
    
#     if not simplecache:
#         raise ValueError("adcp_moored_tidal requires simplecache to work properly")
    
    
#     # csv_kwargs = {}

#     local_paths = []
             


#     for url in urls:

#         if simplecache:
#             # do this originally to get all downloaded and save hashes
#             known_hash = None
#             # local_zip_path = pooch.retrieve(url, known_hash=known_hash, fname=Path(url).name, path=cic.utils.cache_dir)
#             local_zip_path = Path(pooch.retrieve(url, known_hash=known_hash, fname=Path(url).name, path=cic.utils.cache_dir))
#             # known_hash = pooch.file_hash(local_path)  # this is how to access so they can be saved

#         # else:
#         #     # to skip caching
#         #     inner_path = "cia.mwm1_adv-4m.b1/cia.mwm1_adv-4m.b1.20210701.185335.nc"
            
#         #     # fsspec zip filesystem, caching the whole zip file
#         #     fs = fsspec.filesystem("zip", fo=url)

#         #     with fs.open(inner_path) as f:
#         #         ds = xr.open_dataset(f)


#             import zipfile
#             # zip_loc_name = cache_url.split("/")[-1]
#             # zip_loc_path = Path(cic.utils.cache_dir) / zip_loc_name
#             # dir_name = zip_loc_name.rstrip(".zip")
#             # local_path = local_zip_path.parent / local_zip_path.stem
#             with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
#                 zip_ref.extractall(cic.utils.cache_dir)

#         local_paths.extend(Path(cic.utils.cache_dir).glob(f"{local_zip_path.stem}/*.nc"))

#         # # List all files inside the ZIP
#         # files[cache_url] = [f["filename"] for f in fs.ls("") if f["filename"].endswith(".csv")]
#         # files.extend([f["filename"] for f in fs.ls("") if f["filename"].endswith(".csv")])
#         # print("Files inside ZIP:", files)
#     # csv_kwargs = dict(dtype={"Month": "str", "Year": "str", "Day": "str", "Hour": "str", "Minute": "str"})

#     cat = intake.entry.Catalog(metadata=metadata)
#     for local_path in local_paths:
#         # print(local_path)
        
#         # strip_double_quotes(local_path)


#         # # Open remote ZIP with fsspec (using caching so it’s only downloaded once)
#         # fs = fsspec.filesystem("zip", fo=f"simplecache::{cache_url}")

#         # Read all CSVs into a dict of DataFrames
#         # dfs = {}

#         dataset_id = local_path.stem.replace(".", "_")
#         # import pdb; pdb.set_trace()
#         data = intake.readers.datatypes.HDF5(str(local_path))
#         initial_reader = data.to_reader("xarray:Dataset", chunks={})#, open_local=True)
#         # data = intake.readers.datatypes.CSV(str(local_path))
#         # initial_reader = data.to_reader("pandas:DataFrame", **csv_kwargs)
#         # initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
#         # initial_reader = initial_reader.assign(depth=depth)
#         # new_dates_column = initial_reader.apply(cic.utils.parse_year_month_day_hour_minute)
#         # reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=["Month","Day","Year","Hour","Minute"])
#         df = initial_reader.read()
#         print(df.variables)
#         # import pdb; pdb.set_trace()
#         # print(df)

#         hover_cols = cic.utils.get_hover_cols(df)
#         # points_dict(x, y, c, s, hover_cols, slug)
#         plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
#         # plot_kwargs = dict(x=df.cf["longitude"].name, y=[df.cf["latitude"].name, df.cf["salt"].name], hover_cols=hover_cols)
#         initial_reader.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
#         # initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
#         initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], str(local_path)))

#         cat[dataset_id] = initial_reader
#         cat.aliases[dataset_id] = dataset_id
    
    
    

def adcp_moored_noaa_coi_2005(slug, simplecache):
    # simplecache doesn't work for adcps
    
    # these are still intake v1
    metadata = dict(project_name = "Cook Inlet 2005 Current Survey",
        overall_desc = "Moored ADCP (NOAA): ADCP survey Cook Inlet 2005",
        time = "2005, each for one or a few months",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeriesProfile",
        header_names = None,
        map_description = "Moored ADCPs",
        summary = f"""Moored NOAA ADCP surveys in Cook Inlet

ADCP data has been converted to eastward, northward velocities as well as along- and across-channel velocities, in the latter case using the NOAA-provided rotation angle for the rotation. The along- and across-channel velocities are additionally filtered to show the subtidal signal, which is what is plotted in the dataset page.
"""
    )

    station_list = ["COI0501", "COI0502", "COI0503", "COI0504", "COI0505",
                "COI0506", "COI0507", "COI0508", "COI0509", "COI0510", "COI0511",
                "COI0512", "COI0513", "COI0514", "COI0515", "COI0516", "COI0517",
                "COI0518", "COI0519", "COI0520", "COI0521", "COI0522", "COI0523",
                "COI0524"]
    import intake_coops
    cat = intake_coops.COOPSCatalogReader(station_list, include_source_metadata=True, description=metadata["overall_desc"],
                                name=slug, process_adcp="process_uv").read()
    
    for source_name in list(cat):
        md_new = {"minLongitude": cat[source_name].metadata["lng"],
                    "maxLongitude": cat[source_name].metadata["lng"],
                    "minLatitude": cat[source_name].metadata["lat"],
                    "maxLatitude": cat[source_name].metadata["lat"],
                    "minTime": cat[source_name].metadata["deployments"]["first_good_data"],
                    "maxTime": cat[source_name].metadata["deployments"]["last_good_data"],
                    "flood_direction_degrees": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "angle": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "maptype": metadata["maptype"],
                    "featuretype": metadata["featuretype"],
                    "key_variables": ["east","north","along","across","speed"],
                    "depths": [bin["depth"] for bin in cat[source_name].metadata["bins"]["bins"]],
                    }
        start_date = str(pd.Timestamp(cat[source_name].metadata["deployments"]["first_good_data"]).date())
        title = f"lon: {cat[source_name].metadata['lng']}, lat: {cat[source_name].metadata['lat']}, start date: {start_date}"
        # hard-wire the variable names since we don't otherwise need to load the datasets since the metadata
        # is already provided for min/max times and location
        plot_kwargs = dict(x="t", y="depth", cmap=cic.cmap["u"], width=600, title=title, hover=True)

        cat.get_entity(source_name).metadata.update({"plots": {"ualong": cic.utils.quadmesh_dict(var="ualong_subtidal", **plot_kwargs),
                                             "vacross": cic.utils.quadmesh_dict(var="vacross_subtidal", **plot_kwargs),},
                                           "urlpath": f"https://tidesandcurrents.noaa.gov/stationhome.html?id={source_name}"})
        cat.get_entity(source_name).metadata.update(md_new)

    cat.metadata.update(metadata)
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def adcp_moored_noaa_coi_other(slug, simplecache):
    # simplecache doesn't work for adcps
    metadata = dict(project_name = "Cook Inlet 2002/2003/2004/2008/2012 Current Survey",
        overall_desc = "Moored ADCP (NOAA): ADCP survey Cook Inlet, multiple years",
        time = "From 2002 to 2012, each for one or a few months",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeriesProfile",
        header_names = None,
        map_description = "Moored ADCPs",
        summary = f"""Moored NOAA ADCP surveys in Cook Inlet

ADCP data has been converted to eastward, northward velocities as well as along- and across-channel velocities, in the latter case using the NOAA-provided rotation angle for the rotation. The along- and across-channel velocities are additionally filtered to show the subtidal signal, which is what is plotted in the dataset page.
"""
    )
    
    station_list = ["COI0206", "COI0207", "COI0213", "COI0301", "COI0302", "COI0303",
                "COI0306", "COI0307", "COI0418", "COI0419", "COI0420", "COI0421",
                "COI0422", "COI0801", "COI0802", "COI1201", "COI1202", "COI1203",
                "COI1204", "COI1205", "COI1207", "COI1208", "COI1209", "COI1210"]
    
    import intake_coops
    cat = intake_coops.COOPSCatalogReader(station_list, include_source_metadata=True, description=metadata["overall_desc"],
                                name=slug, process_adcp="process_uv", metadata=metadata).read()
    
    for source_name in list(cat):
        md_new = {"minLongitude": cat[source_name].metadata["lng"],
                    "maxLongitude": cat[source_name].metadata["lng"],
                    "minLatitude": cat[source_name].metadata["lat"],
                    "maxLatitude": cat[source_name].metadata["lat"],
                    "minTime": cat[source_name].metadata["deployments"]["first_good_data"],
                    "maxTime": cat[source_name].metadata["deployments"]["last_good_data"],
                    "flood_direction_degrees": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "angle": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "maptype": metadata["maptype"],
                    "featuretype": metadata["featuretype"],
                    "key_variables": ["east","north","along","across","speed"],
                    "depths": [bin["depth"] for bin in cat[source_name].metadata["bins"]["bins"]],
                    }
        start_date = str(pd.Timestamp(cat[source_name].metadata["deployments"]["first_good_data"]).date())
        title = f"lon: {cat[source_name].metadata['lng']}, lat: {cat[source_name].metadata['lat']}, start date: {start_date}"
        # hard-wire the variable names since we don't otherwise need to load the datasets since the metadata
        # is already provided for min/max times and location
        plot_kwargs = dict(x="t", y="depth", cmap=cic.cmap["u"], width=600, title=title, hover=True)

        cat.get_entity(source_name).metadata.update({"plots": {"ualong": cic.utils.quadmesh_dict(var="ualong_subtidal", **plot_kwargs),
                                             "vacross": cic.utils.quadmesh_dict(var="vacross_subtidal", **plot_kwargs),},
                                           "urlpath": f"https://tidesandcurrents.noaa.gov/stationhome.html?id={source_name}"})
        cat.get_entity(source_name).metadata.update(md_new)

    cat.metadata.update(metadata)
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def adcp_moored_noaa_kod_1(slug, simplecache):
    # simplecache doesn't work for adcps
    metadata = dict(project_name = "Kodiak Island 2009 Current Survey (1)",
        overall_desc = "Moored ADCP (NOAA): ADCP survey Kodiak Island, Set 1",
        time = "2009, each for one or a few months",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeriesProfile",
        header_names = None,
        map_description = "Moored ADCPs",
        summary = f"""Moored NOAA ADCP surveys in Cook Inlet

ADCP data has been converted to eastward, northward velocities as well as along- and across-channel velocities, in the latter case using the NOAA-provided rotation angle for the rotation. The along- and across-channel velocities are additionally filtered to show the subtidal signal, which is what is plotted in the dataset page.

Stations "KOD0914", "KOD0915", "KOD0916", "KOD0917", "KOD0918", "KOD0919", "KOD0920" are not included because they are just outside or along the model domain boundary.
"""
    )
    
    station_list = ["KOD0901", "KOD0902", "KOD0903", "KOD0904", "KOD0905", "KOD0906", "KOD0907", 
                    "KOD0910", "KOD0911", "KOD0912", "KOD0913", 
                    # "KOD0914", "KOD0915", "KOD0916", "KOD0917", "KOD0918", "KOD0919", "KOD0920",  # just outside domain
                    "KOD0921", "KOD0922", "KOD0923", "KOD0924", "KOD0925", ]
                    # "KOD0924", "KOD0925", "KOD0926", "KOD0927", "KOD0928", "KOD0929", "KOD0930", 
                    # "KOD0931", "KOD0932", "KOD0933", "KOD0934", "KOD0935", "KOD0936", "KOD0937", 
                    # "KOD0938", "KOD0939", "KOD0940", "KOD0941", "KOD0942", "KOD0943", "KOD0944", ]
    
    import intake_coops
    cat = intake_coops.COOPSCatalogReader(station_list, include_source_metadata=True, description=metadata["overall_desc"],
                                name=slug, process_adcp="process_uv", metadata=metadata).read()
    
    for source_name in list(cat):
        md_new = {"minLongitude": cat[source_name].metadata["lng"],
                    "maxLongitude": cat[source_name].metadata["lng"],
                    "minLatitude": cat[source_name].metadata["lat"],
                    "maxLatitude": cat[source_name].metadata["lat"],
                    "minTime": cat[source_name].metadata["deployments"]["first_good_data"],
                    "maxTime": cat[source_name].metadata["deployments"]["last_good_data"],
                    "flood_direction_degrees": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "angle": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "maptype": metadata["maptype"],
                    "featuretype": metadata["featuretype"],
                    "key_variables": ["east","north","along","across","speed"],
                    "depths": [bin["depth"] for bin in cat[source_name].metadata["bins"]["bins"]],
                    }
        start_date = str(pd.Timestamp(cat[source_name].metadata["deployments"]["first_good_data"]).date())
        title = f"lon: {cat[source_name].metadata['lng']}, lat: {cat[source_name].metadata['lat']}, start date: {start_date}"
        # hard-wire the variable names since we don't otherwise need to load the datasets since the metadata
        # is already provided for min/max times and location
        plot_kwargs = dict(x="t", y="depth", cmap=cic.cmap["u"], width=600, title=title, hover=True)

        cat.get_entity(source_name).metadata.update({"plots": {"ualong": cic.utils.quadmesh_dict(var="ualong_subtidal", **plot_kwargs),
                                             "vacross": cic.utils.quadmesh_dict(var="vacross_subtidal", **plot_kwargs),},
                                           "urlpath": f"https://tidesandcurrents.noaa.gov/stationhome.html?id={source_name}"})
        cat.get_entity(source_name).metadata.update(md_new)

    cat.metadata.update(metadata)
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def adcp_moored_noaa_kod_2(slug, simplecache):
    # simplecache doesn't work for adcps
    metadata = dict(project_name = "Kodiak Island 2009 Current Survey (2)",
        overall_desc = "Moored ADCP (NOAA): ADCP survey Kodiak Island, Set 2",
        time = "2009, each for one or a few months",
        included = True,
        notes = "",
        maptype = "point",
        featuretype = "timeSeriesProfile",
        header_names = None,
        map_description = "Moored ADCPs",
        summary = f"""Moored NOAA ADCP surveys in Cook Inlet

ADCP data has been converted to eastward, northward velocities as well as along- and across-channel velocities, in the latter case using the NOAA-provided rotation angle for the rotation. The along- and across-channel velocities are additionally filtered to show the subtidal signal, which is what is plotted in the dataset page.
"""
    )
    
    station_list = [
                    # "KOD0901", "KOD0902", "KOD0903", "KOD0904", "KOD0905", "KOD0906", "KOD0907", 
                    # "KOD0910", "KOD0911", "KOD0912", "KOD0913", "KOD0914", "KOD0915", "KOD0916", 
                    # "KOD0917", "KOD0918", "KOD0919", "KOD0920", "KOD0921", "KOD0922", "KOD0923", 
                    "KOD0926", "KOD0927", "KOD0928", "KOD0929", "KOD0930", 
                    "KOD0931", "KOD0932", "KOD0933", "KOD0934", "KOD0935", "KOD0936", "KOD0937", 
                    "KOD0938", "KOD0939", "KOD0940", "KOD0941", "KOD0942", "KOD0943", "KOD0944", ]
    
    import intake_coops
    cat = intake_coops.COOPSCatalogReader(station_list, include_source_metadata=True, description=metadata["overall_desc"],
                                name=slug, process_adcp="process_uv", metadata=metadata).read()
    
    for source_name in list(cat):
        md_new = {"minLongitude": cat[source_name].metadata["lng"],
                    "maxLongitude": cat[source_name].metadata["lng"],
                    "minLatitude": cat[source_name].metadata["lat"],
                    "maxLatitude": cat[source_name].metadata["lat"],
                    "minTime": cat[source_name].metadata["deployments"]["first_good_data"],
                    "maxTime": cat[source_name].metadata["deployments"]["last_good_data"],
                    "flood_direction_degrees": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "angle": cat[source_name].metadata["deployments"]["flood_direction_degrees"],
                    "maptype": metadata["maptype"],
                    "featuretype": metadata["featuretype"],
                    "key_variables": ["east","north","along","across","speed"],
                    "depths": [bin["depth"] for bin in cat[source_name].metadata["bins"]["bins"]],
                    }
        start_date = str(pd.Timestamp(cat[source_name].metadata["deployments"]["first_good_data"]).date())
        title = f"lon: {cat[source_name].metadata['lng']}, lat: {cat[source_name].metadata['lat']}, start date: {start_date}"
        # hard-wire the variable names since we don't otherwise need to load the datasets since the metadata
        # is already provided for min/max times and location
        plot_kwargs = dict(x="t", y="depth", cmap=cic.cmap["u"], width=600, title=title, hover=True)

        cat.get_entity(source_name).metadata.update({"plots": {"ualong": cic.utils.quadmesh_dict(var="ualong_subtidal", **plot_kwargs),
                                             "vacross": cic.utils.quadmesh_dict(var="vacross_subtidal", **plot_kwargs),},
                                           "urlpath": f"https://tidesandcurrents.noaa.gov/stationhome.html?id={source_name}"})
        cat.get_entity(source_name).metadata.update(md_new)

    cat.metadata.update(metadata)
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.points_dict(x="longitude", y="latitude", c="station", s="T",
                                                hover_cols=["station", "T"], title=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def drifters_uaf(slug, simplecache):
    metadata = dict(project_name = "Drifters (UAF), multiple projects",
        overall_desc = "Drifters (UAF)",
        time = "From 2003 to 2020, variable",
        included = True,
        notes = "These are accessed from Research Workspace. Datasets were processed using the `drifters_uaf_processing.py` script and resaved into research workspace, and are accessed from those processed files. See processing file for details.",
        maptype = "box",
        featuretype = "trajectory",
        header_names = None,
        map_description = "Drifters",
        summary = f"""Drifters run by Mark Johnson and others out of UAF with various years and drogue depths.
        
* 2003: 7.5m (Cook Inlet)
* 2004: 5m (Cook Inlet)
* 2005: 5m (Cook Inlet)
* 2006: 5m (Cook Inlet)
* 2012: 1m (Cook Inlet), 15m (Cook Inlet)
* 2013: 1m (Cook Inlet), 15m (Cook Inlet)
* 2014: 1m (Cook Inlet)
* 2019: 1m (Kachemak Bay, Lynn Canal)
* 2020: 1m (Kachemak Bay, Lynn Canal)
"""
    )
    
    # urls are stored in a file in RW
    loc_urls = "https://researchworkspace.com/files/44874936/files.txt"
    df_urls = pd.read_csv(loc_urls, header=None, dtype=str)[0]
    
    csv_kwargs = {"index_col": 0}

    cat = intake.entry.Catalog(metadata=metadata)
    for url in df_urls:
        
        if simplecache:
            url = f"simplecache://::{url}"
            csv_kwargs["storage_options"] = simplecache_options

        dataset_id = url.split("/")[-1].split('.')[0].rstrip("_data")  # like 'CIDrifter0250Y2005_SubsurfaceDrogueAt80M'
        data = intake.readers.datatypes.CSV(url)
        initial_reader = data.to_reader("pandas:DataFrame", **csv_kwargs)
        # import pdb; pdb.set_trace()
        df = initial_reader.read()
        hover_cols = cic.utils.get_hover_cols(df)
        # points_dict(x, y, c, s, hover_cols, slug)
        plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
        # plot_kwargs = dict(x=df.cf["longitude"].name, y=[df.cf["latitude"].name, df.cf["salt"].name], hover_cols=hover_cols)
        initial_reader.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
        # initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
        initial_reader.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))

        cat[dataset_id] = initial_reader
        cat.aliases[dataset_id] = dataset_id

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


# def drifters_uaf_orig(slug, simplecache):
#     metadata = dict(project_name = "Drifters (UAF), multiple projects",
#         overall_desc = "Drifters (UAF)",
#         time = "From 2003 to 2020, variable",
#         included = True,
#         notes = "These are accessed from Research Workspace.",
#         maptype = "box",
#         featuretype = "trajectory",
#         header_names = None,
#         map_description = "Drifters",
#         summary = f"""Drifters run by Mark Johnson and others out of UAF with various years and drogue depths.
        
# * 2003: 7.5m (Cook Inlet)
# * 2004: 5m (Cook Inlet)
# * 2005: 5m, 80m (Cook Inlet)
# * 2006: 5m (Cook Inlet)
# * 2012: 1m (Cook Inlet), 15m (Cook Inlet)
# * 2013: 1m (Cook Inlet), 15m (Cook Inlet)
# * 2014: 1m (Cook Inlet)
# * 2019: 1m (Kachemak Bay, Lynn Canal)
# * 2020: 1m (Kachemak Bay, Lynn Canal)

# Descriptive summary of later drifter deployment: https://www.alaska.edu/epscor/about/newsletters/May-2022-feature-current-events.php, data portal: https://ak-epscor.portal.axds.co/
# """
#     )
    
#     baseurl = "https://researchworkspace.com/files"

#     def return_response(loc):

#         # Make a GET request to the website
#         response = requests.get(loc)

#         # Parse the response as JSON
#         data = response.json()

#         return data

#     # know both of these from the file directory structure
#     file_dirs = ["41810355", "41810414", "41810412", "41810413", "41810415"]
#     file_depths = ["1", "15", "5", "7.5", "80"]

#     urls = []
#     depths = []
#     for file_dir, depth in zip(file_dirs, file_depths):
#         loc = f"https://researchworkspace.com/project/41810350/folder/{file_dir}.table?start=0&sort=fileName&dir=asc"
#         data = return_response(loc)
#         new_urls = [f"{baseurl}/{entry['id']}/{entry['fileName']}" for entry in data]
#         urls.extend(new_urls)
#         depths += [depth]*len(new_urls)

#     # possible_datatypes = [intake.readers.datatypes.CSV, intake.readers.PandasExcel]
#     # possible_datatypes = [intake.readers.datatypes.CSV, intake.readers.datatypes.Excel]
#     csv_kwargs = {"dtype": {'Year': str, 'Month': str, 'Day': str, 'Hour': str, 'Minute': str}}
#     cat = intake.entry.Catalog(metadata=metadata)

#     dataset_ids = []
#     for url, depth in zip(urls, depths):
#         # print(url)

#         dataset_id = url.split("/")[-1].split('.')[0].rstrip("_data")  # like 'CIDrifter0250Y2005_SubsurfaceDrogueAt80M'
#         dataset_ids.append(dataset_id)
        
#         # don't want TiledService or CatalogAPI but do want CSV or Excel as appropriate
#         datatype = [rec for rec in intake.datatypes.recommend(url) if rec not in [intake.readers.datatypes.TiledService,intake.readers.datatypes.CatalogAPI]][0]
#         # import pdb; pdb.set_trace()
#         # # do this until can figure out how to read Excel files
#         # if "Excel" in str(datatype):
#         #     continue
#         # print(datatype)
#         # data = intake.readers.PandasExcel(url)
#         # data = intake.readers.datatypes.Excel(url)
#         if simplecache:
#             url = f"simplecache://::{url}"
#             csv_kwargs["storage_options"] = simplecache_options
#         data = datatype(url)
        
#         initial_reader = data.to_reader("pandas:DataFrame", **csv_kwargs)
#         # reader = data.to_reader("pandas:DataFrame", parse_dates={"datetime": ["Year", "Month", "Day", "Hour", "Minute"]}, date_parser=cic.utils.parse_dates) 
#     #  data = intake.readers.datatypes.Excel(file)
#     # reader = data.to_reader("pandas:DataFrame", parse_dates={"datetime": ["Year", "Month", "Day", "Hour", "Minute"]}, date_parser=parse_dates) 
    
#         new_dates_column = initial_reader.apply(cic.utils.parse_year_month_day_hour_minute)
#         reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=["Year", "Month", "Day", "Hour", "Minute"])#.reindex(columns=["datetime"] + new_cols)
#         reader_dates_parsed = reader_dates_parsed.assign(depth_m=depth)
#         # # run function that cleans tracks which splits them into separate tracks 
#         # # if there is a jump in time greater than a median time step (usually 1 hour)
#         # # or if a track is more than 50% on land (judged by 10m Natural Earth land)
#         # # also removes start and end of track is on land
#         # # this creates extra tracks called "deployments"
#         # reader_new_deployments = cic.utils.clean_tracks(reader_dates_parsed)
        
#         df = reader_dates_parsed.read()
#         # import pdb; pdb.set_trace()
#         hover_cols = cic.utils.get_hover_cols(df)
#         # points_dict(x, y, c, s, hover_cols, slug)
#         plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
#         # plot_kwargs = dict(x=df.cf["longitude"].name, y=[df.cf["latitude"].name, df.cf["salt"].name], hover_cols=hover_cols)
#         reader_dates_parsed.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
#         # reader_dates_parsed.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
#         reader_dates_parsed.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))

#         cat[dataset_id] = reader_dates_parsed
#         cat.aliases[dataset_id] = dataset_id

#     # gather metadata across datasets to add to overall catalog
#     cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
#     # set up plotting overall map, which uses general key names 
#     cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
#     cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
#     cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def drifters_ecofoci(slug, simplecache):
    metadata = dict(project_name = "Drifters: Ecosystems & Fisheries-Oceanography Coordinated Investigations (EcoFOCI)",
        overall_desc = "Drifters (EcoFOCI)",
        time = "From 1986 to 2017 total but 2003-2006, 2012-2014 here",
        included = True,
        notes = "",
        maptype = "box",
        featuretype = "trajectory",
        header_names = None,
        map_description = "Drifters",
        summary = f"""EcoFOCI Project.
        
As described on the [main project website for EcoFOCI](https://www.ecofoci.noaa.gov/):

> We study the ecosystems of the North Pacific Ocean, Bering Sea and U.S. Arctic to improve understanding of ecosystem dynamics and we apply that understanding to the management of living marine resources. EcoFOCI scientists integrate field, laboratory and modeling studies to determine how varying biological and physical factors influence large marine ecosystems within Alaskan waters.

> EcoFOCI is a joint research program between the Alaska Fisheries Science Center (NOAA/ NMFS/ AFSC) and the Pacific Marine Environmental Laboratory (NOAA/ OAR/ PMEL).

Drifter data are being pulled from this webpage: https://www.ecofoci.noaa.gov/drifters/efoci_drifterData.shtml which also has a plot available for each drifter dataset.

Several years of EcoFOCI drifter data are also available in a private Research Workspace project: https://researchworkspace.com/project/41531085/files.
"""
    )

    # years = [2012, 2013, 2014]
    years = [2003, 2004, 2005, 2006, 2012, 2013, 2014]
    baseurl = "https://www.ecofoci.noaa.gov/drifters/"

    # Specify the URL of the webpage you want to parse
    source = "https://www.ecofoci.noaa.gov/drifters/efoci_drifterData.shtml"

    # Send a GET request to the webpage
    response = requests.get(source)

    # Parse the HTML content of the webpage with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Convert the soup to a string so we can use regular expressions
    soup_str = str(soup)

    # Regular expression to match URLs that contain f"data{year}/" and end with ".asc"
    urls = []
    for year in years:
        
        regex = fr'data{year}/\d+_y{year}(?:_withT|_withTandIce)?\.asc'

        # Find all matches in the soup
        matches = re.findall(regex, soup_str)

        # Print the matches
        for match in matches:
            urls.append(baseurl + match)
    names = ["latitude_N", "longitude_E", "year", "day_of_year", "time_utc"]

    # metadata = {"website": "https://www.ecofoci.noaa.gov/", 
    #             "data_website": "https://www.ecofoci.noaa.gov/drifters/efoci_drifterData.shtml",
    #             "demo_notebook": "https://researchworkspace.com/file/43008938/drifters_ecofoci.ipynb",
    #             }
    csv_kwargs = dict(skiprows=29, usecols=[0,1,2,3,4], names=names, sep='\\s+',
                      dtype={"year": str, "day_of_year": str, "time_utc": str})
    cat = intake.entry.Catalog(metadata=metadata)

    # drifter_ids = []
    for i, url in enumerate(urls):
        print(url)

        data = intake.readers.datatypes.CSV(url)
        # data = intake.readers.readers.PandasCSV(url)
        # data = intake.readers.datatypes.Text(url)
        df = intake.readers.readers.PandasCSV(data, dtype=str, nrows=22, comment='"', na_values=["%", ">", "=", ","]).read()
        df[df.iloc[:, 0].str.startswith("Drogue depth:")]
        depth = df[df.iloc[:, 0].str.startswith("Drogue depth:")].values[0][0].split()[-1]
        del(df)
        if depth == 'depth:':  # this means the actual depth value is missing, then skip the drifter
            print("WARNING: using 40m as the default depth when no other information is available.")
            # Ladd, Carol, et al. "Northern Gulf of Alaska eddies and associated anomalies." Deep Sea Research Part I: Oceanographic Research Papers 54.4 (2007): 487-509.
            # Stabeno, Phyllis J., et al. "Long-term observations of Alaska Coastal Current in the northern Gulf of Alaska." Deep Sea Research Part II: Topical Studies in Oceanography 132 (2016): 24-40.
            depth = 40
        # import pdb; pdb.set_trace()
        
        # this can't work for some reason: must be a problem in intake
        # if simplecache:
        #     url = f"simplecache://::{url}"
        #     csv_kwargs["storage_options"] = simplecache_options
        # initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs) 
        initial_reader = data.to_reader("pandas:DataFrame", **csv_kwargs)

        # drop time: use this to later add parse times
        reader_drop_time_cols = initial_reader.drop(columns=['year', 'day_of_year', 'time_utc'])
        reader_data_longitude_fixed = reader_drop_time_cols.assign(longitude_E=initial_reader.longitude_E.multiply(-1))
        reader_data_depth_column = reader_data_longitude_fixed.assign(depth_m=depth)

        # keep time: fix times then parse into one column
        reader_fixed_time = initial_reader.assign(time_utc=initial_reader.time_utc.replace("2400", "2359"))
        reader_dates_parsed = reader_fixed_time.apply(cic.utils.parse_dates_doy)  # just column

        # combine readers
        reader_data_depth_column = reader_data_depth_column.assign(datetime=reader_dates_parsed)
        
        df = reader_data_depth_column.read()
        hover_cols = cic.utils.get_hover_cols(df)
        plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
        reader_data_depth_column.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
        reader_data_depth_column.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], url))

        # create catalog entry
        drifter_id = Path(url).stem
        cat[drifter_id] = reader_data_depth_column
        cat.aliases[drifter_id] = drifter_id

    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")


def strip_double_quotes(file_path):
    file_path = Path(file_path)

    # Read file content
    text = file_path.read_text(encoding="utf-8")

    # Only modify if there are double quotes
    if '"' in text:
        import re
        # cleaned = re.sub(r'"', '', text)
        # Remove quotes and inline whitespace (spaces + tabs), keep newlines
        cleaned = re.sub(r'[" \t]+', '', text)

        # Overwrite the file
        file_path.write_text(cleaned, encoding="utf-8")
        # print(f"Removed quotes from {file_path}")
    else:
        pass
        # print(f"No quotes found in {file_path}")


def drifters_epscor(slug, simplecache):
    metadata = dict(project_name = "Drifters (EPSCoR)",
        overall_desc = "Drifters (EPSCoR)",
        time = "From 2019 to 2022",
        included = True,
        notes = "",
        maptype = "box",
        featuretype = "trajectory",
        header_names = None,
        map_description = "Drifters",
        summary = f"""Alaska EPSCoR Drifter Deployment

* Several drifters are run at a time.
* https://ak-epscor.portal.axds.co/#metadata/e773c142-c003-4441-a32a-8656e051f630/project/folder_metadata/5826151
* files: https://ak-epscor.portal.axds.co/#metadata/e773c142-c003-4441-a32a-8656e051f630/project/files
* Descriptive summary of drifter deployment: https://www.alaska.edu/epscor/about/newsletters/May-2022-feature-current-events.php
* data portal: https://ak-epscor.portal.axds.co/
"""
    )
    
    if not simplecache:
        raise ValueError("drifters_epscor requires simplecache to work properly")
    
    depth = 1  # drifters were in the upper 1m of the water column
    
    # FIRST: GETTING ACCESS TO EACH DRIFTER
    
    # IN CATALOG, FIRST RUN THROUGH AND GET URLS FOR ALL DRIFTERS/FILES.
    # ONCE WE KNOW THESE WE CAN SET UP HOW TO ACCESS EACH DRIFTER

    urls = ["https://workspace.aoos.org/published/file/9ab61c12-a668-45e5-8b87-1f0bbecb54db/2019.zip",
                "https://workspace.aoos.org/published/file/99246dca-acfd-4580-b85b-4557a0cd3d5a/2020.zip",
                "https://workspace.aoos.org/published/file/955868b9-07fd-4cb6-ae56-6234a3d6bc20/2021.zip",
                "https://workspace.aoos.org/published/file/7b509076-3d31-4115-9c5f-fefa7b723662/2022.zip"]
    
    csv_kwargs = {}
    csv_kwargs["storage_options"] = simplecache_options
    # files = {}
    # files = []

    local_paths = []

    for url in urls:

        # Use simplecache so the zip is cached locally
        cache_url = f"simplecache://::{url}"
        # this downloads the zip file to cache
        try:
            pd.read_csv(cache_url, **csv_kwargs)
        except ValueError:
            pass  # we expect this error and use it to cache


        # # Open remote ZIP with fsspec (using caching so it’s only downloaded once)
        # fs = fsspec.filesystem("zip", fo=f"simplecache::{cache_url}")
        # fs.ls("")
        import zipfile
        zip_loc_name = cache_url.split("/")[-1]
        zip_loc_path = Path(cic.utils.cache_dir) / zip_loc_name
        dir_name = zip_loc_name.rstrip(".zip")
        dir_path = Path(cic.utils.cache_dir) / dir_name
        with zipfile.ZipFile(zip_loc_path, "r") as zip_ref:
            zip_ref.extractall(dir_path)
        
        local_paths.extend(sorted(dir_path.glob("*.csv")))

        # # List all files inside the ZIP
        # files[cache_url] = [f["filename"] for f in fs.ls("") if f["filename"].endswith(".csv")]
        # files.extend([f["filename"] for f in fs.ls("") if f["filename"].endswith(".csv")])
        # print("Files inside ZIP:", files)
    csv_kwargs = dict(dtype={"Month": "str", "Year": "str", "Day": "str", "Hour": "str", "Minute": "str"})

    cat = intake.entry.Catalog(metadata=metadata)
    for local_path in local_paths:
        # print(local_path)
        
        strip_double_quotes(local_path)


        # # Open remote ZIP with fsspec (using caching so it’s only downloaded once)
        # fs = fsspec.filesystem("zip", fo=f"simplecache::{cache_url}")

        # Read all CSVs into a dict of DataFrames
        # dfs = {}

        dataset_id = local_path.stem.split("_")[0]

        data = intake.readers.datatypes.CSV(str(local_path))
        # initial_reader = data.to_reader("pandas:DataFrame", **csv_kwargs)
        initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
        initial_reader = initial_reader.assign(depth=depth)
        new_dates_column = initial_reader.apply(cic.utils.parse_year_month_day_hour_minute)
        reader_dates_parsed = initial_reader.assign(datetime=new_dates_column).drop(columns=["Month","Day","Year","Hour","Minute"])
        df = reader_dates_parsed.read()
        # import pdb; pdb.set_trace()
        # print(df)

        hover_cols = cic.utils.get_hover_cols(df)
        # points_dict(x, y, c, s, hover_cols, slug)
        plot_kwargs = dict(x=df.cf["longitude"].name, y=df.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
        # plot_kwargs = dict(x=df.cf["longitude"].name, y=[df.cf["latitude"].name, df.cf["salt"].name], hover_cols=hover_cols)
        reader_dates_parsed.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
        # initial_reader.metadata = {"plots": {"data": cic.utils.line_time_dict(**plot_kwargs)}}
        reader_dates_parsed.metadata.update(cic.utils.add_metadata(df, metadata["maptype"], metadata["featuretype"], str(local_path)))

        cat[dataset_id] = reader_dates_parsed
        cat.aliases[dataset_id] = dataset_id

    # import pdb; pdb.set_trace()
    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")
    

def drifters_lake_clark(slug, simplecache):
    metadata = dict(project_name = "Lake Clark Physical Oceanographic Assessment",
        overall_desc = "Drifters (Lake Clark)",
        time = "2021",
        included = True,
        notes = "",
        maptype = "box",
        featuretype = "trajectory",
        header_names = None,
        map_description = "Drifters",
        summary = f"""Project: Lake Clark Physical Oceanographic Assessment

* PIs: Tyler Hennon (UAF), Tahzay Jones (NPS), Seth Danielson (UAF)
* Deployment Vessels: Norseman II (drifters 01-05), Island C (06-18)
* Drifter Model: STC (surface drogued) 
"""
    )
    
    depth = 0  # surface drogued


    url = "https://researchworkspace.com/files/45150532/drifters_combined.csv"
    
    csv_kwargs = dict()
    depth = 0

    if simplecache:
        url = f"simplecache://::{url}"
        csv_kwargs["storage_options"] = simplecache_options

    # split into single CTD cast units by station
    # df = pd.read_csv(url, **csv_kwargs)
    data = intake.readers.datatypes.CSV(url)
    initial_reader = intake.readers.readers.PandasCSV(data, **csv_kwargs)
    initial_reader = initial_reader.assign(depth=depth).drop(columns=['Unnamed: 0'])
    df = initial_reader.read()

    dataset_ids = sorted(df.cf["station"].unique())
    hover_cols = cic.utils.get_hover_cols(df)
    cat = intake.entry.Catalog(metadata=metadata)

    for dataset_id in dataset_ids:
        
        dataset_id = int(dataset_id)

        # select transect/date to get metadata
        reader1station = initial_reader.apply(cic.utils.select_station, dataset_id)


        # get info for this station for metadata
        ddf = cic.utils.select_station(df, dataset_id)

        # dataset_id = str(dataset_id)

        plot_kwargs = dict(x=ddf.cf["longitude"].name, y=ddf.cf["latitude"].name, c=None, s=None, title="", hover_cols=hover_cols)
        reader1station.metadata = {"plots": {"data": cic.utils.points_dict(**plot_kwargs)}}
        reader1station.metadata.update(cic.utils.add_metadata(ddf, metadata["maptype"], metadata["featuretype"], url))
        # import pdb; pdb.set_trace()

        cat[dataset_id] = reader1station
        cat.aliases[dataset_id] = dataset_id


    # gather metadata across datasets to add to overall catalog
    cat.metadata.update(cic.utils.overall_metadata(cat, list(cat)))
    # set up plotting overall map, which uses general key names 
    cat.metadata["map"] = cic.utils.paths_dict(x="longitude", y="latitude", slug=slug)
    cat.metadata["maplabels"] = cic.utils.labels_dict(x="longitude", y="latitude", text="station")
    cat.to_yaml_file(base_dir / f"catalogs/{slug}.yaml")

    

# Generate all catalogs
if __name__ == "__main__":
    
    simplecache = True
    
    from time import time
    for slug in ["drifters_lake_clark", "drifters_epscor"]:# cic.slugs:
        if not (base_dir / f"catalogs/{slug}.yaml").is_file():
            start_time = time()
            getattr(cic.generate_catalogs, slug)(slug, simplecache=simplecache)
            print(f"Catalog: Slug {slug} required time {time() - start_time}")