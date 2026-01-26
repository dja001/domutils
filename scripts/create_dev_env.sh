#!/bin/bash

set -e

if [[ -z $1 ]] ; then
  read -p "Please write the name of the environment that will be created" env_name
else 
  env_name="$1"
fi

mamba create -n ${env_name} -y \
    numpy scipy attrdict cartopy matplotlib dask \
    pytest pytest-timeout pytest-cov \
    pysteps h5py pygrib cairosvg \
    sphinx sphinx_rtd_theme sphinx-gallery \
    sphinx-autodoc-typehints sphinx-argparse \
    packaging twine -c conda-forge

mamba run -n ${env_name} pip install -e ../domcmc_package
mamba run -n ${env_name} pip install -e .

./scripts/edit_pysteprc.sh mamba ${env_name}
