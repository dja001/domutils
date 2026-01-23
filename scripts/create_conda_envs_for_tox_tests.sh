#!/bin/bash

set -e

mamba=/fs/homeu2/eccc/mrd/rpndat/dja001/mambaforge/bin/mamba

common_pkgs="scipy attrdict dask \
tox pytest pytest-timeout pytest-cov pysteps \
h5py pygrib cairosvg \
sphinx sphinx-rtd-theme sphinx-gallery sphinx-autodoc-typehints sphinx-argparse"


## Environment 1: Minimum Requirements (2021-2022 era)
#mamba create -n toxtest_py39 python=3.9 numpy=1.21.5 cartopy=0.19.0.post1 matplotlib=3.3.4 ${common_pkgs} -c conda-forge -y

# Python 3.10 transition (2022 era)
mamba create -n toxtest_py310 python=3.10 numpy=1.23.5 cartopy=0.20.3 matplotlib=3.5.3 ${common_pkgs} -c conda-forge -y

## Python 3.11 early adoption (2023 era)
#mamba create -n toxtest_py311 python=3.11 numpy=1.24.3 cartopy=0.21.1 matplotlib=3.7.2 ${common_pkgs} -c conda-forge -y
#
## Python 3.11 mature (2023-2024 era)
#mamba create -n toxtest_py311b python=3.11 numpy=1.26.4 cartopy=0.22.0 matplotlib=3.8.0 ${common_pkgs} -c conda-forge -y
#
## Python 3.12 (2024 era)
#mamba create -n toxtest_py312 python=3.12 numpy=1.26.4 cartopy=0.23.0 matplotlib=3.8.4 ${common_pkgs} -c conda-forge -y
#
## Python 3.13 (late 2024-early 2025)
#mamba create -n toxtest_py313 python=3.13 numpy=2.1.0 cartopy=0.24.0 matplotlib=3.10.8 ${common_pkgs} -c conda-forge -y
#
## Pysteps not yet available here
## Python 3.14 bleeding edge (2025+)
#mamba create -n toxtest_py314 python=3.14 numpy cartopy matplotlib ${common_pkgs} -c conda-forge -y
