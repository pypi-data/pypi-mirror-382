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

# CTD Transects (UAF): Repeated in central Cook Inlet

Observations of hydrography and currents in central Cook Inlet, Alaska during diurnal
and semidiurnal tidal cycles

Surface-to-bottom measurements of temperature, salinity, and transmissivity, as well as measurements of surface currents (vessel drift speeds) were acquired along an east-west section in central Cook Inlet, Alaska during a 26-hour period on 9-10 August 2003. These measurements are used to describe the evolution of frontal features (tide rips) and physical properties along this section during semidiurnal and diurnal tidal cycles. The observation that the amplitude of surface currents is a function of water depth is used to show that strong frontal features occur in association with steep bathymetry. The positions and strengths of these fronts vary with the semidiurnal tide. The presence of freshwater gradients alters the phase and duration of tidal currents across the section. Where mean density-driven flow is northward (along the eastern shore and near Kalgin Island), the onset of northward tidal flow (flood tide) occurs earlier and has longer duration than the onset and duration of northward tidal flow where mean density-driven flow is southward (in the shipping channel). Conversely, where mean density-driven flow is southward (in the shipping channel), the onset of southward tidal flow (ebb tide) occurs earlier and has longer duration than the onset and duration of southward tidal flow along the eastern shore and near Kalgin Island. 

Observations of hydrography and currents in central Cook Inlet, Alaska during diurnal
and semidiurnal tidal cycles
Stephen R. Okkonen
Institute of Marine Science
University of Alaska Fairbanks
Report: https://www.circac.org/wp-content/uploads/Okkonen_2005_hydrography-and-currents-in-Cook-Inlet.pdf



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("ctd_transects_uaf"))
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
