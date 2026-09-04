#!/bin/bash

#this script downloads a given version of the test data from zenodo repository
#
#usage:
#   ./download_test_data.sh
#       download the complete test data
#   ./download_test_data.sh figures_only
#       download only the reference figures
#   ./download_test_data.sh check
#       verify that the content of the test_data directory is identical to the
#       zenodo record associated with this version of domutils (same files,
#       same md5, nothing extra, nothing missing)
#
#files that are already present with the right md5 are not downloaded again

#get doi for the test data associated with this version of domutils
#DOI will be 10.5281/zenodo.${record_number}
#
#Version v13
record_number=22304314

#---------- arguments ----------

check_mode=false
if [[ "$1" = "check" ]] ; then
    check_mode=true
    shift
fi

if [[ "$1" = "figures_only" ]] ; then
    # download only the static directory
    figures_only=true
else
    # download everything
    figures_only=false
fi

#---------- zenodo file list for this record ----------

#map of file name -> md5 for all files in the zenodo record
declare -A zenodo_md5

#fetch the list of files (with their md5 checksums) from the zenodo api
api_output=$(wget -qO- https://zenodo.org/api/records/${record_number})
zenodo_file_map=$(printf '%s' "${api_output}" | python3 -c "
import json, sys

record = json.load(sys.stdin)
for file in record['files']:
    md5 = file.get('md5')
    if md5 is None :
        md5 = file['checksum'].split(':', 1)[1]
    print(file['key'], md5)
" 2>/dev/null)

if [[ -n ${zenodo_file_map} ]] ; then
    while IFS=' ' read -r file md5 ; do
        zenodo_md5[${file}]=${md5}
    done <<< "${zenodo_file_map}"
    echo "zenodo record #${record_number}# has ${#zenodo_md5[@]} files"
else
    echo "warning: could not retrieve the zenodo file list for record #${record_number}#"
fi

#---------- check mode ----------

if [[ ${check_mode} = true ]] ; then

    if [[ ${#zenodo_md5[@]} -eq 0 ]] ; then
        echo "error: could not retrieve the zenodo file list, cannot check test_data"
        exit 1
    fi

    if [[ ! -d test_data ]] ; then
        echo "error: test_data directory does not exist, run this script first to download it"
        exit 1
    fi

    cd test_data

    status=0

    #every file in the zenodo record must be present here, with the same md5
    for file in "${!zenodo_md5[@]}" ; do
        if [[ ! -f ${file} ]] ; then
            echo "missing:    ${file}"
            status=1
            continue
        fi
        local_md5=$(md5sum ${file} | cut -d' ' -f1)
        if [[ ${local_md5} != ${zenodo_md5[${file}]} ]] ; then
            echo "different:  ${file}"
            echo "             zenodo  ${zenodo_md5[${file}]}"
            echo "             local   ${local_md5}"
            status=1
        fi
    done

    #nothing extra: every top level entry must be a file from the record,
    #or the directory extracted from one of the record's tarballs
    for entry in * ; do
        if [[ -d ${entry} && -n ${zenodo_md5[${entry}.tgz]+x} ]] ; then
            continue
        fi
        if [[ -f ${entry} && -n ${zenodo_md5[${entry}]+x} ]] ; then
            continue
        fi
        echo "extra:      ${entry} (not in the zenodo record)"
        status=1
    done

    if [[ ${status} -eq 0 ]] ; then
        echo "Identical content in test_data and record #${record_number}# on zenodo"
        exit 0
    fi

    echo
    echo "test_data does not match record #${record_number}# on zenodo"
    echo "run ./scripts/download_test_data.sh to get the right data"
    exit 1
fi

#---------- download mode ----------

function download 
{
    #get data from zenodo, skipping files that are already present
    #with the same md5
    filename=$1

    if [[ -f ${filename} ]] ; then
        local_md5=$(md5sum ${filename} | cut -d' ' -f1)
        remote_md5=${zenodo_md5[${filename}]:-}
        if [[ -n ${remote_md5} && ${local_md5} == ${remote_md5} ]] ; then
            echo "skip ${filename} (md5 ${local_md5} matches zenodo)"
            return
        fi
    fi

    set -v
    wget -O ${filename}.new https://zenodo.org/record/${record_number}/files/${filename} || { rm -f ${filename}.new; exit 1; }
    mv ${filename}.new ${filename}
    set +v
}

#make directory for test data and go inside
mkdir -p test_data
cd test_data

# reference figures always get downloaded
arch_list=(reference_figures.tgz)
for this_file in ${arch_list[@]} ; do
    download $this_file
    set -v
    tar -xvf $this_file
    set +v
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
        set -v
        tar -xvf $this_file
        set +v
    done
    
    
    #download test_results and make a copy in package root
    download test_results.tgz
    set -v
    tar -xvf test_results.tgz
    set +v
    cp -rf test_results ../

fi
