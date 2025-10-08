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

# CTD Transect (OTF KBNERR): Repeated from Anchor Point

CTD Transect Across Anchor Point, for GEM Project 030670.

This project used a vessel of opportunity to collect physical oceanographic and fisheries data at six stations along a transect across lower Cook Inlet from Anchor Point (AP) to the Red River delta each day during July. Logistical support for the field sampling was provided in part by the Alaska Department of Fish and Game which has chartered a drift gillnet vessel annually to fish along this transect providing inseason projections of the size of sockeye salmon runs entering Cook Inlet. This project funded collection of physical oceanographic data on board the chartered vessel to help identify intrusions of the Alaska Coastal Current (ACC) into Cook Inlet and test six hypotheses regarding effects of changing oceanographic conditions on migratory behavior and catchability of sockeye salmon entering Cook Inlet. In 2003-2007, a conductivity-temperature-depth profiler was deployed at each station. In 2003-2005, current velocities were estimated along the transect using a towed acoustic Doppler current profiler, and salmon relative abundance and vertical distribution was estimated using towed fisheries acoustic equipment.

Willette, T.M., W.S. Pegau, and R.D. DeCino. 2010. Monitoring dynamics of the Alaska coastal current and development of applications for management of Cook Inlet salmon - a pilot study. Exxon Valdez Oil Spill Gulf Ecosystem Monitoring and Research Project Final Report (GEM Project 030670), Alaska Department of Fish and Game, Commercial Fisheries Division, Soldotna, Alaska.

Report: https://evostc.state.ak.us/media/2176/2004-040670-final.pdf
Project description: https://evostc.state.ak.us/restoration-projects/project-search/monitoring-dynamics-of-the-alaska-coastal-current-and-development-of-applications-for-management-of-cook-inlet-salmon-040670/



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("ctd_transects_otf_kbnerr"))
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
