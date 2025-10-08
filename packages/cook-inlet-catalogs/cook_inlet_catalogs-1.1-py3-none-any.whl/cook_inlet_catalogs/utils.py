import appdirs
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import pandas as pd
from pathlib import Path
from importlib.resources import files
import re
import cf_pandas as cfp
import cf_xarray as cfx
import pyproj
import numpy as np


cache_dir = Path(
appdirs.user_cache_dir(
        appname="cook-inlet-catalogs", appauthor="axiom-data-science"
))
cache_dir.mkdir(parents=True, exist_ok=True)
cache_dir = str(cache_dir)

key_variables = ["u","v","east","north","along","across", "ssh", "temp","salt"]

# Set up vocab for universal usage
vocab = cfp.Vocab()
reg = cfp.Reg(include="tem", exclude=["F_","qc","air","dew"], ignore_case=True)
vocab.make_entry("temp", reg.pattern(), attr="name")
reg = cfp.Reg(include="sal", exclude=["F_","qc"], ignore_case=True)
vocab.make_entry("salt", reg.pattern(), attr="name")
reg = cfp.Reg(include_or=["sea_surface_height","zeta","water_surface_above_station_datum"], exclude=["qc","sea_surface_height_amplitude_due_to_geocentric_ocean_tide"], ignore_case=True)
# reg = cfp.Reg(include_or=["sea_surface_height","zeta","water_surface_above_station_datum"], exclude=["qc","sea_surface_height_amplitude_due_to_geocentric_ocean_tide_geoid_mllw"], ignore_case=True)
vocab.make_entry("ssh", reg.pattern(), attr="name")
vocab.make_entry("speed", ["speed","s$"], attr="name")
reg = cfp.Reg(include="along", exclude=["subtidal"], ignore_case=True)
vocab.make_entry("along", reg.pattern(), attr="name")
reg = cfp.Reg(include="across", exclude=["subtidal"], ignore_case=True)
vocab.make_entry("across", reg.pattern(), attr="name")
vocab.make_entry("dir", ["dir","d$"], attr="name")
vocab.make_entry("station", ["station", "Station","id","drifter"], attr="name")
vocab.make_entry("cruise", ["cruise", "Cruise"], attr="name")
vocab.make_entry("distance", ["distance"], attr="name")
reg = cfp.Reg(include_exact="u", ignore_case=True)
vocab.make_entry("east", reg.pattern(), attr="name")
reg = cfp.Reg(include_exact="u_eastward", ignore_case=True)
vocab.make_entry("east", reg.pattern(), attr="name")
reg = cfp.Reg(include_exact="east", ignore_case=True)
vocab.make_entry("east", reg.pattern(), attr="name")
# reg = cfp.Reg(include_or=["sea_water_x_velocity"], ignore_case=True)
# vocab.make_entry("east", reg.pattern(), attr="standard_name")

reg = cfp.Reg(include_exact="v", ignore_case=True)
vocab.make_entry("north", reg.pattern(), attr="name")
reg = cfp.Reg(include_exact="v_northward", ignore_case=True)
vocab.make_entry("north", reg.pattern(), attr="name")
reg = cfp.Reg(include_exact="north", ignore_case=True)
vocab.make_entry("north", reg.pattern(), attr="name")
# reg = cfp.Reg(include_or=["sea_water_y_velocity"], ignore_case=True)
# vocab.make_entry("north", reg.pattern(), attr="standard_name")

vocab.make_entry("M2-major",["M2-major$"], attr="name")

cfp.set_options(custom_criteria=vocab.vocab)
cfx.set_options(custom_criteria=vocab.vocab)

def paths_dict(x, y, slug):
    """for paths plot"""
    
    d = dict(kind="paths", 
             x=x,
             y=y,
             title=slug,
             line_width=5, 
             geo=True, 
             tiles=True, 
             width=600, 
             height=700,
             legend=False, 
             coastline=False, 
             xlabel="Longitude [W]", 
             ylabel="Latitude [N]", 
             )
    
    return d


def points_dict(x=None, y=None, c=None, s=None, hover_cols=[], title="", size=35, tiles=True, color="k",
                width=600, height=700, legend=False, coastline=False, cmap=None, clabel="", clim=None):
    """for points plot"""
    
    d = dict(kind="points", 
             x=x, 
             y=y, 
             c=c, 
             s=s, 
             hover_cols=hover_cols, 
             title=title,
             color=color, 
             size=size, 
             geo=True, 
             tiles=tiles, 
             width=width, 
             height=height,
             legend=legend, 
             coastline=coastline, 
             xlabel="Longitude [W]", 
             ylabel="Latitude [N]", 
             cmap=cmap,
             clabel=clabel,
             clim=clim,
             )
    
    return d


def labels_dict(x, y, text):
    """for labels on points or paths hvplot"""
    
    d = dict(kind="labels", 
             x=x, 
             y=y,
             text=text, 
             geo=True, 
             text_alpha=0.5,
             hover=False, 
             text_baseline='bottom', 
             fontscale=1.5,
             text_font_size='10pt',
             text_color="black",
             )
    return d

def line_time_dict(x, y, hover_cols=True, subplots=True, title=None, shared_axes=False):
    """for property(ies) vs. time"""
    # if dd is None:
    #     xuse = x
    #     yuse = y
    # elif dd is not None:
    #     xuse = [dd.cf[ele].name for ele in x] if isinstance(x, list) else dd.cf[x].name
    #     yuse = [dd.cf[ele].name for ele in y] if isinstance(y, list) else dd.cf[y].name
    d = {"kind": "line",
        "y": [ele for ele in y] if isinstance(y, list) else y,
        "x": [ele for ele in x] if isinstance(x, list) else x,
        # "invert": True,
        # "flip_yaxis": True,
        "subplots": subplots,
        "width": 700,
        "height": 300,
        "shared_axes": shared_axes,
        "hover_cols": hover_cols,
        "title": title,
        "legend": "top",  # legend at top of plot on outside
    }
    return d


def line_depth_dict(x, y, hover_cols=True, title=None, xlabel=None):
    """for property(ies) vs. depth"""

    d = {"kind": "line",
        "y": [ele for ele in y] if isinstance(y, list) else y,
        "x": [ele for ele in x] if isinstance(x, list) else x,
        "invert": True,
        "flip_yaxis": True,
        "subplots": True,
        "width": 300,
        "height": 400,
        "shared_axes": True,
        "hover_cols": hover_cols,
        "title": title,
        "value_label": xlabel,
    }
    return d


def scatter_dict(var, x, y, cmap, flip_yaxis=False, hover_cols=False, title=None):
    d = {"kind": "scatter",
          "x": x,
          "y": y,
          "c": [ele for ele in var] if isinstance(var, list) else var,
          "clabel": var,
          "cmap": cmap,
          "width": 500,# 500,
          "height": 300,#400,
          "flip_yaxis": flip_yaxis,
          "shared_axes": False,
          "hover_cols": hover_cols,
          "title": title,
          }
    return d


def quadmesh_dict(var, x, y, cmap, flip_yaxis=True, width=500, height=300, vmax=None,
                  rasterize=True, symmetric=True, dynamic=True, geo=False, tiles=False,
                  xlabel=None, ylabel=None, hover=True, title=None, shared_axes=False):

    title = title or ""
    if vmax is not None:
        clim = (0, vmax)
    else:
        clim = None
    # if dd is None:
    #     varuse = var
    #     xuse = x
    #     yuse = y
    #     cmapuse = cmap
    # elif dd is not None:
    #     xuse = dd.cf[x].name
    #     yuse = dd.cf[y].name
    #     varuse = [dd.cf[ele].name for ele in var] if isinstance(var, list) else dd.cf[var].name
    #     cmapuse = chr.cmap[var]
    
    xlabel = xlabel or x
    ylabel = ylabel or y
        
    d = {"kind": "quadmesh",
          "x": x,
          "y": y,
          "z": var,
          "clabel": var,
          "cmap": cmap,
          "width": width,# 500,
          "height": height,#400,
          "flip_yaxis": flip_yaxis,
        #   "rasterize": True,
        "title": title,
          "shared_axes": shared_axes,
          "symmetric": symmetric,
          "hover": hover,
          "rasterize": rasterize, 
          "clim": clim,
          "dynamic": dynamic, # True: dynamicmap if widget, False: converts from dynamicmap to holomap
        #   "widget_location": "bottom",
        "geo": geo,
        "tiles": tiles,
        "xlabel": xlabel,
        "ylabel": ylabel,
          }
    return d


def vector_dict(xname, yname, anglename, magname, dynamic=True, width=500, height=300, 
                geo=False, tiles=False, xlabel=None, ylabel=None):
    xlabel = xlabel or xname
    ylabel = ylabel or yname
    # will come through as dynamicmap if widget
    d = {"kind": "vectorfield",
         "x": xname,
         "y": yname,
         "angle": anglename,
         "mag": magname,
         "hover_cols": False,
       "dynamic": dynamic, # True: dynamicmap if widget, False: converts from dynamicmap to holomap
        #   "widget_location": "bottom",
                  "width": width,# 500,
          "height": height,#400,
        "geo": geo,
        "tiles": tiles,
        "xlabel": xlabel,
        "ylabel": ylabel,
         }
    return d

def map_dict(x, y):
    d = {"kind": "scatter",
         "x": x,
         "y": y,
         "c": "jday",
         "clabel": "Julian Day",
         "cmap": "gray",
         "width": 400,# 500,
         "height": 300,#400, 
         "title": f"Locations",
         "aspect": 'equal',}
    return d


def add_metadata(dd, maptype, featuretype, url):
    d = {"minLongitude": float(dd.cf["longitude"].min()),
        "minLatitude": float(dd.cf["latitude"].min()),
        "maxLongitude": float(dd.cf["longitude"].max()),
        "maxLatitude": float(dd.cf["latitude"].max()),
        "minTime": str(dd.cf["T"].values.min()) if "T" in dd.cf.keys() else None,
        "maxTime": str(dd.cf["T"].values.max()) if "T" in dd.cf.keys() else None,
        "maptype": maptype,
        "featuretype": featuretype,
        "key_variables": [key_variable for key_variable in key_variables if key_variable in dd.cf.keys()],
        "urlpath": url
        }
    if d["maptype"] == "line":
        # check if min longitude and min latitude are both in the same observation
        if dd.cf["longitude"].idxmin() == dd.cf["latitude"].idxmin():
            d["minLatitude_match"] = "minLongitude"
            d["maxLatitude_match"] = "maxLongitude"
            
        else:
            d["minLatitude_match"] = "maxLongitude"
            d["maxLatitude_match"] = "minLongitude"
            
        # if dd.cf["longitude"].loc[0] == d["minLongitude"] and dd.cf["latitude"].iloc[0] == d["minLatitude"]:
        #     d["minLatitude_match"] = "minLongitude"

    return d


def overall_metadata(cat, dataset_ids):
    maxLat, maxLon, minLat, minLon = -100, -200, 100, 400
    maxTime, minTime = "1900-01-01", "2100-01-01"
    # maxTime, minTime = pd.Timestamp("1900-01-01"), pd.Timestamp("2100-01-01")
    
    
    key_variables = []
    for dataset_id in dataset_ids:
        # most up-to-date metadata could be in cat[dataset_id].metadata (intake v2) or in
        # cat[dataset_id].describe()["metadata"] (intake v1)
        if 'maxLatitude' in cat[dataset_id].metadata:
            metadata = cat[dataset_id].metadata
        # this hangs:
        # elif 'maxLatitude' in cat[dataset_id].describe()["metadata"]:
        #     metadata = cat[dataset_id].describe()["metadata"]
        else:
            metadata = None
            raise ValueError("Relevant metadata not found in catalog entry.")
        maxLat = max(maxLat, metadata['maxLatitude'])
        maxLon = max(maxLon, metadata['maxLongitude'])
        minLat = min(minLat, metadata['minLatitude'])
        minLon = min(minLon, metadata['minLongitude'])
        maxTime = max(maxTime, metadata['maxTime']) if metadata['maxTime'] is not None else maxTime
        minTime = min(minTime, metadata['minTime']) if metadata['minTime'] is not None else minTime
        key_variables += metadata['key_variables']
    key_variables = list(set(key_variables))
    metadata = {"maxLatitude": maxLat, "maxLongitude": maxLon, "minLatitude": minLat, "minLongitude": minLon,
                            "maxTime": maxTime, "minTime": minTime, "key_variables": key_variables}
    return metadata


def cat_path(slug):
    import cook_inlet_catalogs
    base_dir = files(cook_inlet_catalogs)
    cat_path = base_dir / f"catalogs/{slug}.yaml"
    return cat_path


def combine_datasets_for_map(cat):
    """combine datasets in catalog
    
    using metadata in catalog, respecting maptype
    returns dd for plotting and ddlabels for labeling
    """

    cols = ["longitude", "latitude"] + ["T", "station"] #cat.metadata["plots"]["points"]["hover_cols"]
    # cols = ["minLongitude", "maxLongitude", "minLatitude", "maxLatitude", "minTime", "maxTime"]
    dds = []
    for dataset_id in list(cat):
        ddt = pd.json_normalize(cat[dataset_id].metadata)#[cols]
        ddt["station"] = dataset_id
        ddt["latitude"] = ddt["minLatitude"]
        ddt["longitude"] = np.nan  # placeholder for column name to be caught by keys
        keys = [ddt.cf[col].name for col in cols]
        # make two rows for each dataset in order to have a transect in case is a transect
        if cat[dataset_id].metadata["maptype"] == "line":
            ddt["longitude"] = ddt[cat[dataset_id].metadata["minLatitude_match"]]
            dds.append(ddt[keys])        
            # ddt2 = ddt.copy()
            ddt["latitude"] = ddt["maxLatitude"]
            ddt["longitude"] = ddt[cat[dataset_id].metadata["maxLatitude_match"]]
            dds.append(ddt[keys])        
            # ddt3 = ddt.copy()  
            # need to break up each line with nan's
            ddt["longitude"] = np.nan
            ddt["latitude"] = np.nan
            dds.append(ddt[keys])        
        # simple case
        elif cat[dataset_id].metadata["maptype"] == "point":
            ddt["longitude"] =  ddt["minLongitude"]
            dds.append(ddt[keys])        
        # need to make a box with lines
        elif cat[dataset_id].metadata["maptype"] == "box":
            ddt["longitude"] = ddt["minLongitude"]
            dds.append(ddt[keys])        
            ddt["longitude"] = ddt["maxLongitude"]
            ddt["latitude"] = ddt["minLatitude"]
            dds.append(ddt[keys])        
            ddt["longitude"] = ddt["maxLongitude"]
            ddt["latitude"] = ddt["maxLatitude"]
            dds.append(ddt[keys])        
            ddt["longitude"] = ddt["minLongitude"]
            ddt["latitude"] = ddt["maxLatitude"]
            dds.append(ddt[keys])        
            ddt["longitude"] = ddt["minLongitude"]
            ddt["latitude"] = ddt["minLatitude"]
            dds.append(ddt[keys])        
            # need to break up each line with nan's
            ddt["longitude"] = np.nan
            ddt["latitude"] = np.nan
            dds.append(ddt[keys])        

        # else:
        #     ddt2["latitude"] = ddt2["maxLatitude"]
        
        # ddt3["station"] = np.nan
        # ddt3.cf["T"] = np.nan
        # dds.append(ddt[keys])
        # dds.append(ddt2[keys])
        # dds.append(ddt3[keys])
        # dds.append(ddt[keys])
    dd = pd.concat(dds, ignore_index=True)
    if cat[dataset_id].metadata["maptype"] == "line":
        dd.drop_duplicates(subset=[dd.cf["T"].name, dd.cf["latitude"].name,dd.cf["longitude"].name], inplace=True)
    ddlabels = dd.copy()  # have only one copy of each row, to use for labeling plots
    ddlabels.drop_duplicates(subset=[dd.cf["station"].name], inplace=True)
    
    return dd, ddlabels


def select_station(df, station):
    dd = df[df.cf["station"] == station]
    idup = ~dd.index.duplicated()
    # reset the index as long as I am not using the index
    # columns in OMSA to calculate everything
    return dd.iloc[idup].reset_index(drop=True)


def select_ds_year_month(ds, year, month):
    return ds.cf.sel(T=slice(f"{year}-{month}", f"{year}-{month}"))


def select_df_month(df, month):
    dfd = df.set_index(df.cf["T"].name).loc[f"{df.cf['T'].dt.year[0]}-{month}"].reset_index()
    # dfd["distance [km]"] = calculate_distance(dfd.cf["longitude"], 
    #                                     dfd.cf["latitude"])
    return dfd


def select_df_by_column(df, colname, value):
    dfd = df[df[colname] == value]
    return dfd.reset_index(drop=True)


def select_df_cruise_line(df, cruise, line):
    dff = df[(df["Cruise"] == cruise) & (df.line == line)].copy().reset_index(drop=True)
    # dff = dff.reset_index().set_index(["date_time","Depth [m]","Latitude [degrees_north]","Longitude [degrees_east]"], drop=False)
    return dff


def select_df_visit_transect(df, visit_transect):
    return df[(df["Visit"] == visit_transect[0]) * (df["Transect"] == visit_transect[1])]


def select_df_year_day_of_july(df, year, day):
    return df.set_index(df.cf["T"].name).loc[f"{year}-07-{day}"].reset_index() 


def rename_Date_Visit(df):
    return df.rename(columns={"Date": "Visit"})


def get_hover_cols(df, distance=False, extra_keys=None):
    keys = [df.cf["longitude"].name, df.cf["latitude"].name,
            df.cf["Z"].name, df.cf["T"].name]
    if "station" in df.cf.keys():
        keys += [df.cf["station"].name]        

    if "temp" in df.cf.keys():
        keys += [df.cf["temp"].name]
    elif "salt" in df.cf.keys():
        keys += [df.cf["salt"].name]
    if extra_keys is not None:
        keys += [df.cf[key].name for key in extra_keys if key in df.cf.keys()]
    if distance:
        keys += ["distance [km]"]
    return list(set(keys))


def convert_tz_AK_UTC(df):
    # convert from local time zone to UTC
    df = df.set_index(df.cf["T"].name).tz_localize("US/Alaska").tz_convert("UTC").tz_localize(None).reset_index()
    return df


# def calculate_distance(lons, lats):
def calculate_distance(df):
    """Calculate distance (km), esp for transects."""
    lons, lats = df.cf["longitude"], df.cf["latitude"]
    G = pyproj.Geod(ellps="WGS84")
    distance = G.inv(
        lons[:-1],
        lats[:-1],
        lons[1:],
        lats[1:],
    )[2]
    distance = np.hstack((np.array([0]), distance))
    distance = distance.cumsum() / 1000  # km
    # return distance
    df["distance [km]"] = distance
    return df

# def is_key(s):
#     """to list keys in intake catalog"""
#     # Check if the string is a 16-character hexadecimal string
#     if re.fullmatch(r'[a-fA-F0-9]{16}', s):
#         return False
#     else:
#         return True


# def cat_keys(cat):
#     return [entry for entry in cat.entries if is_key(entry)]


def parse_date_time(df: pd.DataFrame) -> pd.DataFrame:
    return pd.to_datetime(df.date.str.cat(df.time), format='%m/%d/%Y%H:%M')
    # return pd.to_datetime(f"{df.pop('date')} {df.pop('time')}", format="%Y/%m/%d %H:%M")


def parse_year_month_day_hour_minute(df: pd.DataFrame) -> pd.DataFrame:
    date_str = df.Year.str.cat([df.Month, df.Day], sep='-').str.cat(df.Hour.str.cat(df.Minute, sep=':'), sep=' ')
    # date_str = f"{df.Year}-{df.Month}-{df.Day} {df.Hour}:{df.Minute}"
    return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M', exact=False)
    # return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M')



# def parse_dates(Year, Month, Day, Hour, Minute):    
#     date_str = f"{Year}-{Month}-{Day} {Hour}:{Minute}"
#     return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M')


def parse_dates_doy(df: pd.DataFrame) -> pd.DataFrame:
    return pd.to_datetime(df.year.str.cat(df.day_of_year).astype(str).str.cat(df.time_utc), format='%Y%j%H%M')


def plot_map(df, drifter_id, res='10m'):

    # Map
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    land = cfeature.NaturalEarthFeature('physical', 'land', res,
                                    edgecolor='face',
                                    facecolor='#F0EFE4')
    ax.add_feature(land)
    ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '10m',
                                     edgecolor='face',
                                     facecolor=cfeature.COLORS['water'])
    ax.add_feature(land)

    # ax.add_feature(cfeature.LAND)
    # ax.add_feature(cfeature.OCEAN)
    # ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    
    # Add high resolution coastline feature
    ax.coastlines(resolution='10m')

    ax.tick_params(left=False, labelleft=False)

    # Add gridlines and labels
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.5, linestyle='-')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 15}
    gl.ylabel_style = {'size': 15}

    # Drifter
    lonkey, latkey, Tkey = df.cf["longitude"].name, df.cf["latitude"].name, df.cf["T"].name
    df.plot(x=lonkey, y=latkey, ax=ax, legend=False, transform=pc, color="r", label="")
    ax.plot(df.iloc[0][lonkey], df.iloc[0][latkey], "go", ms=15, mec="k", transform=pc, label="start")
    ax.plot(df.iloc[-1][lonkey], df.iloc[-1][latkey], "ko", ms=15, mec="k", transform=pc, label="end");
    
    title = f"Drifter {drifter_id}: {df[Tkey].iloc[0].date()} to {df[Tkey].iloc[-1].date()}"
    ax.set_title(title)
    plt.legend(loc="best")
    
    return fig
