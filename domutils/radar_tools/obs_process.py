
#identify logger names based on package hierarchy
import numpy as np
import dask
import dask.array 
import dask.distributed

def _setup_logging(args, is_worker=False, sub_dir=''):
    """setup logger and handlers

    Because of parallel execution, logging has to be setup for every forked processes
    so it is put in this reusable function
    """

    import sys 
    import logging
    import domutils._py_tools as dpy

    # logging is configured to write everything to stdout in addition to a log file
    # in a 'logs' directory
    logging_basename = 'domutils.radar_tools'
    logger = logging.getLogger(logging_basename)
    # if this is a newly created logger, it will have no handlers
    if not len(logger.handlers):
        #make sure 'logs' directory exists and is empty
        dpy.parallel_mkdir('logs')

        logging.captureWarnings(True)
        logger.setLevel(args.log_level)
        #handlers
        stream_handler = logging.StreamHandler(sys.stdout)
        if is_worker:
            dpy.parallel_mkdir('logs/'+sub_dir)
            worker_id = str(dask.distributed.get_worker().id)
            file_handler = logging.FileHandler('logs/'+sub_dir+'/'+worker_id, 'w')
        else:
            file_handler = logging.FileHandler('logs/obs_process.log', 'w')
        #levels
        stream_handler.setLevel(args.log_level)
        file_handler.setLevel(args.log_level)
        #format
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if is_worker:
            stream_formatter = logging.Formatter(worker_id+'    %(message)s')
        else:
            stream_formatter = file_formatter
        stream_handler.setFormatter(stream_formatter)
        file_handler.setFormatter(file_formatter)
        #add handlers
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger

def output_fst_file(args, this_time):
    import os
    return os.path.join(args.output_dir, this_time.strftime(args.output_file_struc))

def weighted_median_3d(values, weights, values2):
    """
    Compute column-wise weighted median along axis=2.
    NaN-safe: ignores entries where either values or weights are NaN.
    Returns array of shape (nx, ny).
    """
    import numpy as np

    # 1) Mask invalid entries
    mask = (~np.isnan(values)) & (~np.isnan(weights))

    # Replace invalid values so they do not affect sorting or sums
    values_masked  = np.where(mask, values,  np.inf)
    values2_masked = np.where(mask, values2, np.inf)
    weights_masked = np.where(mask, weights, 0.0)

    # 2) Sort by values along axis=2
    sorting_inds = np.argsort(values_masked, axis=2)

    sorted_values  = np.take_along_axis(values_masked,  sorting_inds, axis=2)
    sorted_values2 = np.take_along_axis(values2_masked, sorting_inds, axis=2)
    sorted_weights = np.take_along_axis(weights_masked, sorting_inds, axis=2)

    # 3) Compute cumulative weights
    cumsum = np.cumsum(sorted_weights, axis=2)

    total_weight = np.sum(sorted_weights, axis=2, keepdims=True)
    half_weight = total_weight / 2.0

    # 4) Find first index where cumulative weight >= half
    # If total_weight == 0, this will incorrectly return 0, so we fix below
    z_index = np.argmax(cumsum >= half_weight, axis=2)

    # 5) Extract weighted median
    weighted_median1 = np.take_along_axis(
        sorted_values,
        z_index[..., None],
        axis=2
    ).squeeze(axis=2)
    weighted_median2 = np.take_along_axis(
        sorted_values2,
        z_index[..., None],
        axis=2
    ).squeeze(axis=2)

    # 6) Handle columns with no valid weights
    weighted_median1 = np.where(total_weight.squeeze(axis=2) > 0,
                               weighted_median1,
                               -9999.)
    weighted_median2 = np.where(total_weight.squeeze(axis=2) > 0,
                               weighted_median2,
                               0.)

    return weighted_median1, weighted_median2

import numpy as np
from numba import njit, prange
@njit(parallel=True)
def weighted_median_3d_local3x3_numba(values, weights):
    nx, ny, nz = values.shape
    out = np.full((nx, ny), np.nan)

    # maximum possible pooled size = 9 * nz
    max_size = 9 * nz

    for i in prange(nx):

        for j in range(ny):

            # determine neighborhood bounds
            i0 = 0 if i == 0 else i - 1
            i1 = nx if i == nx - 1 else i + 2
            j0 = 0 if j == 0 else j - 1
            j1 = ny if j == ny - 1 else j + 2

            # temporary buffers
            v_buf = np.empty(max_size, dtype=np.float64)
            w_buf = np.empty(max_size, dtype=np.float64)

            n = 0

            # gather valid samples
            for ii in range(i0, i1):
                for jj in range(j0, j1):
                    for k in range(nz):
                        v = values[ii, jj, k]
                        w = weights[ii, jj, k]

                        if not np.isnan(v) and not np.isnan(w):
                            v_buf[n] = v
                            w_buf[n] = w
                            n += 1

            if n == 0:
                continue

            # slice to valid length
            v_valid = v_buf[:n]
            w_valid = w_buf[:n]

            total_weight = 0.0
            for t in range(n):
                total_weight += w_valid[t]

            if total_weight == 0.0:
                continue

            # sort by value
            order = np.argsort(v_valid)
            v_sorted = v_valid[order]
            w_sorted = w_valid[order]

            # cumulative sum until half weight
            half_weight = 0.5 * total_weight
            cumsum = 0.0

            for t in range(n):
                cumsum += w_sorted[t]
                if cumsum >= half_weight:
                    out[i, j] = v_sorted[t]
                    break

    return out

def serial_parallel_sumbit(this_function, args, dates_to_process):
    """ launch function in serial or in parallel depending on existence of dast_client

    """

    import time
    import glob
    from collections import Counter
    import dask
    from domcmc import fst_tools
    import copy

    #logging
    logger = _setup_logging(args)

    if args.dask_client is None :
        #serial execution
        logger.info(f'Launching SERIAL computation of {this_function.__name__}')
        results = []
        for tt, this_time in enumerate(dates_to_process):

            this_result = this_function(this_time, args)
            
            results.append(this_result) 

    else:
        #parallel execution
        logger.info(f'Launching PARALLEL computation of {this_function.__name__}')

        tt1 = time.time()

        # remove dask_client which is not serializable
        args_clean = copy.copy(args)
        for attr in ('dask_client',):  # fill in from the output above
            setattr(args_clean, attr, None)

        # Scatter large shared objects once to all workers
        args_future = args.dask_client.scatter(args_clean, broadcast=True)

        # Submit tasks directly — no dask.array wrapping needed
        futures = [
            args.dask_client.submit(this_function, this_date, args_future)
            for this_date in dates_to_process
        ]

        # Gather results (blocks until all done)
        results = args.dask_client.gather(futures)

        # Clean up scattered data before next computation
        args.dask_client.cancel([args_future])

        tt2 = time.time()
        logger.info(f'Parallel execution done; walltime: {tt2-tt1} seconds')

    # results is a list of (date, status) tuples
    dates, statuses = zip(*results)
    status_counts = Counter(statuses)
    for status, count in status_counts.items():
        logger.info(f'  {status}: {count} dates')


def perform_nowcast(args, t0, lead_time_s, proj_obj=None):

    import os
    import datetime
    import pysteps
    from domutils import radar_tools

    missing = -9999.
    logger = _setup_logging(args)

    # advection method
    extrapolate = pysteps.extrapolation.interface.get_method("semilagrangian")

    mv_time = t0 
    mv_file = args.motion_vectors_dir + mv_time.strftime('%Y%m%d%H%M_end_window.npz')
    if not os.path.isfile(mv_file):
        # dont do anything if mv file is not there
        logger.warning(f"{mv_file=} does not exist, we return empty interpolated precip and data")

        empty_precip  = np.full((args.out_nx, args.out_ny), np.nan)
        empty_quality = np.full((args.out_nx, args.out_ny), np.nan)
        return empty_precip, empty_quality

    try:
        mv_avg = np.load(mv_file)['uv_motion']
    except:
        logger.warning(f"Unable to read {mv_file=}, we return empty interpolated precip and data")

        empty_precip  = np.full((args.out_nx, args.out_ny), np.nan)
        empty_quality = np.full((args.out_nx, args.out_ny), np.nan)
        return empty_precip, empty_quality

    # get precip and qi to extrapolate
    desired_quantity='precip_rate'
    dat_dict = radar_tools.get_instantaneous(valid_date=t0,
                                             desired_quantity=desired_quantity,
                                             data_path=args.input_data_dir,
                                             odim_latlon_file=args.h5_latlon_file,
                                             data_recipe=args.input_file_struc,
                                             dest_lon=args.out_lons,
                                             dest_lat=args.out_lats,
                                             input_proj_obj=proj_obj,
                                             median_filt=args.nowcast_median_filt,
                                             smooth_radius=args.nowcast_smooth_radius) 
    #if we got nothing, fill output with nodata and zeros
    if dat_dict is None:
        logger.warning(f"Unable to get source precip in {args.input_data_dir} at {t0}, we return empty interpolated precip and data")

        empty_precip  = np.full((args.out_nx, args.out_ny), np.nan)
        empty_quality = np.full((args.out_nx, args.out_ny), np.nan)
        return empty_precip, empty_quality
    else:
        precip_rate     = np.transpose(dat_dict[desired_quantity])
        quality_index   = np.transpose(dat_dict['total_quality_index'])
        # Nans are better handled by extrapolate and no not lead to rigning artefacts
        precip_rate = np.where(np.isclose(precip_rate, missing), np.nan, precip_rate)
        quality_index = np.where(np.isclose(quality_index, missing), np.nan, quality_index)

    lead_time_arr = np.atleast_1d(lead_time_s)
    advected_precip  = np.full((args.out_nx, args.out_ny, lead_time_arr.size), np.nan)
    advected_quality = np.full((args.out_nx, args.out_ny, lead_time_arr.size), np.nan)

    # there can be many leadtimes for nowcast extrapolation at the end of a period
    for tt, this_leadtime in enumerate(lead_time_arr):

        # scale motion vectors
        scaling_factor = this_leadtime / args.input_dt
        uv_scaled = scaling_factor * mv_avg

        # advect precip and qi at appropriate time
        advected_precip[:,:,tt]  = np.squeeze( np.transpose(extrapolate(precip_rate,   uv_scaled, 1, interp_order=3, outval=np.nan, allow_nonfinite_values=True)) )
        advected_quality[:,:,tt] = np.squeeze( np.transpose(extrapolate(quality_index, uv_scaled, 1, interp_order=3, outval=np.nan, allow_nonfinite_values=True)) )

    # adjust missing values that could have been wrongfully modified during advection
    advected_precip  = np.where(advected_precip  < 0., np.nan, advected_precip)
    advected_quality = np.where(advected_quality < 0., np.nan, advected_quality)
    advected_quality = np.where(advected_quality > 1., 1., advected_quality)

    return np.squeeze(advected_precip), np.squeeze(advected_quality)


def _process_at_one_time(this_time, args):
    #output data to std file

    import os
    import time
    import copy
    import rpnpy.librmn.all as rmn
    from rpnpy.rpndate import RPNDate
    from domutils import radar_tools
    from domcmc import fst_tools
    import domutils._py_tools as dpy

    logger = _setup_logging(args)

    logger.info(f'_process_at_one_time starting to process date: {this_time}')

    #output filename 
    output_file = os.path.join(args.processed_data_dir, this_time.strftime(args.output_file_struc))
    # check if we need to process this date
    if os.path.isfile(output_file):
        # output file is there, check if data is there at this time. 
        pr = fst_tools.get_data(var_name='RDPR', file_name=output_file, datev=this_time)
        qi = fst_tools.get_data(var_name='RDQI', file_name=output_file, datev=this_time)
        if (pr is not None) and (qi is not None):
            if args.complete_dataset:
                logger.info(f'{output_file} exists, desired data is there and complete_dataset=True. Skipping to the next.')
                return this_time, 'skip'
            else:
                logger.info(f'{output_file} exists, and complete_dataset=False. We remove it and will rewrite it.')
                os.remove(output_file)
        else:
            logger.info(f'{output_file} exists and is incomplete, we remove it and rewrite it')
            os.remove(output_file)
    else:
        #we will create or overwrite the file; before that make sure directory exists
        this_fst_dir = os.path.dirname(output_file)
        dpy.parallel_mkdir(this_fst_dir)
    
    #reading the data
    if args.accum_len is not None:
        desired_quantity='accumulation'
        dat_dict = radar_tools.get_accumulation(end_date=this_time,
                                                duration=args.accum_len,
                                                desired_quantity=desired_quantity,
                                                data_path=args.input_data_dir,
                                                odim_latlon_file=args.h5_latlon_file,
                                                data_recipe=args.input_file_struc,
                                                dest_lon=args.out_lons,
                                                dest_lat=args.out_lats,
                                                proj_obj=args.proj_obj,
                                                median_filt=args.preproc_median_filt,
                                                smooth_radius=args.preproc_smooth_radius)

        if desired_quantity == 'accumulation':
            logger.warning('!!!convert mm to m since PR quantity is outputted!!!')
            dat_dict['accumulation'] /= 1e3
        data_quantity_name  = desired_quantity
        data_date_name      = 'end_date'
    else:
        #
        #if reflectivity is desired use:
        #desired_quantity='reflectivity'

        #
        #for precipitation rates used in LHN use:
        desired_quantity='precip_rate'

        #get, convert, interpolate and smooth ODIM Reflectivity mosaics
        t1 = time.time()
        dat_dict = radar_tools.get_instantaneous(valid_date=this_time,
                                                 desired_quantity=desired_quantity,
                                                 data_path=args.input_data_dir,
                                                 odim_latlon_file=args.h5_latlon_file,
                                                 data_recipe=args.input_file_struc,
                                                 dest_lon=args.out_lons,
                                                 dest_lat=args.out_lats,
                                                 input_proj_obj=args.proj_obj,
                                                 median_filt=args.preproc_median_filt,
                                                 smooth_radius=args.preproc_smooth_radius)
        t2 = time.time()
        logger.info(f'Reading took: {t2-t1:4.2f}s')
        data_quantity_name  = desired_quantity
        data_date_name      = 'valid_date'

    #if we got nothing, fill output with nodata and zeros
    if dat_dict is None:
        logger.warning('no data found or file unreadeable, observations are set to -9999. with quality index = 0.')
        expected_shape  = args.out_lats.shape
        precip_rate     = np.full(expected_shape, -9999.)
        quality_index   = np.zeros(expected_shape)
        data_valid_date = this_time
    else:
        precip_rate     = dat_dict[data_quantity_name]
        quality_index   = dat_dict['total_quality_index']
        data_valid_date = dat_dict[data_date_name]

    #mettre etiket
    if args.preproc_median_filt is None :
        etiquette_median_filt = 0
    else:
        etiquette_median_filt = args.preproc_median_filt
    if args.preproc_smooth_radius is None :
        etiquette_smooth_radius = 0
    else:
        etiquette_smooth_radius = args.preproc_smooth_radius
    etiket = 'MED'+"{:1d}".format(etiquette_median_filt)+'SM'+"{:02d}".format(etiquette_smooth_radius)

    _write_fst_file(this_time, precip_rate, quality_index, args, etiket=etiket, output_file=output_file)

    #make a figure for this std file if the argument figure_dir was provided
    if args.processed_figure_dir is not None:
        radar_tools.plot_rdpr_rdqi(fst_file=output_file, 
                                   this_date=this_time,
                                   figure_dir = args.processed_figure_dir,
                                   args=args)

    return this_time, 'success'



def _parse_num(arg, dtype='int', deltat_seconds=False):
    """
    change string to number

    parses m1p4 to -1.4
    removes preceding zeros

    with deltat_seconds=True output will always be in seconds
    Suffix can be:
        S, second, seconds         -> seconds
        M, minute, minutes         -> minutes (* 60)
        H, hour,   hours           -> hours   (* 3600)
    If no suffix: raises ValueError

    Examples:
        '2S'        -> 2
        '2 seconds' -> 2
        '2M'        -> 120
        '2 minutes' -> 120
        '2H'        -> 7200
        '2 hours'   -> 7200

    return desired type
    """

    if isinstance(arg, str):
        if deltat_seconds:
            import re
            #                      ([0-9]*\.?[0-9]+)   \s*   ([a-zA-Z]+)
            #                            ↑              ↑          ↑
            #                       number part     optional   unit part
            #                                        spaces
            match = re.fullmatch(r'([0-9]*\.?[0-9]+)\s*([a-zA-Z]+)', arg.strip())
            if not match:
                raise ValueError(
                    f"Cannot parse '{arg}': expected a number followed by a unit "
                    f"(e.g. '2S', '2 seconds', '13M', '13 minutes', '1H', '1 hour')"
                )
            value_str, unit = match.group(1), match.group(2).lower()

            if unit in ('s', 'second', 'seconds'):
                num_str = float(value_str)
            elif unit in ('m', 'minute', 'minutes'):
                num_str = float(value_str) * 60.
            elif unit in ('h', 'hour', 'hours'):
                num_str = float(value_str) * 3600.
            else:
                raise ValueError(
                    f"Unknown time unit '{unit}'. "
                    f"Use S/second/seconds, M/minute/minutes, or H/hour/hours."
                )
        else:
            num_str = arg.lstrip('0').replace('p', '.').replace('m', '-')
            if num_str == '':
                num_str = 0
    else:
        num_str = arg

    if dtype == 'int':
        out = int(num_str)
    elif dtype == 'float':
        out = float(num_str)
    else:
        raise ValueError('unknown dtype')

    return out


def _to_datetime(time_str):
    """
    changes string yyyymmddhhmmss to python datetime object
    """
    import datetime

    yyyy = _parse_num(time_str[0:4])
    mo   = _parse_num(time_str[4:6])
    dd   = _parse_num(time_str[6:8])
    hh   = _parse_num(time_str[8:10])
    mi   = _parse_num(time_str[10:12])
    ss   = 0
    return datetime.datetime(yyyy,mo,dd,hh,mi,ss)



def _motion_vector_at_one_time(this_time, args, missing=-9999., undetect=-3333.):
    """ read 3 precip field and compute motion vectors at one time

    re-reading precip fields is not the most efficient but the time needed to do this
    is negligible compared to computing motion vectors
    """

    import os
    import datetime
    import pysteps 
    import domutils
    import domutils._py_tools as dpy
    from domcmc import fst_tools

    logger = _setup_logging(args)

    logger.info(f'_motion_vector_at_one_time starting; end_time:{this_time}')

    # the file we want to write to
    output_file = args.motion_vectors_dir + this_time.strftime('%Y%m%d%H%M_end_window.npz')

    if (os.path.isfile(output_file) and args.complete_dataset):
        try:
            mv_avg = np.load(output_file)['uv_motion']
            logger.info(f'{output_file} is readeable and complete_dataset=True. Skipping to the next.')
            return this_time, 'skip'
        except:
            logger.info(f'{output_file} not readeable, we rewrite it.')
            os.remove(output_file)
    elif os.path.isfile(output_file):
        #file exists but we are not completing a dataset erase file before making a new one
        os.remove(output_file)
    else:
        #we will create a new file; before that make sure directory exists
        dpy.parallel_mkdir(args.motion_vectors_dir)

    # index in time array
    # number of timesteps for motion vectors
    nt = 3
    #                                                                                 -2, -1, 0
    desired_times = [ this_time + datetime.timedelta(seconds=(args.input_dt*tt)) for tt in np.arange(1-nt,1) ]

    # read precip, convert to reflectivity and reshape to make pysteps happy
    min_dbz = 0.
    z_acc = np.zeros((nt,args.out_ny,args.out_nx))
    for tt, input_time in enumerate(desired_times):
        fst_file = os.path.join(args.processed_data_dir, input_time.strftime(args.output_file_struc))
        if not os.path.isfile(fst_file):
            logger.warning(f'Problem with: {fst_file} file does not exist, no motion vector for {this_time}')
            return this_time, 'missing_input'
        z_v = fst_tools.get_data(var_name='RDPR', file_name=fst_file, datev=input_time)['values']
        if np.all(z_v <= min_dbz):
            logger.warning(f'Problem with: {fst_file} no valid pecip, no motion vector for {this_time}')
            return this_time, 'empty_input'
        z_acc[tt,:,:] = np.transpose(domutils.radar_tools.exponential_zr(z_v, r_to_dbz=True))

    # Only pixels that are genuinely missing (radar offline) in any frame
    # -9999. = nodata
    bad = np.any(z_acc <= missing, axis=0)  
    
    # Replace nodata sentinel with NaN across all frames for those pixels
    z_acc[:, bad] = np.nan
    
    # Replace undetect sentinel with your zero-echo dBZ value
    z_acc[z_acc <= undetect] = min_dbz  

    # compute motion vectors
    oflow_method = pysteps.motion.get_method("LK")
    uv_motion = oflow_method(z_acc)

    #save output to file
    try:
        np.savez_compressed(output_file, uv_motion=uv_motion)
    except:
        raise RuntimeError(f'problem writing: {output_file}')

    #make a figure for this std file if the argument figure_dir was provided
    if args.mv_figure_dir is not None:
        domutils.radar_tools.plot_rdpr_rdqi(uv_motion=uv_motion,
                                            z_acc=z_acc,
                                            lats=args.out_lats,
                                            lons=args.out_lons,
                                            this_date=this_time,
                                            figure_dir = args.mv_figure_dir,
                                            args=args)
   
    logger.info(f'_motion_vector_at_one_time done; end_time:{this_time}')
    
    return this_time, 'success'



def _t_interp_at_one_time(this_time, args ):
    """nowcasting time interpolation using forward and backward advection
    """

    import os
    import datetime
    from domcmc import fst_tools
    import domutils._py_tools as dpy
    from domutils import radar_tools
    import pysteps 
    import time

    missing = -9999.
    proj_obj = args.proj_obj

    # logging
    logger = _setup_logging(args)

    fst_output_file = output_fst_file(args, this_time)
    #logger.info(f'Working on: {os.path.basename(fst_output_file)}')
    if os.path.isfile(fst_output_file):
        if args.complete_dataset:
            # output file is there, check if data is there at this time. 
            _aquire_lock(fst_output_file)
            pr = fst_tools.get_data(var_name='RDPR', file_name=fst_output_file, datev=this_time)
            qi = fst_tools.get_data(var_name='RDQI', file_name=fst_output_file, datev=this_time)
            _release_lock(fst_output_file)
            if (pr is not None) and (qi is not None):
                logger.info(f'{fst_output_file} exists, desired data is there and complete_dataset=True. Skipping to the next.')
                return this_time, 'Skip'
        else:
            logger.info(f'{fst_output_file} exists, but complete_dataset=False. We remove this output file and recreate it.')
            os.remove(fst_output_file)
    else:
        #we will create a new file; before that make sure directory exists
        dpy.parallel_mkdir(args.output_dir)

    # weight model
    def exp_decay(dt):

        # weights depend on time in minutes
        t = dt/60.

        # with MED3 impact
        A = 4.670791350191597e-17
        B = 0.251576516840336
        C = 4.684302891729712e-18
        tau = 2.0070688609868617

        abs_t = np.abs(t)

        #A = 0.7197592925023092
        #B = 0.2678550020451625
        #C = 0.012385471844791388
        #tau = 0.7067125168603899

        return A*np.exp(-abs_t / tau) + B*np.exp(-abs_t / (10.*tau)) + C*np.exp(-abs_t / (100.*tau))

    def nearest_neighbor(dt):
        if dt < 0:
            weight = 0.
        else:
            weight = 1.

        return weight

    def linear(dt):
        abs_dt = np.abs(dt)
        return  1. - abs_dt/args.interp_max_dt

    #weight_fct = nearest_neighbor
    weight_fct = linear
    #weight_fct = exp_decay

    # all inputs within range to participate in average
    t_max = this_time + datetime.timedelta(seconds=args.interp_max_dt)
    t_min = this_time - datetime.timedelta(seconds=args.interp_max_dt)
    participating_list = []
    candidate_inputs = [ tt
                         for tt in args.input_date_list
                         if t_min <= tt < t_max
                       ]
    for input_time in candidate_inputs:
        dt = (this_time - input_time).total_seconds()
        weight = weight_fct(dt)
        if (weight < 0.) or (weight > 1.):
            raise ValueError(f'Weight out of bounds [0, 1]: {weight=}, {this_time=}')
        if np.isclose(weight,0.):
            continue
        #if np.isclose(weight,1.):
        #    dt = 0.
        participating_list.append({'vtime'  : input_time,
                                   'dt'     : dt,
                                   'weight' : weight
                                  })

    # if we are extrapolating, the last output data should always be part of the list
    last_input_time = args.input_date_list[-1]
    if this_time > last_input_time:
        last_input_is_in_list = False
        for item in participating_list:
            if item['vtime'] == last_input_time:
                last_input_is_in_list = True
                break
        if not last_input_is_in_list:
            dt = (this_time - last_input_time).total_seconds()
            weight = weight_fct(dt)
            #if np.isclose(weight,1.):
            #    dt = 0.
            participating_list.append({'vtime'  : last_input_time,
                                       'dt'     : dt,
                                       'weight' : weight
                                      })
            
    # info string
    participating_string = ''
    for item in participating_list:
        participating_string += f'{item['weight']:5.4f}*{item['dt']} +'
    logger.info(f'Mix for {this_time=}' + participating_string)

    # output matrices
    num_participants = len(participating_list)
    rr_arr          = np.full((args.out_nx, args.out_ny, num_participants), np.nan)
    qi_arr          = np.full((args.out_nx, args.out_ny, num_participants), np.nan)
    weighted_qi_arr = np.full((args.out_nx, args.out_ny, num_participants), np.nan)
    for pp, item in enumerate(participating_list):

        # the nowcasting step
        # all -ve values were assigned to Nan in this step
        advected_precip, advected_quality = perform_nowcast(args, item['vtime'], item['dt'], proj_obj=proj_obj)
        
        rr_arr[:,:,pp] = advected_precip
        qi_arr[:,:,pp] = advected_quality
        # make qi diminish as a result of advection
        weighted_qi_arr[:,:,pp] = item['weight']*advected_quality

    ###--------------------------------------------------------------------
    ### Weighted median filter of all nowcasts together
    ##interpolated_precip, interpolated_quality = weighted_median_3d(rr_arr, weighted_qi_arr, qi_arr)

    #interpolated_precip = weighted_median_3d_local3x3_numba(rr_arr, weighted_qi_arr)
    #interpolated_quality = qi_arr[:,:,0]
    #interpolated_precip  = np.where(np.isfinite(interpolated_precip), interpolated_precip, missing)
    #interpolated_quality  = np.where(np.isfinite(interpolated_quality), interpolated_quality, missing)


    ###--------------------------------------------------------------------
    # Averaging all nowcasts together
    #normalize weight so that column sum is one when obtaining PR averages
    qi_column_sum = np.nansum(weighted_qi_arr, axis=2, keepdims=True)
    pr_weights_arr = weighted_qi_arr / qi_column_sum
    qi_column_sum = np.squeeze(qi_column_sum)   # we don't need the 3rd dim of size 1 anymore

    interpolated_precip  = np.nansum(pr_weights_arr * rr_arr, axis=2)

    interpolated_quality = 1. -  np.prod( (1. - np.nan_to_num(weighted_qi_arr, nan=.0)), axis=2)

    interpolated_precip  = np.where(np.isclose(qi_column_sum, 0.), missing, interpolated_precip)
    #--------------------------------------------------------------------


    etiket = 'EXTRAPOL'
    _write_fst_file(this_time, interpolated_precip, interpolated_quality, args, etiket=etiket, 
                    output_file=fst_output_file)

    #make a figure for this std file if the argument figure_dir was provided
    if args.output_figure_dir is not None:
        radar_tools.plot_rdpr_rdqi(fst_file=fst_output_file, 
                                   this_date=this_time,
                                   figure_dir = args.output_figure_dir,
                                   info=participating_string,
                                   args=args)

    logger.info(f'Done interpolating to: {this_time}')
    return this_time, 'Success'

#@dask.delayed
#def _dask_error_f_deltat_at_one_time(*args, **kwargs):
#
#    #setup logger for dask worker if not already done
#    command_line_args = args[0]
#    logger = _setup_logging(command_line_args, is_worker=True, sub_dir='error_f_deltat')
#
#    return _error_f_deltat_at_one_time(*args, **kwargs)
#
#def _error_f_deltat_at_one_time(args, start_time, deltat_max, proj_obj):
#    """nowcasting time interpolation using forward and backward advection
#    """
#
#    import os
#    import time
#    import datetime
#    from domcmc import fst_tools
#    import domutils._py_tools as dpy
#    from domutils import radar_tools
#    import time
#    from scipy import stats
#    import sqlite3
#
#    missing = -9999.
#
#    # logging
#    logger = _setup_logging(args)
#
#    output_file = args.output_dir + start_time.strftime('%Y%m%d%H%M.sqlite')
#    logger.info(f'Working on: {os.path.basename(output_file)}')
#    if os.path.isfile(output_file) and args.complete_dataset:
#        logger.info(f'{output_file} exists, Skipping to the next.')
#        return np.array([1], dtype=float)
#    else:
#        #we will create a new file; before that make sure directory exists
#        dpy.parallel_mkdir(args.output_dir)
#
#    leadtimes = np.arange(0, deltat_max, args.input_dt)
#    # the nowcasting step
#    logger.info('Advecting...')
#    advected_precip, advected_quality = perform_nowcast(args, start_time, leadtimes, proj_obj)
#    if advected_precip is None:
#        logger.info(f'nothing to work with on {start_time}')
#        return np.array([1], dtype=float)
#    print('Done...')
#
#    # --- open DB and prepare table ---
#    conn = sqlite3.connect(output_file)
#    cur = conn.cursor()
#    
#    cur.execute("""
#    CREATE TABLE IF NOT EXISTS scores (
#        leadtime REAL,
#        rmse REAL,
#        mae REAL,
#        fcst_eff REAL
#    )
#    """)
#
#    desired_quantity='precip_rate'
#    for tt, this_leadtime in enumerate(leadtimes):
#
#        dat_dict = radar_tools.get_instantaneous(valid_date=start_time+datetime.timedelta(seconds=this_leadtime),
#                                                 desired_quantity=desired_quantity,
#                                                 data_path=args.input_data_dir,
#                                                 odim_latlon_file=args.h5_latlon_file,
#                                                 data_recipe=args.input_file_struc,
#                                                 dest_lon=args.out_lons,
#                                                 dest_lat=args.out_lats,
#                                                 input_proj_obj=proj_obj,
#                                                 median_filt=args.nowcast_median_filt,
#                                                 smooth_radius=args.nowcast_smooth_radius) 
#        this_reference = dat_dict[desired_quantity]
#        this_qi = dat_dict['total_quality_index']
#
#        this_nowcast =   advected_precip[:,:,tt]
#        this_quality =   advected_quality[:,:,tt]
#
#        good_pts = (this_qi > 0.) & (this_quality > 0.) & np.isfinite(this_reference) & np.isfinite(this_nowcast)
#
#        rmse = np.sqrt(np.mean((this_reference[good_pts] - this_nowcast[good_pts])**2.))
#        mae  = np.mean(  np.abs(this_reference[good_pts] - this_nowcast[good_pts]))
#        corr_coeff, _ = stats.pearsonr(this_reference[good_pts], this_nowcast[good_pts])
#        fcst_eff = 100.*(1. - np.sqrt(1. - corr_coeff**2.))
#
#        cur.execute(
#            """
#            INSERT INTO scores (leadtime, rmse, mae, fcst_eff)
#            VALUES (?, ?, ?, ?)
#            """,
#            (float(this_leadtime), float(rmse), float(mae), float(fcst_eff))
#        )
#        logger.info(f'leadtime {this_leadtime}, rmse {rmse}, mae {mae}, fcst_eff {fcst_eff}')
#
#    # --- save and close ---
#    conn.commit()
#    conn.close()
#
#    logger.info(f'Done error_f_deltat for: {start_time}, {os.path.basename(output_file)} was written.')
#    return np.array([1], dtype=float)


#def _error_f_deltat(args, deltat_max):
#    """ given evenly separated input radar data and motoin vectors
#        compute various error metrics as a function of deltat
#
#    """
#
#    import time
#    import dask
#    from domutils import radar_tools
#
#    #logging
#    logger = _setup_logging(args)
#
#    logger.info('Preparing projection object for advected precip')
#    t1 = time.time()
#    # note, median filter is not part of the projection object and need not be specified here
#    #       However, smooth radius and average are part of the projection object
#    valid_date = args.input_date_list[0]
#    desired_quantity='precip_rate'
#    dat_dict = radar_tools.get_instantaneous(valid_date=valid_date,
#                                             desired_quantity=desired_quantity,
#                                             data_path=args.input_data_dir,
#                                             odim_latlon_file=args.h5_latlon_file,
#                                             data_recipe=args.input_file_struc,
#                                             dest_lon=args.out_lons,
#                                             dest_lat=args.out_lats,
#                                             output_proj_obj=True,
#                                             smooth_radius=args.nowcast_smooth_radius)
#    advec_source_proj_obj = dat_dict['proj_obj']
#    t2 = time.time()
#    logger.info(f'Done in {t2-t1:4.2f}s')
#
#
#    if args.ncores == 1 :
#        #serial execution
#        logger.info('Launching SERIAL computation of nowcast error_f_deltat')
#
#        for start_time in args.input_date_list:
#            _error_f_deltat_at_one_time(args, start_time, deltat_max, advec_source_proj_obj)
#    else:
#        #parallel execution
#        logger.info('Launching PARALLEL of nowcast error_f_deltat')
#
#        tt1 = time.time()
#
#        #delay input data 
#        delayed_args = dask.delayed(args)
#        delayed_advec_source_proj_obj = dask.delayed(advec_source_proj_obj)
#
#        #delayed list of results
#        res_list = [dask.array.from_delayed(_dask_error_f_deltat_at_one_time(args, start_time, deltat_max, delayed_advec_source_proj_obj), (1,), float) for start_time in args.input_date_list ]
#
#        #what output do we want
#        res_stack = dask.array.stack(res_list)
#                
#        # computation happens here
#        big_arr = res_stack.compute()
#
#
#        tt2 = time.time()
#        logger.info(f'Parallel execution done; walltime: {tt2-tt1} seconds')


def _aquire_lock(filename):
    """ Acquire file lock
    """
    import time
    import os

    lock_file = filename+'.lock'

    start_time = time.time()
    timeout = 120.
    delay   = .5
    while True:
        try:
            # Attempt to create the lockfile.
            # These flags cause os.open to raise an OSError if the file already exists.
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            with os.fdopen(fd, "a") as f:
                f.write('You shall not pass!')
            break
        except FileExistsError:
            if (time.time() - start_time) >= timeout:
                raise RuntimeError("Timeout occurred getting file lock")
            print(f'waiting lockfile: {lock_file}')
            time.sleep(delay)

    return True


def _release_lock(filename):
    import os
    lock_file = filename+'.lock'
    if os.path.isfile(lock_file):
        os.unlink(lock_file)



def _write_fst_file(out_date, precip_rate, quality_index, args, etiket='', 
                    output_file=None):
    """ write precip to a fst file
    """
    import os
    import copy
    import rpnpy.librmn.all as rmn
    from rpnpy.rpndate import RPNDate
    from domcmc import fst_tools

    logger = _setup_logging(args)

    # read fst template
    fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR')

    #prepare std objects
    #cmc timestamp
    date_obj = RPNDate(out_date)
    cmc_timestamp = date_obj.datev

    #fst file to write to
    if output_file is None:
        output_file = output_fst_file(args, out_date)

    # aquire lock for this file
    _aquire_lock(output_file)

    first_time_writing_to_outfile = True
    if os.path.isfile(output_file):
        first_time_writing_to_outfile = False

    logger.info(f'writing {output_file}')
    iunit = rmn.fstopenall(output_file,rmn.FST_RW)

    if 'combined_yy_grid' in fst_template.keys():
        #write ^> to output file
        if first_time_writing_to_outfile:
            rmn.writeGrid(iunit, fst_template['combined_yy_grid'])

        #put precip rate into combined YY array
        nx, ny = precip_rate.shape
        reshaped_pr = np.full((nx, ny*2), -9999.)
        reshaped_qi = np.zeros((nx, ny*2))
        reshaped_pr[:,0:ny] = precip_rate
        reshaped_qi[:,0:ny] = quality_index
        precip_rate   = reshaped_pr
        quality_index = reshaped_qi

    else:
        #write >> ^^ to output file
        if first_time_writing_to_outfile:
            rmn.writeGrid(iunit, fst_template['grid'])

    #make RDPR entry
    rdpr_entry = copy.deepcopy(fst_template['meta'])
    rdpr_entry['nomvar']        = 'RDPR'
    rdpr_entry['etiket']        = etiket
    rdpr_entry['dateo']         = cmc_timestamp
    rdpr_entry['datev']         = cmc_timestamp
    rdpr_entry['ip2']           = 0
    rdpr_entry['deet']          = 0
    rdpr_entry['npas']          = 0
    rdpr_entry['nbits']         = 32
    rdpr_entry['typvar']        = 'I'
    rdpr_entry['d']             = np.asfortranarray(precip_rate, dtype='float32')

    #make RDQI entry
    rdqi_entry = copy.deepcopy(fst_template['meta'])
    rdqi_entry['nomvar']        = 'RDQI'
    rdqi_entry['etiket']        = etiket
    rdqi_entry['dateo']         = cmc_timestamp
    rdqi_entry['datev']         = cmc_timestamp
    rdqi_entry['ip2']           = 0
    rdqi_entry['deet']          = 0
    rdqi_entry['npas']          = 0
    rdqi_entry['nbits']         = 32
    rdqi_entry['typvar']        = 'I'
    rdqi_entry['d']             = np.asfortranarray(quality_index, dtype='float32')

    rmn.fstecr(iunit, rdpr_entry, rewrite=False)
    rmn.fstecr(iunit, rdqi_entry, rewrite=False)

    #close file
    rmn.fstcloseall(iunit)

    # release lock on file to allow other processes to write to it
    _release_lock(output_file)

    logger.info(f'Done writing {output_file}')


def write_empty_fst_output(args, this_date):
    fst_output_file = output_fst_file(args, this_date)
    precip_rate   = np.full((args.out_nx, args.out_ny), -9999.)
    quality_index = np.full((args.out_nx, args.out_ny), 0.)

    _write_fst_file(this_date, precip_rate, quality_index, args, etiket='EMPTY', 
                    output_file=fst_output_file)


def all_empty_outputs(args):
    """ If no inputs available, we generate empty outputs that will allow assim cycle to continue
    """
    logger = _setup_logging(args)
    for this_date in args.output_date_list:
        write_empty_fst_output(args, this_date)
    logger.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    logger.warning('')
    logger.warning('')
    logger.warning('ALL outputs are empty, something is wrong with input data')
    logger.warning('')
    logger.warning('')
    logger.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        



def obs_process(args=None):
    """ Batch processing of precipitation observation

      This function provides time and space interpolation of precipitiaton data.
      If desired, processing such as median filtering and boxcar-type filtering
      can be applied at the same time. 

      See  for an example.

      It is intended to be used as a command-line program, that would be called like:

      .. code-block:: bash

          python -m domutils.radar_tools.obs_process
                    --input_data_dir    .../data/radar_h5_composites/v8/ 
                    --output_dir        .../python/obs_process/outdir/                       
                    --output_figure_dir .../python/obs_process/figdir/                       
                    --fst_file_struc    %Y/%m/%d/%Y%m%d%H%M_mosaic.fst                                             
                    --input_file_struc  %Y/%m/%d/qcomp_%Y%m%d%H%M.h5                                               
                    --h5_latlon_file    .../files/radar_continental_2.5km_2882x2032.pickle   
                    --t0                ${t_start}                                                                 
                    --tf                ${t_stop}                                                                  
                    --input_dt          10                                                                         
                    --sample_pr_file    .../domains/hrdps_5p1_prp0.fst   
                    --ncores            40                                                                         
                    --complete_dataset  True                                                                       
                    --median_filt       3                                                                          
                    --smooth_radius     4                                                                          

      Alternatively, is is possible to call this function directly from Python by defining a
      simple object whose attributes are the arguments.
      Such use is demonstrated in :ref:`Interpolate a batch of observations`.
      

      Argument description:

      .. argparse::
          :module: domutils.radar_tools.obs_process
          :func: _define_parser
          :prog: obs_process


          

    """



    import os
    import sys
    import time
    import datetime
    import domutils._py_tools as dpy
    from domcmc import fst_tools
    from domutils import radar_tools

    #keep track of runtime
    time_start = time.time()

    if args is None:

        # we are processing command line arguments
        parser = _define_parser()
        args = parser.parse_args()

    else:
        # arguments are passed through the attributes of an object, 
        # set all non mandatory arguments to default values when called with args
        non_mandatory_args = _define_parser(only_arg_list=True)
        for (var_name, vtype, vdefault, vhelp) in non_mandatory_args:
            # remove the -- at the beginning  var_name
            var_name = var_name[2:]
            if not hasattr(args, var_name):
                setattr(args, var_name, vdefault)


    #add trailling / to all directories
    args.input_data_dir += '/'
    args.output_dir += '/'

    if args.output_figure_dir == 'no_figures' or args.output_figure_dir == 'None':
        args.output_figure_dir = None
    else:
        args.output_figure_dir += '/'

    if args.processed_figure_dir == 'no_figures' or args.processed_figure_dir == 'None':
        args.processed_figure_dir = None
    else:
        args.processed_figure_dir += '/'

    if args.mv_figure_dir == 'no_figures' or args.mv_figure_dir == 'None':
        args.mv_figure_dir = None
    else:
        args.mv_figure_dir += '/'

    if args.intermediate_files_dir == 'None':
        args.intermediate_files_dir = None
    else:
        args.intermediate_files_dir += '/'

    # parse numeric inputs
    def _number_that_may_be_none(arg):
        if arg is not None :
            if arg.lower() == 'none' :
                arg = None
            else:
                arg = _parse_num(arg)
        return arg

    args.accum_len             = _number_that_may_be_none(args.accum_len)
    args.preproc_median_filt   = _number_that_may_be_none(args.preproc_median_filt)
    args.nowcast_median_filt   = _number_that_may_be_none(args.nowcast_median_filt)
    args.preproc_smooth_radius = _number_that_may_be_none(args.preproc_smooth_radius)
    args.nowcast_smooth_radius = _number_that_may_be_none(args.nowcast_smooth_radius)
    args.avg_n_motion_vect     = _number_that_may_be_none(args.avg_n_motion_vect)

    if args.cartopy_dir == 'None':
        #if argument is not provided do nothing
        args.cartopy_dir = None
    else:
        #setup directory where shapefiles will be found
        args.cartopy_dir += '/'

    if args.dask_tmp_dir == 'None':
        #if argument is not provided do nothing
        args.dask_tmp_dir = os.getenv('TMPDIR')
    else:
        #setup directory where shapefiles will be found
        args.dask_tmp_dir += '/'

    if args.h5_latlon_file == 'None':
        args.h5_latlon_file = None

    #parse complete_dataset
    #not directly using bool type since any string, including 'False', will be interpreted as True....
    if args.complete_dataset.lower() == 'false':
        args.complete_dataset = False
    elif args.complete_dataset.lower() == 'true':
        args.complete_dataset = True
    else :
        raise ValueError('Argument --complete_dataset can only be set to True or False')

    #change date from string to datetime object
    args.input_t0 = _to_datetime(args.input_t0)
    if args.input_tf is not None:
        #if input_tf provided use it
        args.input_tf = _to_datetime(args.input_tf)
    else:
        #otherwise get it from fcst len
        args.fcst_len = _parse_num(args.fcst_len)
        args.input_tf = args.input_t0 + datetime.timedelta(seconds=args.fcst_len*3600.)

    args.input_dt = _parse_num(args.input_dt, dtype='float', deltat_seconds=True)

    if args.interp_max_dt is None:
        args.interp_max_dt = args.input_dt 
    elif args.interp_max_dt == 'None':
        args.interp_max_dt = args.input_dt 
    else:
        args.interp_max_dt = _parse_num(args.interp_max_dt, dtype='float', deltat_seconds=True)

    #output dates
    if args.output_t0 is None:
        args.output_t0 = args.input_t0
    elif args.output_t0 == 'None':
        args.output_t0 = args.input_t0
    else:
        args.output_t0 = _to_datetime(args.output_t0)
    if args.output_tf is None:
        args.output_tf = args.input_tf
    elif args.output_tf == 'None':
        args.output_tf = args.input_tf
    else:
        args.output_tf = _to_datetime(args.output_tf)
    if args.output_dt is None:
        args.output_dt = args.input_dt
    elif args.output_dt == 'None':
        args.output_dt = args.input_dt
    else: 
        args.output_dt = _parse_num(args.output_dt, dtype='float', deltat_seconds=True)

    # output size
    fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)
    if fst_template is None:
        raise ValueError('Problem getting PR from: ',args.sample_pr_file )
    (args.out_nx, args.out_ny) = fst_template['lat'].shape
    args.out_lats = fst_template['lat']
    args.out_lons = fst_template['lon']

    # initialize logging
    logger = _setup_logging(args)


    # flush logs directory if it exists
    if os.path.isdir('logs'):
        os.system('rm -rf logs')
    
    #log header
    logger.info('')
    logger.info('')
    logger.info('executing python script:  domutils.radar_tools.obs_process.py')
    logger.info('All logs printed to stdout can also be found in ./logs/')
    logger.info('')
    logger.info('')

    logger.info('After parsing, input arguments are:')
    for arg in vars(args):
       logger.info(arg +' = '+ str(getattr(args, arg)))
    logger.info('')
    logger.info('')

    if args.t_interp_method == 'nowcast':
        min_time_necessary = (  args.output_t0 
                              - datetime.timedelta(seconds=args.interp_max_dt)
                              - ((args.avg_n_motion_vect) * datetime.timedelta(seconds=args.input_dt))
                             )
        # we want input time list to start earlier than output dt
        while args.input_t0 > min_time_necessary:
            args.input_t0 -= datetime.timedelta(seconds=args.input_dt)

    #make list of dates where input radar data is needed and add it to arguments
    t_len = (args.input_tf-args.input_t0) + datetime.timedelta(seconds=1)    #+ 1 second for inclusive end point
    elasped_seconds = t_len.days*3600.*24. + t_len.seconds
    args.input_date_list = [args.input_t0 + datetime.timedelta(seconds=x) for x in np.arange(0,elasped_seconds,args.input_dt)]

    #make list of dates where output radar data is desired
    t_len = (args.output_tf-args.output_t0) + datetime.timedelta(seconds=1)    #+ 1 second for inclusive end point
    elasped_seconds = t_len.days*3600.*24. + t_len.seconds
    args.output_date_list = [args.output_t0 + datetime.timedelta(seconds=x) for x in np.arange(0,elasped_seconds,args.output_dt)]


    # pre-build projection object to accelerate reading when preprocessing data
    # note, median filter is not part of the projection object and need not be specified here
    logger.info('Preparing projection object for pre-processing')
    desired_quantity='precip_rate'
    t1 = time.time()
    valid_date = args.input_date_list[0]
    for valid_date in args.input_date_list:
        dat_dict = radar_tools.get_instantaneous(valid_date=valid_date,
                                                 desired_quantity=desired_quantity,
                                                 data_path=args.input_data_dir,
                                                 odim_latlon_file=args.h5_latlon_file,
                                                 data_recipe=args.input_file_struc,
                                                 dest_lon=args.out_lons,
                                                 dest_lat=args.out_lats,
                                                 output_proj_obj=True,
                                                 smooth_radius=args.preproc_smooth_radius)
        if dat_dict is not None:
            break

    if dat_dict is None:
        # no input available at ALL input dates, we write mock data that will no nothing and exit
        all_empty_outputs(args)
        return

    preprocess_proj_obj = dat_dict['proj_obj']
    t2 = time.time()
    logger.info(f'Done in {t2-t1:4.2f}s')

    # pre-build projection object to accelerate reading when performing final nowcast interp
    # note, median filter is not part of the projection object and need not be specified here
    logger.info('Preparing projection object for final nowcast interp')
    desired_quantity='precip_rate'
    t1 = time.time()
    # valid_date is set in the loop above for first existing entry
    dat_dict = radar_tools.get_instantaneous(valid_date=valid_date,
                                             desired_quantity=desired_quantity,
                                             data_path=args.input_data_dir,
                                             odim_latlon_file=args.h5_latlon_file,
                                             data_recipe=args.input_file_struc,
                                             dest_lon=args.out_lons,
                                             dest_lat=args.out_lats,
                                             output_proj_obj=True,
                                             smooth_radius=args.nowcast_smooth_radius)
    nowcast_interp_proj_obj = dat_dict['proj_obj']
    t2 = time.time()
    logger.info(f'Done in {t2-t1:4.2f}s')



    # remove potententially dangling lock file from previous run
    out_file_list = set( [output_fst_file(args, out_date) for out_date in args.output_date_list] )
    for this_file in sorted(out_file_list):
        if os.path.isfile(this_file+'.lock'):
            os.remove(this_file+'.lock')

    # clean outputs in clobber mode
    if args.complete_dataset:
        logger.info('complete_dataset=True; option, no cleanup of directories is performed. ')
    else:
        logger.info('complete_dataset=False; we remove all pre-existing output files before continuing. ')
        for this_file in sorted(out_file_list):
            if os.path.isfile(this_file):
                os.remove(this_file)


    if args.ncores > 1:
        logger.info(f'Starting local dask cluster with {args.ncores} workers.')

        if os.path.isfile('./maestro_dask_cluster/scheduler-file'):
            #parallel executions with a previously started dask cluster that can be used via a schedule file
            logger.info(f'Using existing dask cluster')
            args.dask_client = dask.distributed.Client(scheduler_file=params.scheduler_file, 
                                                       local_directory=params.tmp_dir)
        else:
            logger.info(f'Creating local dask cluster')
            args.dask_client = dask.distributed.Client(processes=True, threads_per_worker=1, 
                                                       n_workers=args.ncores, 
                                                       local_directory=args.dask_tmp_dir, 
                                                       silence_logs=40) 
        logger.info('Done')
    else:
        args.dask_client=None

    # time interpolation 
    if args.t_interp_method == 'None':
        # No temporal interpolation, only observation processing
        if args.output_date_list != args.input_date_list:
            raise ValueError('Select a time interpolation method if output is desired at times different from input')
        else:
            # 1- process radar file and write output to new files
            dates_to_process = args.input_date_list
            args.processed_data_dir = args.output_dir
            serial_parallel_sumbit(_process_at_one_time, args, dates_to_process)

    elif args.t_interp_method == 'nowcast':

        # set tmp files dir is specified
        if args.intermediate_files_dir is not None:
            intermediate_files_dir  = args.intermediate_files_dir
        else:
            intermediate_files_dir  = final_output_dir

        # directories for temporary files 
        # used in step 1 and 2
        args.processed_data_dir = os.path.join(intermediate_files_dir, 'processed/')

        # 1- Process input data and write output to files
        #    override output dir since in this context these outputs are only intermediate results
        args.proj_obj = preprocess_proj_obj
        dates_to_process = args.input_date_list
        serial_parallel_sumbit(_process_at_one_time, args, dates_to_process)

        # 2- compute motion vectors associated with processed outputs computed at the step above
        dates_to_process = args.input_date_list[args.avg_n_motion_vect-1:]
        args.motion_vectors_dir = os.path.join(intermediate_files_dir, 'motion_vectors/')
        serial_parallel_sumbit(_motion_vector_at_one_time, args, dates_to_process)

        # 3- use nowcast for time interpolation
        args.proj_obj = nowcast_interp_proj_obj
        dates_to_process = args.output_date_list
        serial_parallel_sumbit(_t_interp_at_one_time, args, dates_to_process)

        ## Optionnal- characterize error as function of deltat
        #args.output_dir = '/space/hall5/sitestore/eccc/mrd/rpndat/dja001/ten_minutes_time_interpolated/error_f_deltat_med3/'
        #deltat_max = 60. *60. # seconds
        #_error_f_deltat(args, deltat_max)

    else:
        raise ValueError('type of time interpolation not supported.')

    if args.dask_client is not None:
        args.dask_client.close()

    #we are done
    time_stop = time.time()
    logger.info(f'Python code completed, Runtime was : {time_stop-time_start} seconds')


def _define_parser(only_arg_list=False):
    '''return argument parser
    '''
    import argparse

    non_mandatory_args = [
          ('--h5_latlon_file'          , str,   'None',      "Pickle file containing the lat/lons of the Baltrad grid"),
          ('--input_tf'                , str,   'None',      "yyyymmsshhmmss end      time; datestring"),
          ('--fcst_len'                , str,   'None',      "duration of forecast (hours)"),
          ('--accum_len'               , str,   'None',      "duration of accumulation (minutes)"),
          ('--output_t0'               , str,   'None',      "yyyymmsshhmmss begining time; datestring"),
          ('--output_tf'               , str,   'None',      "yyyymmsshhmmss end      time; datestring"),
          ('--output_dt'               , str,   'None',      "interval (minutes M or seconds S) between output radar mosaics"),
          ('--t_interp_method'         , str,   'None',      "time interpolation method"),
          ('--interp_max_dt'           , str,   'None',      "max interval (minutes M or seconds S) where data will contribute to nowcast interpolation"),
          ('--avg_n_motion_vect'       , str,   'None',      "Number of motion vectors (separated by input_dt) to be averaged for more temporal consistency"),
          ('--sample_pr_file'          , str,   'None',      "File containing PR to establish the domain"),
          ('--output_file_format'      , str,   'npz',       "File format of processed files"),
          ('--ncores'                  , int,   1,           "number of cores for parallel execution"),
          ('--complete_dataset'        , str,   'False',     "Skip existing files, default is to clobber them"),
          ('--preproc_median_filt'     , str,   'None',      "Pre processing median filter; box size (pixels)"),
          ('--nowcast_median_filt'     , str,   'None',      "Advected data  median filter; box size (pixels)"),
          ('--preproc_smooth_radius'   , str,   'None',      "Pre processing smoothing radius (km) where radar data be smoothed"),
          ('--nowcast_smooth_radius'   , str,   'None',      "Advected_data  smoothing radius (km) where radar data be smoothed"),
          ('--intermediate_files_dir'  , str,   'None',      "Where to store processed and motion vector files when doing nowcast interpolation"),
          ('--processed_figure_dir'    , str,   'no_figures',"If a path is provided, a figure will be created for each std file created"),
          ('--mv_figure_dir'           , str,   'no_figures',"If a path is provided, a figure will be created for each std file created"),
          ('--output_figure_dir'       , str,   'no_figures',"If a path is provided, a figure will be created for each std file created"),
          ('--cartopy_dir'             , str,   'None',      "Directory for cartopy shape files"),
          ('--dask_tmp_dir'            , str,   'None',      "Directory for dask tmp files"),
          ('--figure_format'           , str,   'gif',       "File format of figure "),
          ('--log_level'               , str,   'INFO',      "minimum level of messages printed to stdout and in log files "),
          ]

    if only_arg_list:
        # we only want the list of mandatory arguments and their default values
        return non_mandatory_args
    else:
        # we want a full fledged argument parser
        desc="read radar H5 files, interpolate/smooth and write to FST"
        parser = argparse.ArgumentParser(description=desc, 
                 prefix_chars='-+', formatter_class=argparse.RawDescriptionHelpFormatter)
        required_args = parser.add_argument_group('Required named arguments')
        required_args.add_argument("--input_data_dir"   , type=str,   required=True,  help="path of source radar mosaics files")
        required_args.add_argument("--input_t0"         , type=str,   required=True,  help="yyyymmsshhmmss begining time; datestring")
        required_args.add_argument("--input_dt"         , type=str,   required=True,  help="interval (minutes M or seconds S) between input radar mosaics")
        required_args.add_argument("--output_dir"       , type=str,   required=True,  help="directory for output fst files")
        required_args.add_argument("--output_file_struc", type=str,   required=True,  help="strftime syntax for constructing fst filenames for output of obsprocess")
        required_args.add_argument("--input_file_struc" , type=str,   required=True,  help="strftime syntax for constructing H5  filenames")

        optional_args = parser.add_argument_group('Optional named arguments')
        for (var_name, vtype, vdefault, vhelp) in non_mandatory_args:
            optional_args.add_argument(var_name, type=vtype, default=vdefault, help=vhelp)

        return parser

if __name__ == '__main__':     
    obs_process()

