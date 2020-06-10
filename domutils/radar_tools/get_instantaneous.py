from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def get_instantaneous(valid_date:       Optional[Any]   = None,
                      data_path:        Optional[str]   = None,
                      data_recipe:      Optional[str]   = None,
                      desired_quantity: Optional[str]   = None,
                      median_filt:      Optional[int]   = None,
                      coef_a:           Optional[float] = None,
                      coef_b:           Optional[float] = None,
                      qced:             Optional[bool]  = True,
                      missing:          Optional[float] = -9999.,
                      latlon:           Optional[bool]  = False,
                      dest_lon:         Optional[Any]   = None,
                      dest_lat:         Optional[Any]   = None,
                      average:          Optional[bool]  = False,
                      nearest_time:     Optional[float] = None,
                      smooth_radius:    Optional[float] = None,
                      odim_latlon_file: Optional[str]   = None,
                      verbose:          Optional[int]   = 0):
    """ Get instantaneous precipitation from various sources

    Provides one interface 
    for:
        - support of Odim h5 composites and URP composites in the standard format
        - output to an arbitrary output grid
        - Consistent median filter on precip observations and the accompanying quality index
        - Various types of averaging 
        - Find the nearest time where observations are available


    The file extension present in *data_recipe* determines the file type of the source data
    Files having no extension are assumed to be in the 'standard' file format

    Args:

        valid_date:       datetime object with the validity date of the precip field
        data_path:        path to directory where data is expected
        data_recipe:      datetime code for constructing the file name  eg: /%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
                          the filename will be obtained with  data_path + valid_date.strftime(data_recipe)
        desired_quantity: What quantity is desired in output dictionary
                          *precip_rate* in [mm/h] and *reflectivity* in [dBZ]
                           are supported
        median_filt:       If specified, a median filter will be applied on the data being read and the associated
                           quality index.
                           eg. *medialFilter=3* will apply a median filter over a 3x3 boxcar
                           If unspecified, no filtering is applied
        coef_a:            Coefficient *a* in Z = aR^b
        coef_b:            Coefficient *b* in Z = aR^b
        qced:              Only for Odim H5 composites
                           When True (default), Quality Controlled reflectivity (DBZH) will be returned.
                           When False, raw reflectivity (TH) will be returned.
        missing:           Value that will be assigned to missing data
        latlon:            Return *latitudes* and *longitudes* grid of the data
        dest_lon:          Longitudes of destination grid. If not provided data is returned on its original grid
        dest_lat:          Latitudes  of destination grid. If not provided data is returned on its original grid
        average:           Use the averaging method to interpolate data (see geo_tools documentation), this can be slow
        nearest_time:      If set, rewind time until a match is found to an integer number of *nearestTime*
                           For example, with nearestTime=10, time will be rewinded to the nearest integer of 10 minutes
        smooth_radius:     Use the smoothing radius method to interpolate data, faster (see geo_tools documentation)
        odim_latlon_file:  file containing the latitude and longitudes of Baltrad mosaics in Odim H5 format
        verbose:           Set >=1 to print info on execution steps

    Returns:

        None               If no file matching the desired time is found

        or

        {

        'reflectivity'        2D reflectivity on destination grid (if requested)

        'precip_rate'         2D reflectivity on destination grid (if requested)

        'total_quality_index' Quality index of data with 1 = best and 0 = worse

        'valid_date'          Actual validity date of data

        'latitudes'           If latlon=True

        'longitudes'          If latlon=True

        }



    """

    import os
    import datetime
    import copy
    import numpy as np
    from . import read_h5_composite
    from . import read_fst_composite
    from . import exponential_zr
    from . import median_filter
    #import geo_tools from parent module
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import domutils.geo_tools as geo_tools


    #defaut time is now
    if valid_date is None:
        valid_date = datetime.datetime()

    if verbose >= 1 :
        print('get_instantaneous, getting data for: ', valid_date)

    #default coefficients for Z-R
    if coef_a is None:
        coef_a = 300
    if coef_b is None:
        coef_b = 1.4

    #default data path and recipe point to operational h5 outputs
    if data_path is None:
        data_path = '/space/hall2/sitestore/eccc/cmod/prod/hubs/radar/BALTRAD/Outcoming/Composites'
    if data_recipe is None:
        data_recipe = '/%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'

    #defaut value for desired quantity
    if desired_quantity is None:
        desired_quantity = 'reflectivity'
    elif desired_quantity == 'reflectivity':
        pass
    elif desired_quantity == 'precip_rate':
        pass
    else:
        raise ValueError('Wrong value in desired_quantity ')

    #define settings if interpolation to a destination grid is needed
    interpolate=False
    require_precip_rate = False
    if dest_lon is not None and dest_lat is not None:
        interpolate=True
        latlon=True

        #if any kind of averaging is to be done we need precipitation rates
        if average or smooth_radius is not None:
            require_precip_rate = True


    #
    #
    #rewind clock if nearest time is required
    this_time = copy.deepcopy(valid_date)
    #rewind time if necessary 
    if nearest_time is not None:
        try : 
            minutes = this_time.minute
        except :
            raise ValueError('Could get minute from datetime object valid_date*')

        for tt in np.arange(0, np.float(nearest_time)):
            this_time = valid_date - datetime.timedelta(minutes=tt)
            minutes = this_time.minute
            remainder = np.mod(minutes, nearest_time)
            if np.isclose(remainder, 0.):
                break


    #
    #
    #make filename from recipe
    try : 
        this_file_name = this_time.strftime(data_recipe)
    except :
        raise ValueError('Could not build filename from datetime object')
    #complete filename of data file to read
    data_file = data_path + this_file_name


    #
    #
    #read data based on extension
    name, ext = os.path.splitext(data_recipe)
    if ext == '.h5':
        #
        #
        #ODIM H5 format
        out_dict = read_h5_composite(data_file,
                                     qced=qced,
                                     latlon=latlon,
                                     verbose=verbose,
                                     latlon_file=odim_latlon_file)
    elif (ext == '.std'  or 
          ext == '.stnd'  or
          ext == '.fst'   or
          ext == '') :

        #
        #
        #CMC *standard* format
        out_dict = read_fst_composite(data_file,
                                      latlon=latlon,
                                      verbose=verbose)

    else:
        raise ValueError('Filetype: '+ext+' not yet supported')

    #return None if nothing was returned by reader
    if out_dict is None:
        return None


    #
    #
    #perform conversion if necessary
    if desired_quantity == 'reflectivity' :
        if 'reflectivity' not in out_dict:
            #conversion from R to dBZ
            try: 
                out_dict['reflectivity'] = exponential_zr(out_dict['precip_rate'],
                                                          coef_a=coef_a, coef_b=coef_b,
                                                          r_to_dbz=True)
            except:
                raise ValueError('Could not convert precip rate to reflectivity')

    if desired_quantity == 'precip_rate' or require_precip_rate :
        if 'precip_rate' not in out_dict:
            #conversion from R to dBZ
            try: 
                out_dict['precip_rate'] = exponential_zr(out_dict['reflectivity'],
                                                       coef_a=coef_a, coef_b=coef_b,
                                                       dbz_to_r=True)
            except:
                raise ValueError('Could not convert precip rate to reflectivity')


    #
    #
    #remove speckle with median filter if desired
    if median_filt is not None:
        #speckle filter will be applied from precip_rate or reflectivity
        #the same pixel selection is applied to quality indexes 

        if verbose >= 1 :
            print('get_instantaneous, applying median filter')

        if 'reflectivity' in out_dict:
            median_inds = median_filter.get_inds(out_dict['reflectivity'], window=median_filt)
            out_dict['reflectivity'] = median_filter.apply_inds(out_dict['reflectivity'], median_inds)
            if 'precip_rate' in out_dict:
                out_dict['precip_rate'] = median_filter.apply_inds(out_dict['precip_rate'], median_inds)

        elif 'precip_rate' in out_dict:
             median_inds = median_filter.get_inds(out_dict['precip_rate'], window=median_filt)
             filtered_pr = median_filter.apply_inds(out_dict['precip_rate'], median_inds)
             out_dict['precip_rate']        = filtered_pr
        else:
            raise ValueError('One of reflectivity or precip_rate must be present for filtering')

        #quality index should always be in dict
        out_dict['total_quality_index'] = median_filter.apply_inds(out_dict['total_quality_index'], median_inds)


    #
    #
    #perform interpolation if necessary
    if interpolate:

        if verbose >= 1 :
            print('get_instantaneous, interpolating to destination grid')

        #projection from one grid to another
        proj_obj = geo_tools.ProjInds(src_lon=out_dict['longitudes'], src_lat=out_dict['latitudes'],
                                      dest_lon=dest_lon, dest_lat=dest_lat,
                                      average=average, smooth_radius=smooth_radius,
                                      missing=missing)
        interpolated_pr  = None
        interpolated_ref = None
        if average or smooth_radius is not None:
            #interpolation involving some averaging
            interpolated_pr = proj_obj.project_data(out_dict['precip_rate'],         weights=out_dict['total_quality_index'])
            interpolated_qi = proj_obj.project_data(out_dict['total_quality_index'], weights=out_dict['total_quality_index'])
            #if reflectivity is present get it from interpolated precip Rate
            if 'reflectivity' in out_dict:
                interpolated_ref = exponential_zr(interpolated_pr,
                                                  coef_a=coef_a, coef_b=coef_b,
                                                  r_to_dbz=True)
        else :
            #interpolation by nearest neighbor
            interpolated_qi = proj_obj.project_data(out_dict['total_quality_index'])
            if 'precip_rate' in out_dict:
                interpolated_pr =  proj_obj.project_data(out_dict['precip_rate'])
            if 'reflectivity' in out_dict:
                interpolated_ref = proj_obj.project_data(out_dict['reflectivity'])

        #update outdict
        out_dict['total_quality_index'] = interpolated_qi
        out_dict['latitudes']  = dest_lat
        out_dict['longitudes'] = dest_lon
        if interpolated_pr is not None:
            out_dict['precip_rate'] = interpolated_pr
        if interpolated_ref is not None:
            out_dict['reflectivity'] = interpolated_ref

        if verbose >= 1 :
            print('get_instantaneous, interpolation done')

    return out_dict

    def main():
        pass

    if __name__ == "__main__":
        main()
