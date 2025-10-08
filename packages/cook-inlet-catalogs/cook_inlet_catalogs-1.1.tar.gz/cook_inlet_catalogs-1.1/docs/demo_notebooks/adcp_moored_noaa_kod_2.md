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

# Moored ADCP (NOAA): ADCP survey Kodiak Island, Set 2

Moored NOAA ADCP surveys in Cook Inlet

ADCP data has been converted to eastward, northward velocities as well as along- and across-channel velocities, in the latter case using the NOAA-provided rotation angle for the rotation. The along- and across-channel velocities are additionally filtered to show the subtidal signal, which is what is plotted in the dataset page.



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("adcp_moored_noaa_kod_2"))
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
