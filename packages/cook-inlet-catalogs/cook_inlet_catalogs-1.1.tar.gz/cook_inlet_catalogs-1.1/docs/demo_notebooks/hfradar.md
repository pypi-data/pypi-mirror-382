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

# HF Radar (UAF)

HF Radar from UAF.

Files are:

* Upper Cook Inlet (System A): 2002-2003 and 2009
* Lower Cook Inlet (System B): 2006-2007

Data variables available include tidally filtered and weekly averaged along with tidal constituents calculated from hourly data.
    
Some of the data is written up in reports:

* https://espis.boem.gov/final%20reports/5009.pdf
* https://www.govinfo.gov/app/details/GOVPUB-I-47b721482d69e308aec1cca9b3e51955

![pic](https://researchworkspace.com/files/40338104/UAcoverage.gif)



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("hfradar"))
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
