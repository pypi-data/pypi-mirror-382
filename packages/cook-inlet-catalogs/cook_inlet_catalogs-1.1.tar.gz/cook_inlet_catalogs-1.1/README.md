cook-inlet-catalogs
===================
[![License:MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://img.shields.io/readthedocs/cook-inlet-catalogs/latest.svg?style=for-the-badge)](https://cook-inlet-catalogs.readthedocs.io/en/latest/?badge=latest)


Intake catalogs of datasets from Cook Inlet, AK

--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>


Contained in this repository are catalogs to make it easy to access data for a variety of ocean data in Cook Inlet, Alaska. Data types are:

* Moored ADCP
* CTD profiles
* Underway CTD
* Towed CTD
* Drifters
* HF Radar
* Moorings

Data is from other sources and is accessed from original sources when possible with as much information as we could gather.

Catalogs are in `cook_inlet_catalogs/catalogs` and have been run without `fsspec`'s `simplecache` turned on, however, the `generate catalogs.py` script can be rerun locally with a flag turned on to use the `simplecache`. 

Demonstration notebooks for each catalog are available in the docs, showing all data locations as well as one sample dataset and a plot of that dataset. These files can be downloaded locally in the repository and run locally to examine other datasets. They are [MyST Markdown](https://mystmd.org/) but can be converted to Jupyter notebooks with [Jupytext](https://github.com/mwouts/jupytext).


Axiom Data Science, AK