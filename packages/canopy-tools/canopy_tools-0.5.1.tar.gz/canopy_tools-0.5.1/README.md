[![Python Versions](https://img.shields.io/pypi/pyversions/canopy-tools.svg)](https://www.python.org/downloads/release/python-31210/)
[![pipeline status](https://codebase.helmholtz.cloud/canopy/canopy/badges/main/pipeline.svg)](https://codebase.helmholtz.cloud/canopy/canopy/-/pipelines)
[![Docs Status](https://readthedocs.org/projects/canopy-tools/badge/?version=stable)](https://canopy-tools.readthedocs.io/en/stable/?badge=stable)
[![PyPI Latest Release](https://img.shields.io/pypi/v/canopy-tools.svg)](https://pypi.org/project/canopy-tools/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/canopy-tools.svg?label=PyPI%20downloads)](https://pypi.org/project/canopy-tools/)

<img src="https://codebase.helmholtz.cloud/canopy/canopy/-/raw/main/docs/_static/canopylogo_small.png" alt="Canopy Logo" width="300" height="auto">

**canopy** is an open source python project designed to support research in the field of vegetation dynamics and climate modelling by providing tools for **analysing** and **visualising** Dynamic Global Vegetation Model (**DGVM**) **outputs**. 

# Installation

```bash
# Create a conda environment (optionnal)
conda create --name canopy python=3.12
conda activate canopy

# Use conda-forge to install canopy
conda install canopy-tools --channel conda-forge

# ... or pip
pip install canopy-tools
```

# Documentation

You can find the canopy documentation on [canopy-tools.readthedocs.io](https://canopy-tools.readthedocs.io/en/stable/)

### How to use

You can use canopy in two modes:

- [Interactive mode](https://canopy-tools.readthedocs.io/en/latest/quick_start.html#interactive-mode), an intuitive and flexible mode, to analyse data and generate figures using python functions.

- [JSON mode](https://canopy-tools.readthedocs.io/en/latest/quick_start.html#json-mode), a easy-to-use and fast mode, to generate figures using a structured JSON configuration file.

### Technical documentation

- [Spatial Reduction Operations](https://canopy-tools.readthedocs.io/en/latest/technical_documentation.html#spatial-reduction-operations)

# Issue, questions or suggestions

If you find any bug, please report it on our [github issues](https://codebase.helmholtz.cloud/canopy/canopy/-/issues).

If you have any questions or suggestions, you can also reach the cano**py** community through [our mattermost](https://mattermost.imk-ifu.kit.edu/lpj-guess/channels/canopy---help-desk).

# Authors

This project is being developed by David M. Belda & Adrien Damseaux from the [Global Land Ecosystem Modelling Group](https://lemg.imk-ifu.kit.edu/) at the [Karlsruhe Institute of Technology](https://www.kit.edu/).