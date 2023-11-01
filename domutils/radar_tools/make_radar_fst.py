
#identify logger names based on package hierarchy
import numpy as np
import dask
import dask.array 
import dask.distributed

def setup_logging(args, is_worker=False):
    """setup logger and handlers

    Because of parallel execution, logging has to be setup for every forked processes
    so it is put in this reusable function
    """

    import sys 
    import logging

    # logging is configured to write everything to stdout in addition to a log file
    # in a 'logs' directory
    logging_basename = 'domutils.radar_tools'
    logger = logging.getLogger(logging_basename)
    # if this is a newly created logger, it will have no handlers
    if not len(logger.handlers):
        logging.captureWarnings(True)
        logger.setLevel(args.log_level)
        #handlers
        stream_handler = logging.StreamHandler(sys.stdout)
        if is_worker:
            worker_id = str(dask.distributed.get_worker().id)
            file_handler = logging.FileHandler('logs/'+worker_id, 'w')
        else:
            file_handler = logging.FileHandler('logs/main.log', 'w')
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

@dask.delayed
def dask_to_fst(*args, **kwargs):
    import sys
    import multiprocessing

    #setup logger for dask worker if not already done
    command_line_args = args[2]
    logger = setup_logging(command_line_args, is_worker=True)

    return to_fst(*args, **kwargs)


def to_fst(valid_date, fst_template, args):
    #output data to std file

    import os
    import time
    import copy
    import rpnpy.librmn.all as rmn
    from rpnpy.rpndate import RPNDate
    from domutils import radar_tools
    import domutils._py_tools as dpy

    logger = setup_logging(args)

    logger.info('to_fst starting to process date: '+str(valid_date))

    #output filename and directory
    output_file = args.output_dir + valid_date.strftime(args.processed_file_struc)
    #if in complete mode and file exists, return and test next one
    if (os.path.isfile(output_file) and args.complete_dataset):
        logger.info(output_file+ ' exists and complete_dataset=True. Skipping to the next.')
        return np.array([1], dtype=float)
    elif os.path.isfile(output_file):
        #file exists but we are not completing a dataset erase file before making a new one
        os.remove(output_file)
    else:
        #we will create or overwrite the file; before that make sure directory exists
        this_fst_dir = os.path.dirname(output_file)
        dpy.parallel_mkdir(this_fst_dir)
    
    #get destination grid from PR template
    dest_lon = fst_template['lon']
    dest_lat = fst_template['lat']

    #reading the data
    if args.accum_len is not None:
        desired_quantity='accumulation'
        fst_var_name='PR'
        dat_dict = radar_tools.get_accumulation(end_date=valid_date,
                                                duration=args.accum_len,
                                                desired_quantity=desired_quantity,
                                                data_path=args.radar_data_dir,
                                                odim_latlon_file=args.h5_latlon_file,
                                                data_recipe=args.h5_file_struc,
                                                dest_lon=dest_lon,
                                                dest_lat=dest_lat,
                                                median_filt=args.median_filt,
                                                smooth_radius=args.smooth_radius)

        if desired_quantity == 'accumulation':
            logger.warning('!!!convert mm to m since PR quantity is outputted!!!')
            dat_dict['accumulation'] /= 1e3
        data_quantity_name  = desired_quantity
        data_date_name      = 'end_date'
    else:
        #
        #if reflectivity is desired use:
        #desired_quantity='reflectivity'
        #fst_var_name='RDBZ'

        #
        #for precipitation rates used in LHN use:
        desired_quantity='precip_rate'
        fst_var_name='RDPR'

        #get, convert, interpolate and smooth ODIM Reflectivity mosaics
        dat_dict = radar_tools.get_instantaneous(valid_date=valid_date,
                                                 desired_quantity=desired_quantity,
                                                 data_path=args.radar_data_dir,
                                                 odim_latlon_file=args.h5_latlon_file,
                                                 data_recipe=args.h5_file_struc,
                                                 dest_lon=dest_lon,
                                                 dest_lat=dest_lat,
                                                 median_filt=args.median_filt,
                                                 smooth_radius=args.smooth_radius)
        data_quantity_name  = desired_quantity
        data_date_name      = 'valid_date'

    #if we got nothing, fill output with nodata and zeros
    if dat_dict is None:
        logger.warning('no data found or file unreadeable, observations are set to -9999. with quality index = 0.')
        expected_shape  = dest_lat.shape
        precip_rate     = np.full(expected_shape, -9999.)
        quality_index   = np.zeros(expected_shape)
        data_valid_date = valid_date
    else:
        precip_rate     = dat_dict[data_quantity_name]
        quality_index   = dat_dict['total_quality_index']
        data_valid_date = dat_dict[data_date_name]

    #mettre etiket
    if args.median_filt is None :
        etiquette_median_filt = 0
    else:
        etiquette_median_filt = args.median_filt
    if args.smooth_radius is None :
        etiquette_smooth_radius = 0
    else:
        etiquette_smooth_radius = args.smooth_radius
    etiket = 'MED'+"{:1d}".format(etiquette_median_filt)+'SM'+"{:02d}".format(etiquette_smooth_radius)

    write_fst_file(valid_date, precip_rate, quality_index, args, etiket=etiket)

    #make a figure for this std file if the argument figure_dir was provided
    if args.figure_dir is not None:
        radar_tools.plot_rdpr_rdqi(fst_file=output_file, 
                                   this_date=valid_date,
                                   fig_dir=args.figure_dir,
                                   fig_format=args.figure_format,
                                   args=args)

    return np.array([1.],dtype=float)



def parse_num(arg, dtype='int'):
    """
    change string to number

    parses m1p4 to -1.4
    removes preceding zeros

    return desired type
    """

    num_str = arg.lstrip('0').replace('p','.').replace('m','-')
    if num_str == '':
        num_str = 0

    if dtype == 'int':
        out = int(num_str)
    elif dtype == 'float':
        out = float(num_str)
    else:
        raise ValueError('unknown dtype')

    return out


def to_datetime(time_str):
    """
    changes string yyyymmddhhmmss to python datetime object
    """
    import datetime

    yyyy = parse_num(time_str[0:4])
    mo   = parse_num(time_str[4:6])
    dd   = parse_num(time_str[6:8])
    hh   = parse_num(time_str[8:10])
    mi   = parse_num(time_str[10:12])
    ss   = 0
    return datetime.datetime(yyyy,mo,dd,hh,mi,ss)


def obs_process(args):
    """ read odim H5, manipulate it, and write to fst

    depending on the number of cpus, serial execution or parallel execution with multiprocessing will be chosen 
    """

    import os
    import datetime
    import glob
    import signal
    import time
    from domcmc import fst_tools


    #logging
    logger = setup_logging(args)

    logger.info('getting output domain from: '+ args.sample_pr_file)
    fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)
    if fst_template is None:
        raise ValueError('Problem getting PR from: ',args.sample_pr_file )

    #if only 1 cpu, do serial execution in a for loop
    # makes for easier debugging 
    if args.ncores == 1 :
        #serial execution
        logger.info('Launching SERIAL execution of obs processing')
        for this_date in args.input_date_list:
            to_fst(this_date, fst_template, args)
    else :
        #parallel conversion with nultiprocessing
        logger.info('Launching PARALLEL execution of of observation processing')

        #delay input data 
        delayed_args         = dask.delayed(args)
        delayed_fst_template = dask.delayed(fst_template)

        #delayed list of results
        res_list = [dask.array.from_delayed(dask_to_fst(this_date, delayed_fst_template, delayed_args), (1,), float) for this_date in args.input_date_list ]

        #what output do we want
        res_stack = dask.array.stack(res_list)
                
        # computation happens here
        tt1 = time.time()
        big_arr = res_stack.compute()
        tt2 = time.time()
        print('  parallel execution took ', tt2-tt1, ' seconds')
        print('')
        print(big_arr.shape)

        ##setup parallel submission
        #original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        #pool = multiprocessing.Pool(args.ncores)
        #signal.signal(signal.SIGINT, original_sigint_handler)

        ##function that gets called when something goes wrong in the pool
        #def kill_pool(err_msg):
        #    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #    print('Error message from failing task:')
        #    print(err_msg)
        #    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #    pool.terminate()
        #
        ##jobs are launched in parallel
        #res_list = []
        #for this_date in args.input_date_list:
        #    res_list.append(
        #            pool.apply_async( dask_to_fst, 
        #                              args=(this_date, fst_template, args), 
        #                              error_callback=kill_pool,
        #                            ) 
        #        )

        ##get results
        #results = np.asarray([_res.get() for _res in res_list])

        ## Normal termination
        #pool.close()
        #pool.join()

        # check that we received all correct termination
        if big_arr.sum() != len(args.input_date_list) :
            raise RuntimeError('did not receive correct termination from all processes')

@dask.delayed
def dask_motion_vector_at_one_time(*args, **kwargs):
    return motion_vector_at_one_time(*args, **kwargs)

def motion_vector_at_one_time(this_time, args):
    """ read 3 precip field and compute motion vectors at one time

    re-reading precip fields is not the most efficient but the time needed to do this
    is negligible compared to computing motion vectors
    """

    import os
    import domutils
    import domutils._py_tools as dpy
    import pysteps
    from domcmc import fst_tools

    logger = setup_logging(args)

    logger.info('motion_vector_at_one_time starting to process date: '+str(this_time))

    # the file we want to write to
    output_file = args.motion_vectors_dir + this_time.strftime('%Y%m%d%H%M_end_window.npy')

    if (os.path.isfile(output_file) and args.complete_dataset):
        logger.info(output_file+ ' exists and complete_dataset=True. Skipping to the next.')
        return np.array([1], dtype=float)
    elif os.path.isfile(output_file):
        #file exists but we are not completing a dataset erase file before making a new one
        os.remove(output_file)
    else:
        #we will create a new file; before that make sure directory exists
        dpy.parallel_mkdir(args.motion_vectors_dir)

    # index in time array
    tt = args.input_date_list.index(this_time)
    logger.info(f'Computing motion vectors, end time: {this_time}')

    # number of timesteps for motion vectors
    nt = 3
    z_acc = np.zeros((nt, args.out_ny, args.out_nx))

    # read precip, convert to reflectivity and reshape to make pysteps happy
    z_v = fst_tools.get_data(var_name='RDPR', dir_name=args.output_dir, datev=args.input_date_list[tt-2])['values']
    z_acc[0,:,:] = np.transpose(domutils.radar_tools.exponential_zr(z_v, r_to_dbz=True))
    z_v = fst_tools.get_data(var_name='RDPR', dir_name=args.output_dir, datev=args.input_date_list[tt-1])['values']
    z_acc[1,:,:] = np.transpose(domutils.radar_tools.exponential_zr(z_v, r_to_dbz=True))
    z_v = fst_tools.get_data(var_name='RDPR', dir_name=args.output_dir, datev=args.input_date_list[tt  ])['values']
    z_acc[2,:,:] = np.transpose(domutils.radar_tools.exponential_zr(z_v, r_to_dbz=True))

    # remove small values
    min_dbz = 0.
    z_acc = np.where(z_acc < min_dbz, 0., z_acc)

    # compute motion vectors
    oflow_method = pysteps.motion.get_method("LK")
    uv_motion = oflow_method(z_acc)

    #save output to file
    np.save(output_file, uv_motion)
    
    #           U               V
    logger.info('Motion vectors done', uv_motion.dtype)
    return np.array([1], dtype=float)


def make_motion_vectors(args):
    """ compute motion vectors for radar observations available at a evenly separated times

    depending on the number of cpus, serial execution or parallel execution with multiprocessing will be chosen 
    """

    import time
    import glob
    import signal
    import dask
    from domcmc import fst_tools

    #logging
    logger = setup_logging(args)

    #read first entry to get dimensions
    z_v = fst_tools.get_data(var_name='RDPR', dir_name=args.processed_dir, datev=args.input_date_list[0])['values']
    nx, ny = z_v.shape
    args.out_nx = nx
    args.out_ny = ny

    #for output we keep pysteps dim convention ny, ny, nx
    nt = len(args.input_date_list)-2


    if args.ncores == 1 :
        #serial execution
        logger.info('Launching SERIAL computation of motion vectors')
        result_arr = np.zeros((nt,))
        for tt, this_time in enumerate(args.input_date_list[2:]):

            this_result = motion_vector_at_one_time(this_time, args)
            
            #shift before next round
            result_arr[tt] = this_result

    else:
        #parallel execution
        logger.info('Launching PARALLEL computation of motion vectors')

        #delay input data 
        delayed_args = dask.delayed(args)

        #delayed list of results
        res_list = [dask.array.from_delayed(dask_motion_vector_at_one_time(this_date, delayed_args), (1,), float) for this_date in args.input_date_list[2:] ]

        #what output do we want
        res_stack = dask.array.stack(res_list)
                
        # computation happens here
        tt1 = time.time()
        result_arr = res_stack.compute()
        tt2 = time.time()
        print('  parallel execution took ', tt2-tt1, ' seconds')

    print('')
    print(f'Sum result arr: {int(np.sum(result_arr))}, we expected: {len(args.input_date_list[2:])}')

def scale_wind(uv, fact_before):
    """scale wind vector for mid timesteps
    """

    # conversion to rho theta (met angle convention)
    rho = np.sqrt(uv[0,:,:]**2. + uv[1,:,:]**2.)
    theta = np.arctan2(uv[0,:,:],uv[1,:,:])

    # scale modulus
    rho *= fact_before
    uv[0,:,:] = rho * np.sin(theta)
    uv[1,:,:] = rho * np.cos(theta)

    # return scaled u and v components
    return uv


@dask.delayed
def dask_t_interp_at_one_time(*args, **kwargs):
    return t_interp_at_one_time(*args, **kwargs)

def t_interp_at_one_time(out_time, args):
    """nowcasting time interpolation using forward and backward advection
    """

    import os
    from domcmc import fst_tools
    import domutils._py_tools as dpy
    from pysteps import nowcasts
    import pysteps 
    import time

    missing = -9999.

    # logging
    logger = setup_logging(args)

    # Because outputs at multiple times can be found in the same output files
    # time interpolated outputs are always regenerated and not compatible with 
    # the --complete_dataset keywork.

    fst_output_file = args.output_dir + out_time.strftime(args.tinterpolated_file_struc)
    if not os.path.isfile(fst_output_file):
        #we will create a new file; before that make sure directory exists
        dpy.parallel_mkdir(args.output_dir)

    # find input time just after and just before
    found = False
    do_backward_advect = True
    for t_after, this_time in enumerate(args.input_date_list):
        if this_time > out_time:
            found = True
            break

    if (t_after == 0) :
        raise RuntimeError('desired out_time is before the first available input')

    if found :
        # found interval that brackets out time, all is well
        t_before = t_after -1
    else:
        if out_time >= args.input_date_list[-1]:
            # out_time is equal or larger than last input time
            # only forward advection will be used to generate nowcast
            do_backward_advect = False
            t_before = -1
        else:
            raise RuntimeError('Something weird going on, stopping')

    #initialize advection code
    extrapolate = pysteps.extrapolation.interface.get_method("semilagrangian")

    # multiplicative factors for intermediate timesteps before and after
    fact_before = (out_time - args.input_date_list[t_before]).seconds / args.input_dt
    # get wind before and after
    wind_file = args.motion_vectors_dir + args.input_date_list[t_before].strftime('%Y%m%d%H%M_end_window.npy')
    uv_before = np.load(wind_file)
    # scale wind 
    uv_before = scale_wind(uv_before, fact_before)
    # get precip before and after
    precip_before  = np.transpose(fst_tools.get_data(var_name='RDPR', dir_name=args.processed_dir, datev=args.input_date_list[t_before])['values'])
    quality_before = np.transpose(fst_tools.get_data(var_name='RDQI', dir_name=args.processed_dir, datev=args.input_date_list[t_before])['values'])
    # advect wind at appropriate time
    forward_precip   = np.transpose(extrapolate(precip_before,  uv_before, 1, outval=0.))
    forward_quality  = np.transpose(extrapolate(quality_before, uv_before, 1, outval=0.))
    # adjust missing values that could have been modified during advection
    forward_precip = np.where(forward_precip < 0., missing, forward_precip)


    if do_backward_advect: 
        # multiplicative factors for intermediate timesteps before and after
        fact_after  = -1. * (args.input_date_list[t_after] - out_time ).seconds / args.input_dt
        # get wind before and after
        wind_file = args.motion_vectors_dir + args.input_date_list[t_after ].strftime('%Y%m%d%H%M_end_window.npy')
        uv_after  = np.load(wind_file)
        # scale wind 
        uv_after  = scale_wind(uv_after,  fact_after)
        # get precip before and after
        precip_after   = np.transpose(fst_tools.get_data(var_name='RDPR', dir_name=args.processed_dir, datev=args.input_date_list[t_after] )['values'])
        quality_after  = np.transpose(fst_tools.get_data(var_name='RDQI', dir_name=args.processed_dir, datev=args.input_date_list[t_after] )['values'])
        # advect wind at appropriate time
        backward_precip  = np.transpose(extrapolate(precip_after,   uv_after,  1, outval=0.))
        backward_quality = np.transpose(extrapolate(quality_after,  uv_after,  1, outval=0.))
        # adjust missing values that could have been modified during advection
        backward_precip = np.where(backward_precip < 0., missing, backward_precip)

        # average result weighted by separation time
        precip_rate   = (1. - fact_before)*forward_precip  + fact_before*backward_precip
        quality_index = (1. - fact_before)*forward_quality + fact_before*backward_quality
        # exclude nodata from average, pick only the alternative when available
        if fact_before > 0.:
            precip_rate   = np.where( forward_precip < 0.,  backward_precip,  precip_rate)
            quality_index = np.where( forward_precip < 0., backward_quality,  quality_index)
        if (1. - fact_before) > 0.:
            precip_rate   = np.where(backward_precip < 0.,   forward_precip,  precip_rate)
            quality_index = np.where(backward_precip < 0.,  forward_quality,  quality_index)

    else:
        # We only did forward advection
        precip_rate   = forward_precip 
        quality_index = forward_quality

    etiket = 'EXTRAPOL'
    write_fst_file(out_time, np.squeeze(precip_rate), np.squeeze(quality_index), args, etiket=etiket, 
                   output_file=fst_output_file)

    return np.array([1], dtype=float)

def nowcast_t_interp(args):
    """ given precip estimates and motion vectors, do nowcasts as a mean of time interpolation

    """

    import time
    import glob
    import signal
    import dask
    import dask.array as da
    from domcmc import fst_tools

    #logging
    logger = setup_logging(args)


    if args.ncores == 1 :
        #serial execution
        logger.info('Launching SERIAL computation of nowcast time interpolation')

        for out_time in args.output_date_list:
            t_interp_at_one_time(out_time, args)
    else:
        #parallel execution
        logger.info('Launching PARALLEL of nowcast time interpolation')

        #delay input data 
        delayed_args = dask.delayed(args)

        #delayed list of results
        res_list = [dask.array.from_delayed(dask_t_interp_at_one_time(this_date, delayed_args), (1,), float) for this_date in args.output_date_list ]

        #what output do we want
        res_stack = dask.array.stack(res_list)
                
        # computation happens here
        tt1 = time.time()
        big_arr = res_stack.compute()
        tt2 = time.time()
        print('  parallel execution took ', tt2-tt1, ' seconds')
        print('')
        print(big_arr.shape)


def aquire_lock(filename):
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


def release_lock(filename):
    import os
    lock_file = filename+'.lock'
    if os.path.isfile(lock_file):
        os.unlink(lock_file)



def write_fst_file(out_date, precip_rate, quality_index, args, etiket='', 
                   output_file=None):
    """ write precip to a fst file
    """
    import os
    import copy
    import rpnpy.librmn.all as rmn
    from rpnpy.rpndate import RPNDate
    from domcmc import fst_tools

    logger = setup_logging(args)

    # read fst template
    fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR')

    #prepare std objects
    #cmc timestamp
    date_obj = RPNDate(out_date)
    cmc_timestamp = date_obj.datev

    #fst file to write to
    if output_file is None:
        output_file = args.output_dir + out_date.strftime(args.processed_file_struc)

    # aquire lock for this file
    aquire_lock(output_file)

    first_time_writing_to_outfile = True
    if os.path.isfile(output_file):
        first_time_writing_to_outfile = False

    logger.info('writing ' + output_file)
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
    release_lock(output_file)

    logger.info('Done writing ' + output_file)




def main():
    """ module for making a CMC "standard" file containing radar data

    It is intended to be used as a script, for example:

    

      =====================================================
      export XDG_RUNTIME_DIR=$TMPDIR
      export OMP_NUM_THREADS=2
      ulimit -s 128000
      
      #make symlink to anaconda python interpreter
      conda_python=$(which python)
      rm -f conda_python
      ln -s ${conda_python} conda_python
      
      #inclusively
      t_start=$(r.date -V 2016070109)
      t_stop=$(r.date -V  2016070115)
      
      #get info on options with 
      # python -m domutils.radar_tools.make_radar_fst -h
      
      #path to operationnal baltrad outputs:
      #  /space/hall4/sitestore/eccc/cmod/prod/hubs/radar/BALTRAD/Outcoming/Composites/ \
      
      #process data and make std file
      python -m domutils.radar_tools.make_radar_fst                                                           \
                --radar_data_dir   /space/hall4/sitestore/eccc/mrd/rpndat/dja001/data/radar_h5_composites/v8/ \
                --output_dir       /home/dja001/python/make_radar_fst/outdir/                                 \
                --figure_dir       /home/dja001/python/make_radar_fst/figdir/                                 \
                --fst_file_struc   %Y/%m/%d/%Y%m%d%H%M_mosaic.fst                                             \
                --h5_file_struc    %Y/%m/%d/qcomp_%Y%m%d%H%M.h5                                               \
                --h5_latlon_file   /home/dja001/shared_stuff/files/radar_continental_2.5km_2882x2032.pickle   \
                --t0               ${t_start}                                                                 \
                --tf               ${t_stop}                                                                  \
                --input_dt         10                                                                         \
                --sample_pr_file   /space/hall4/sitestore/eccc/mrd/rpndat/dja001/domains/hrdps_5p1_prp0.fst   \
                --ncores           40                                                                         \
                --complete_dataset True                                                                       \
                --median_filt      3                                                                          \
                --smooth_radius    4                                                                          \
      
      if [[ $? -ne 0 ]] ; then
          echo 'A problem has occured; exiting'
          exit 1
      fi
      =====================================================

    """



    import os
    from os import linesep as newline
    import sys
    import argparse
    import time
    import datetime
    import domutils._py_tools as dpy


    #keep track of runtime
    time_start = time.time()

    #parse arguments
    desc="read radar H5 files, interpolate/smooth and write to FST"
    parser = argparse.ArgumentParser(description=desc, 
             prefix_chars='-+', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--radar_data_dir"   , type=str,   required=True,  help="path of source radar mosaics files")
    parser.add_argument("--output_dir"       , type=str,   required=True,  help="directory for output fst files")
    parser.add_argument("--processed_file_struc", type=str,required=True,  help="strftime syntax for constructing fst filenames for output of obsprocess")
    parser.add_argument("--tinterpolated_file_struc", type=str,required=False,  help="strftime syntax for constructing time interpolated filenames")
    parser.add_argument("--h5_file_struc"    , type=str,   required=True,  help="strftime syntax for constructing H5  filenames")
    parser.add_argument("--h5_latlon_file"   , type=str,   required=False, help="Pickle file containing the lat/lons of the Baltrad grid")
    parser.add_argument("--input_t0"         , type=str,   required=True,  help="yyyymmsshhmmss begining time; datestring")
    parser.add_argument("--input_tf"         , type=str,   required=False, help="yyyymmsshhmmss end      time; datestring")
    parser.add_argument("--input_dt"         , type=str,   required=True,  help="interval (minutes) between input radar mosaics")
    parser.add_argument("--fcst_len"         , type=float, required=False, help="duration of forecast (hours)")
    parser.add_argument("--accum_len"        , type=str,   required=False, help="duration of accumulation (minutes)")
    parser.add_argument("--output_t0"        , type=str,   required=False, help="yyyymmsshhmmss begining time; datestring")
    parser.add_argument("--output_tf"        , type=str,   required=False, help="yyyymmsshhmmss end      time; datestring")
    parser.add_argument("--output_dt"        , type=str,   required=True,  help="interval (minutes) between output radar mosaics")
    parser.add_argument("--t_interp_method"  , type=str,   default='None', help="time interpolation method")
    parser.add_argument("--sample_pr_file"   , type=str,   required=True,  help="File containing PR to establish the domain")
    parser.add_argument("--ncores"           , type=int,   default=1,      help="number of cores for parallel execution")
    parser.add_argument("--complete_dataset" , type=str,   default='False',help="Skip existing files, default is to clobber them")
    parser.add_argument("--median_filt"      , type=str,   default='None', help="box size (pixels) for median filter")
    parser.add_argument("--smooth_radius"    , type=str,   default='None', help="radius (km) where radar data be smoothed")
    parser.add_argument("--figure_dir"       , type=str,   default='no_figures', help="If provided, a figure will be created for each std file created")
    parser.add_argument("--cartopy_dir"      , type=str,   default='None', help="Directory for cartopy shape files")
    parser.add_argument("--figure_format"    , type=str,   default='gif',  help="File format of figure ")
    parser.add_argument("--log_level"        , type=str,   default='INFO', help="minimum level of messages printed to stdout and in log files ")
    args = parser.parse_args()


    #add trailling / to all directories
    args.radar_data_dir += '/'
    args.output_dir += '/'
    if args.figure_dir == 'no_figures' or args.figure_dir == 'None':
        args.figure_dir = None
    else:
        args.figure_dir += '/'

    #parse accum_len
    if args.accum_len is not None :
        if args.accum_len == 'None' :
            args.accum_len = None
        else:
            args.accum_len = parse_num(args.accum_len)

    #parse median_filt
    if args.median_filt is not None :
        if args.median_filt == 'None' :
            args.median_filt = None
        else:
            args.median_filt = parse_num(args.median_filt)

    #parse smooth_radius
    if args.smooth_radius is not None :
        if args.smooth_radius == 'None' :
            args.smooth_radius = None
        else:
            args.smooth_radius = parse_num(args.smooth_radius)

    if args.cartopy_dir == 'None':
        #if argument is not provided do nothing
        args.cartopy_dir = None
    else:
        #setup directory where shapefiles will be found
        args.cartopy_dir += '/'

    #parse complete_dataset
    #not directly using bool type since any string, including 'False', will be interpreted as True....
    if args.complete_dataset.lower() == 'false':
        args.complete_dataset = False
    elif args.complete_dataset.lower() == 'true':
        args.complete_dataset = True
    else :
        raise ValueError('Argument --complete_dataset can only be set to True or False')

    #change date from string to datetime object
    args.input_t0 = to_datetime(args.input_t0)
    if args.input_tf is not None:
        #if input_tf provided use it
        args.input_tf = to_datetime(args.input_tf)
    else:
        #otherwise get it from fcst len
        args.input_tf = args.input_t0 + datetime.timedelta(seconds=args.fcst_len*3600.)
    args.input_dt = parse_num(args.input_dt, dtype='float') * 60. #convert input_dt to seconds

    #output dates
    if args.output_t0 is None:
        args.output_t0 = args.input_t0
    else:
        args.output_t0 = to_datetime(args.output_t0)
    if args.output_tf is None:
        args.output_tf = args.input_tf
    else:
        args.output_tf = to_datetime(args.output_tf)
    args.output_dt = parse_num(args.output_dt, dtype='float') * 60. #convert input_dt to seconds


    #make sure 'logs' directory exists and is empty
    if os.path.isdir('logs'):
        os.system('rm -f ./logs/main.log')
        os.system('rm -f ./logs/Worker*')
    else:
        #no need for parallel stuff here but the function already exists and will get the job done.
        dpy.parallel_mkdir('logs')

    
    # initialize logging
    logger = setup_logging(args)

    #log header
    logger.info('')
    logger.info('')
    logger.info('executing python script:  domutils.radar_tools.make_radar_fst.py')
    logger.info('All logs printed to stdout can also be found in ./logs/')
    logger.info('')
    logger.info('')

    logger.info('After parsing, input arguments are:')
    for arg in vars(args):
       logger.info(arg +' = '+ str(getattr(args, arg)))
    logger.info('')
    logger.info('')

    #make list of dates where input radar data is needed and add it to arguments
    t_len = (args.input_tf-args.input_t0) + datetime.timedelta(seconds=1)    #+ 1 second for inclusive end point
    elasped_seconds = t_len.days*3600.*24. + t_len.seconds
    args.input_date_list = [args.input_t0 + datetime.timedelta(seconds=x) for x in np.arange(0,elasped_seconds,args.input_dt)]

    #make list of dates where output radar data is desired
    t_len = (args.output_tf-args.output_t0) + datetime.timedelta(seconds=1)    #+ 1 second for inclusive end point
    elasped_seconds = t_len.days*3600.*24. + t_len.seconds
    args.output_date_list = [args.output_t0 + datetime.timedelta(seconds=x) for x in np.arange(0,elasped_seconds,args.output_dt)]

    # If time interpolated outputs already exists for this period, 
    # they are deleted here along with potentially dangling lock files
    out_file_list = set( [args.output_dir + out_date.strftime(args.tinterpolated_file_struc) for out_date in args.output_date_list] )
    for this_file in out_file_list:
        if os.path.isfile(this_file):
            os.remove(this_file)
        if os.path.isfile(this_file+'.lock'):
            os.remove(this_file+'.lock')

    # initialize dask client if needed
    if args.ncores > 1 :
        client = dask.distributed.Client(processes=True, threads_per_worker=1,n_workers=args.ncores, silence_logs=40)

    #compute motion vectors
    if args.t_interp_method == 'None':
        # No temporal interpolation, only observation processing
        if args.output_date_list != args.input_date_list:
            raise ValueError('Select a time interpolation method if output is desired at times different from input')
        else:
            # 1- process radar file and write output to fst files
            obs_process(args)

    elif args.t_interp_method == 'nowcast':

        # check that interpolation will be possible
        if args.output_date_list[0] < args.input_date_list[0] + + datetime.timedelta(seconds=args.input_dt) :
            raise ValueError('For nowcast interpolation the earliest output time must be at least two input delta_t after the earliest input time')

        ## 1- process radar file and write output to fst files
        output_dir = args.output_dir 
        ## override output dir since in this context these outputs are only intermediate results
        args.output_dir    = output_dir + 'processed/'
        args.processed_dir = args.output_dir
        #obs_process(args)

        ## 2- compute motion vectors associated with processed outputs
        args.motion_vectors_dir = output_dir + 'motion_vectors/'
        #make_motion_vectors(args)

        # 3- use nowcast for time interpolation
        args.output_dir    = output_dir 
        nowcast_t_interp(args)

    else:
        raise ValueError('type of time interpolation not supported.')

    #we are done
    time_stop = time.time()
    logger.info('Python code completed, Runtime was : '+str(time_stop-time_start)+' seconds')


if __name__ == "__main__":     
    main()

