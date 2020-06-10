from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def get_accumulation(end_date:         Optional[Any]   = None,
                     duration:         Optional[Any]   = None,
                     desired_quantity: Optional[str]   = None,
                     data_path:        Optional[str]   = None,
                     data_recipe:      Optional[str]   = None,
                     median_filt:      Optional[int]   = None,
                     coef_a:           Optional[float] = None,
                     coef_b:           Optional[float] = None,
                     qced:             Optional[bool]  = True,
                     missing:          Optional[float] = -9999.,
                     latlon:           Optional[bool]  = False,
                     dest_lon:         Optional[Any]   = None,
                     dest_lat:         Optional[Any]   = None,
                     average:          Optional[bool]  = False,
                     nearest:          Optional[float] = None,
                     smooth_radius:    Optional[float] = None,
                     odim_latlon_file: Optional[str]   = None,
                     verbose:          Optional[int]   = 0):

    """Get accumulated precipitation from instantaneous observations

    This is essentially a wrapper around get_instantaneous.
    Data is read during the accumulation period and accumulated (in linear units of 
    precipitation rates) taking the quality index into account. 
    If interpolation to a different grid is desired, it is performed after the 
    accumulation procedure. 

    If the desired quantity *reflectivity* or *precip_rate* is desired, then the
    returned quantity will reflect the average precipitation rate during the accumulation 
    period.

    With an endTime set to 16:00h and duration to 60 (minutes), 
    data from:
        - 15:10h, 15:20h, 15:30h, 15:40h, 15:50h and 16:00h
    will be accumulated 

    Args:

        end_date:         datetime object representing the time (inclusively) at the end of the accumulation period
        duration:         amount of time (minutes) during which precipitation should be accumulated
                            
        data_path:        path to directory where data is expected
        data_recipe:      datetime code for constructing the file name  eg: /%Y/%m/%d/qcomp_%Y%m%d%H%M.h5'
                          the filename will be obtained with  data_path + valid_date.strftime(data_recipe)
        desired_quantity: What quantity is desired in output dictionary.
                          Supported values are:
                            - *accumulation*  Default option, the amount of water (in mm) 
                            - *avg_precip_rate* For average precipitation rate (in mm/h) during the accumulation period
                            - *reflectivity*  For the reflectivity (in dBZ) associated with the average precipitation rate
        median_filt:      If specified, a median filter will be applied on the data being read and the associated
                          quality index.
                          eg. *medialFilter=3* will apply a median filter over a 3x3 boxcar
                          If unspecified, no filtering is applied
        coef_a:           Coefficient *a* in Z = aR^b
        coef_b:           Coefficient *b* in Z = aR^b
        qced:             Only for Odim H5 composites
                          When True (default), Quality Controlled reflectivity (DBZH) will be returned.
                          When False, raw reflectivity (TH) will be returned.
        missing:          Value that will be assigned to missing data
        latlon:           Return *latitudes* and *longitudes* grid of the data
        dest_lon:         Longitudes of destination grid. If not provided data is returned on its original grid
        dest_lat:         Latitudes  of destination grid. If not provided data is returned on its original grid
        average:          Use the averaging method to interpolate data (see geo_tools documentation), this can be slow
        nearest:          If set, rewind time until a match is found to an integer number of *nearest*
                          For example, with nearest=10, time will be rewinded to the nearest integer of 10 minutes
        smooth_radius:    Use the smoothing radius method to interpolate data, faster (see geo_tools documentation)
        odim_latlon_file: file containing the latitude and longitudes of Baltrad mosaics in Odim H5 format
        verbose:          Set >=1 to print info on execution steps

    Returns:
        None              If no file matching the desired time is found

        or

        {

        'end_date'              End time for accumulation period

        'duration'              Accumulation length (minutes)

        'reflectivity'          2D reflectivity on destination grid (if requested)

        'precip_rate'           2D reflectivity on destination grid (if requested)

        'total_quality_index'   Quality index of data with 1 = best and 0 = worse


        'latitudes'             If latlon=True

        'longitudes'            If latlon=True

        }



    """

    global orig_lat
    import os
    import datetime
    import numpy as np
    from .  import get_instantaneous
    from .  import exponential_zr
    #import geo_tools from parent module
    import os, sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    import domutils.geo_tools as geo_tools

    if verbose >= 1 :
        print('get_accumulation starting')

    #define settings if interpolation to a destination grid is needed
    #for better performance, interpolation will be performed only once
    #data has been accumulated on its original grid
    interpolate=False
    if dest_lon is not None and dest_lat is not None:
        interpolate=True
        latlon=True

    #defaut time is now
    if end_date is None:
        end_date = datetime.datetime()

    #defaut duration is 1h
    if duration is None:
        duration = 60.

    #default coefficients for Z-R
    if coef_a is None:
        coef_a = 300
    if coef_b is None:
        coef_b = 1.4

    #defaut value for desired quantity
    if desired_quantity is None:
        desired_quantity   = 'accumulation'
    elif desired_quantity == 'accumulation':
        pass
    elif desired_quantity == 'avg_precip_rate':
        pass
    elif desired_quantity == 'reflectivity':
        pass
    else:
        raise ValueError('Wrong value in desired_quantity ')

    #start filling out output dictionary
    out_dict = {'end_date':   end_date,
                'duration':   duration }


    #time interval between radar observations
    name, ext = os.path.splitext(data_recipe)
    if ext == '.h5':
        radar_dt = 10.
    else:
        raise ValueError('Filetype: '+ext+' not yet supported')
    

    #
    #
    #get list of times during which observations should be accumulated
    m_list = np.arange(0, duration, radar_dt)
    date_list = [end_date - datetime.timedelta(minutes=this_min) for this_min in m_list]


    #
    #
    #read data
    #for 1st time
    kk = 0
    this_date = date_list[kk]
    dat_dict = get_instantaneous(desired_quantity='precip_rate',
                                 valid_date=this_date,
                                 data_path=data_path,
                                 odim_latlon_file=odim_latlon_file,
                                 data_recipe=data_recipe,
                                 median_filt=median_filt,
                                 latlon=latlon,
                                 verbose=verbose)
    data_shape = dat_dict['precip_rate'].shape
    if latlon is not None:
        orig_lat = dat_dict['latitudes']
        orig_lon = dat_dict['longitudes']
    #init accumulation arrays
    accum_dat = np.full( (data_shape[0], data_shape[1], len(date_list)), missing)
    accum_qi  = np.zeros((data_shape[0], data_shape[1], len(date_list)))
    #save data
    accum_dat[:,:,kk] = dat_dict['precip_rate']
    accum_qi[:,:,kk]  = dat_dict['total_quality_index']
    #
    #read rest of data
    for kk, this_date in enumerate(date_list):
        #we already did the 1st one, skip it
        if kk == 0 :
            continue

        #fill accumulation arrays with data for this time
        dat_dict = get_instantaneous(desired_quantity='precip_rate',
                                     valid_date=this_date,
                                     data_path=data_path,
                                     odim_latlon_file=odim_latlon_file,
                                     data_recipe=data_recipe,
                                     median_filt=median_filt,
                                     verbose=verbose)
        if dat_dict is not None:
            accum_dat[:,:,kk] = dat_dict['precip_rate']
            accum_qi[:,:,kk]  = dat_dict['total_quality_index']


    #
    #
    #average of precip_rate is weighted by quality index
    if verbose >= 1 :
        print('get_accumulation, computing average precip rate in accumulation period')
    sum_w  = np.sum(accum_qi, axis=2)
    good_pts = np.asarray(sum_w > 0.).nonzero()
    #
    #average precip_rate
    weighted_sum = np.sum(accum_dat*accum_qi, axis=2)
    avg_pr = np.full_like(sum_w, missing)
    if good_pts[0].size > 0:
        avg_pr[good_pts] = weighted_sum[good_pts]/sum_w[good_pts]
    #
    #compute average quality index
    weighted_sum = np.sum(accum_qi*accum_qi, axis=2)
    avg_qi = np.full_like(sum_w, missing)
    if good_pts[0].size > 0:
        avg_qi[good_pts] = weighted_sum[good_pts]/sum_w[good_pts]


    #
    #
    #perform interpolation if necessary
    if interpolate:
        if verbose >= 1 :
            print('get_accumulation, interpolating to destination grid')

        #projection from one grid to another
        proj_obj = geo_tools.ProjInds(src_lon=orig_lon,  src_lat=orig_lat,
                                      dest_lon=dest_lon, dest_lat=dest_lat,
                                      average=average,   smooth_radius=smooth_radius,
                                      missing=missing)
        if average or smooth_radius is not None:
            #interpolation involving some averaging
            interpolated_pr = proj_obj.project_data(avg_pr, weights=avg_qi)
            interpolated_qi = proj_obj.project_data(avg_qi, weights=avg_qi)
        else :
            #interpolation by nearest neighbor
            interpolated_pr = proj_obj.project_data(avg_pr)
            interpolated_qi = proj_obj.project_data(avg_qi)

        #fill out_dict
        out_dict['avg_precip_rate']     = interpolated_pr
        out_dict['total_quality_index'] = interpolated_qi
        out_dict['latitudes']           = dest_lat
        out_dict['longitudes']          = dest_lon
    else:
        #no Interpolation 
        out_dict['avg_precip_rate']     = avg_pr
        out_dict['total_quality_index'] = avg_qi
        if latlon:
            out_dict['latitudes']     = orig_lat
            out_dict['longitudes']    = orig_lon


    #
    #
    #convert precip rates to other quantities if desired
    if desired_quantity == 'accumulation':
        if verbose >= 1 :
            print('get_accumulation computing accumulation from avg precip rate')
        # rate (mm/h) * duration time (h) = accumulation (mm)
        #number of hours of accumulation period
        duration_hours = duration/60.
        out_dict['accumulation'] = out_dict['avg_precip_rate'] * duration_hours
    #
    if desired_quantity == 'reflectivity':
        if verbose >= 1 :
            print('get_accumulation computing reflectivity from avg precip rate')
        out_dict['reflectivity'] = exponential_zr(out_dict['avg_precip_rate'],
                                                  coef_a=coef_a, coef_b=coef_b,
                                                  r_to_dbz=True)

    if verbose >= 1 :
        print('get_accumulation done')
    return out_dict





