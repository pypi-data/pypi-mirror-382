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

# Drifters (UAF)

Drifters run by Mark Johnson and others out of UAF with various years and drogue depths.
        
* 2003: 7.5m (Cook Inlet)
* 2004: 5m (Cook Inlet)
* 2005: 5m, 80m (Cook Inlet)
* 2006: 5m (Cook Inlet)
* 2012: 1m (Cook Inlet), 15m (Cook Inlet)
* 2013: 1m (Cook Inlet), 15m (Cook Inlet)
* 2014: 1m (Cook Inlet)
* 2019: 1m (Kachemak Bay, Lynn Canal)
* 2020: 1m (Kachemak Bay, Lynn Canal)

Descriptive summary of later drifter deployment: https://www.alaska.edu/epscor/about/newsletters/May-2022-feature-current-events.php, data portal: https://ak-epscor.portal.axds.co/



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("drifters_uaf"))
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
