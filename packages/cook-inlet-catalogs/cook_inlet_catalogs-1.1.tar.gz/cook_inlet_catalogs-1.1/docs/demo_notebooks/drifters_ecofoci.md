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

# Drifters (EcoFOCI)

EcoFOCI Project.
        
As described on the [main project website for EcoFOCI](https://www.ecofoci.noaa.gov/):

> We study the ecosystems of the North Pacific Ocean, Bering Sea and U.S. Arctic to improve understanding of ecosystem dynamics and we apply that understanding to the management of living marine resources. EcoFOCI scientists integrate field, laboratory and modeling studies to determine how varying biological and physical factors influence large marine ecosystems within Alaskan waters.

> EcoFOCI is a joint research program between the Alaska Fisheries Science Center (NOAA/ NMFS/ AFSC) and the Pacific Marine Environmental Laboratory (NOAA/ OAR/ PMEL).

Drifter data are being pulled from this webpage: https://www.ecofoci.noaa.gov/drifters/efoci_drifterData.shtml which also has a plot available for each drifter dataset.

Several years of EcoFOCI drifter data are also available in a private Research Workspace project: https://researchworkspace.com/project/41531085/files.



```{code-cell}
cat = intake.open_catalog(cic.utils.cat_path("drifters_ecofoci"))
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
