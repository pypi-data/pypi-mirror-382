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

# CTD Transects (GWA): Six repeat transects in Cook Inlet


The Kachemak Bay Research Reserve (KBRR) and NOAA Kasitsna Bay Laboratory jointly work to complete oceanographic monitoring in Kachemak Bay and lower Cook Inlet, in order to provide the physical data needed for comprehensive restoration monitoring in the Exxon Valdez oil spill (EVOS) affected area. This project utilized small boat oceanographic and plankton surveys at existing KBRR water quality monitoring stations to assess spatial, seasonal and inter-annual variability in water mass movement. In addition, this work leveraged information from previous oceanographic surveys in the region, provided environmental information that aided a concurrent Gulf Watch benthic monitoring project, and benefited from a new NOAA ocean circulation model for Cook Inlet.

Surveys are conducted annually along five primary transects; two in Kachemak Bay and three in lower Cook Inlet, Alaska. Oceanographic data were collected via vertical CTD casts from surface to bottom, zooplankton and phytoplankton tows were made in the upper water column, and seabird and marine mammal observations were performed opportunistically. We also collect meteorological data and water quality measurements in Homer Harbor and Anchor Point year-round at stations as part of our National Estuarine Research Reserve (NERR) System-wide Monitoring program in Seldovia and Homer harbors, and in ice-free months at a mooring near the head of Kachemak Bay.

Project files and further description can be found here: https://gulf-of-alaska.portal.aoos.org/#metadata/4e28304c-22a1-4976-8881-7289776e4173/project
    


```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("ctd_transects_gwa"))
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
