import subprocess
import nbformat as nbf
import cook_inlet_catalogs as cic
from pathlib import Path
import intake
import hvplot.xarray

imports = f"""\
import intake
import hvplot.pandas
import hvplot.xarray
import cook_inlet_catalogs as cic
import holoviews as hv
"""

def write_nb(slug):

    nb = nbf.v4.new_notebook()
    
    cat = intake.open_catalog(cic.utils.cat_path(slug))
# Click here to run this notebook in Binder, a hosted environment: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/axiom-data-science/cook-inlet-catalogs/HEAD?labpath=docs%2Fdemo_notebooks%2F{slug}.md)

    text = f"""\
# {cat.metadata['overall_desc']}

{cat.metadata['summary']}

"""

    imports_cell = nbf.v4.new_code_cell(imports)
    text_cell = nbf.v4.new_markdown_cell(text)
    nb['cells'] = [imports_cell, text_cell]
    
    code = f"""\
cat = intake.open_catalog(cic.utils.cat_path("{slug}"))"""
    code_cell = nbf.v4.new_code_cell(code)

    nb['cells'] += [code_cell]
    
    text = f"""\
## Plot all datasets in catalog
"""
    text_cell = nbf.v4.new_markdown_cell(text)

    code = f"""\
dd, ddlabels = cic.utils.combine_datasets_for_map(cat)
dd.hvplot(**cat.metadata["map"]) * ddlabels.hvplot(**cat.metadata["maplabels"])
"""
    code_cell = nbf.v4.new_code_cell(code)
    nb['cells'] += [text_cell, code_cell]

    
    text = f"""\
## List available datasets in the catalog
"""
    text_cell = nbf.v4.new_markdown_cell(text)

    code = f"""\
dataset_ids = list(cat)
dataset_ids
"""
    code_cell = nbf.v4.new_code_cell(code)
    nb['cells'] += [text_cell, code_cell]

    
    text = f"""\
## Select one dataset to investigate
"""
    text_cell = nbf.v4.new_markdown_cell(text)

    code = f"""\
try:
    dataset_id = dataset_ids[2]
except:
    dataset_id = dataset_ids[0]
print(dataset_id)

dd = cat[dataset_id].read()
dd
"""
    code_cell = nbf.v4.new_code_cell(code)
    nb['cells'] += [text_cell, code_cell]

    
    text = f"""\
## Plot one dataset
"""
    text_cell = nbf.v4.new_markdown_cell(text)

    # dynamic should be True to use in notebooks but False for when compiling for docs
    # have to change this in the metadata
    code = """\
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
"""

    code_cell = nbf.v4.new_code_cell(code)
    nb['cells'] += [text_cell, code_cell]
    
    nbf.write(nb, f'demo_notebooks/{slug}.ipynb')

    # Run jupytext command
    subprocess.run(["jupytext", "--to", "myst", f'demo_notebooks/{slug}.ipynb'])

if __name__ == "__main__":
    base_dir = Path("demo_notebooks")
    
    for slug in cic.slugs:
        # if not (base_dir / f"{slug}.ipynb").is_file():
        print(slug)
        write_nb(slug)