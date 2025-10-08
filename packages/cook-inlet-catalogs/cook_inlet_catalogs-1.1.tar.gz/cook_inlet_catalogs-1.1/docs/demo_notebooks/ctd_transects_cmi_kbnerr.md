---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.3
---

```{code-cell}
import intake
import hvplot.pandas
import hvplot.xarray
import cook_inlet_catalogs as cic
import holoviews as hv
```

# CTD Transects, Moored CTD (CMI KBNERR): Six repeat, one single transect, one moored CTD

Seasonality of Boundary Conditions for Cook Inlet, Alaska

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



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("ctd_transects_cmi_kbnerr"))
```

## Plot all datasets in catalog

```{code-cell}
dd, ddlabels = cic.utils.combine_datasets_for_map(cat)
dd.hvplot(**cat.metadata["map"]) * ddlabels.hvplot(**cat.metadata["maplabels"])
```

## List available datasets in the catalog

```{code-cell}
dataset_ids = list(cat)
dataset_ids
```

## Select one dataset to investigate

```{code-cell}
try:
    dataset_id = dataset_ids[2]
except:
    dataset_id = dataset_ids[0]
print(dataset_id)

dd = cat[dataset_id].read()
dd
```

## Plot one dataset

```{code-cell}
keys = list(cat[dataset_id].metadata["plots"].keys())
print(keys)

plots = []
for key in keys:
    plot_kwargs = cat[dataset_id].metadata["plots"][key]
    if "clim" in plot_kwargs and isinstance(plot_kwargs["clim"], list):
        plot_kwargs["clim"] = tuple(plot_kwargs["clim"])
    if "dynamic" in plot_kwargs:
        plot_kwargs["dynamic"] = False
    plots.append(cat[dataset_id].ToHvPlot(**plot_kwargs).read())
hv.Layout(plots).cols(1)
```
