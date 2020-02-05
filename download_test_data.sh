#!/bin/bash

set -v

#this script downloads a given version of the test data from zenodo repository


#get doi for the test data associated with this version of domutils
#DOI will be 10.5281/zenodo.${record_number}
#
record_number=3642234


function download 
{
    #get data from zenodo
    filename=$1
    wget https://zenodo.org/record/${record_number}/files/${filename}
}

#make directory for test data and go inside
mkdir -p test_data
cd test_data

#download files
file_list=(goes_gpm_data.pickle
           pal_demo_data.pickle
           radar_continental_2.5km_2882x2032.pickle)
for this_file in ${file_list[@]} ; do
    download $this_file
done

#download and untar tarballs
arch_list=(odimh5_radar_composites.tgz
           std_radar_mosaics.tgz)
for this_file in ${arch_list[@]} ; do
    download $this_file
    tar -xvf $this_file
    rm -f $this_file
done

#download images and put a copy in docs/
download _static.tgz
tar -xvf _static.tgz
rm -f _static.tgz
cp -rf _static ../docs/

set +v


