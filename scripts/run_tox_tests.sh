#!/bin/bash

set -e

mamba=/space/hall7/sitestore/eccc/mrd/rpnad/dja001/mambaforge/bin/mamba

# Test all versions
for PY_VER in 39 310 311 311b 312 313 ; do
    echo Processing "$PY_VER"
    ${mamba} run -n toxtest_py${PY_VER} tox -e py${PY_VER}
done

### Or individual
#PY_VER='313'
#${mamba} run -n toxtest_py${PY_VER} tox -e py${PY_VER}
