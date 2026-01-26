#!/bin/bash

set -v

#this script downloads a given version of the test data from zenodo repository


#get doi for the test data associated with this version of domutils
#DOI will be 10.5281/zenodo.${record_number}
#
#v1.1.1
record_number=18380236

# this function takes one argument for downloading only the _static directory
if [[ "$1" = "figures_only" ]] ; then
    # download only the static directory
    figures_only=true
else
    # download everything
    figures_only=false
fi

function download 
{
    #get data from zenodo
    filename=$1
    wget https://zenodo.org/record/${record_number}/files/${filename}
}

#make directory for test data and go inside
mkdir -p test_data
cd test_data

# reference figures always get downloaded
arch_list=(reference_figures.tgz)
for this_file in ${arch_list[@]} ; do
    download $this_file
    tar -xvf $this_file
done

if [[ $figures_only = true ]] ; then
  # copy reference figures to docs
  rm -rf ../docs/_static
  cp -rf ../test_data/reference_figures ../docs/_static

else
    # download all files needed for running the tests

    #download all files
    file_list=(hrdps_5p1_prp0.fst
               prepare_tgz_for_zenodo.sh
               tarsum.py
               radar_continental_2.5km_2882x2032.pickle
               goes_gpm_data.pickle
               pal_demo_data.pickle)
    for this_file in ${file_list[@]} ; do
        download $this_file
    done
    
    #download and untar tarballs
    arch_list=(odimh5_radar_composites.tgz
               sqlite_radar_volume_scans.tgz
               mrms_grib2.tgz
               stage4_composites.tgz
               odimh5_radar_volume_scans.tgz
               std_radar_mosaics.tgz)
    for this_file in ${arch_list[@]} ; do
        download $this_file
        tar -xvf $this_file
    done
    
    
    #download test_results and make a copy in package root
    download test_results.tgz
    tar -xvf test_results.tgz
    cp -rf test_results ../

fi

set +v


