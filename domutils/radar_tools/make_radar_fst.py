
#identify logger names based on package hierarchy
logging_basename = 'domutils.radar_tools'


def multi_to_fst(*args, **kwargs):
    import sys
    import logging
    import multiprocessing

    #logger name is the same for all workers
    process_logger = logging.getLogger()

    #add handlers if none are present for this worker
    if not len(process_logger.handlers):
        command_line_args = args[2]
        process_logger.setLevel(command_line_args.log_level)
        logging.captureWarnings(True)
        #handlers
        worker_id = str(multiprocessing.current_process().name)
        stream_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler('logs/'+worker_id, 'w')
        #levels
        stream_handler.setLevel(command_line_args.log_level)
        file_handler.setLevel(command_line_args.log_level)
        #format
        formatter_stream = logging.Formatter(worker_id+'    %(message)s')
        stream_handler.setFormatter(formatter_stream)
        formatter_file= logging.Formatter('%(asctime)s - %(name)s in %(funcName)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter_file)
        #add handlers
        process_logger.addHandler(stream_handler)
        process_logger.addHandler(file_handler)

    return to_fst(*args, **kwargs)


def to_fst(valid_date, fst_template, args):
    #output data to std file

    import os
    import time
    import copy
    import logging
    import numpy as np
    import rpnpy.librmn.all as rmn
    from rpnpy.rpndate import RPNDate
    from domutils import radar_tools
    import domutils._py_tools as dpy

    logger = logging.getLogger()
    logger.info('to_fst starting to process date: '+str(valid_date))

    #output filename and directory
    output_file = args.output_dir + valid_date.strftime(args.fst_file_struc)
    #if in complete mode and file exists, return and test next one
    if (os.path.isfile(output_file) and args.complete_dataset):
        logger.info(output_file+ ' exists and complete_dataset=True. Skipping to the next.')
        return np.array([1])
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
        logger.warning('no data found or file unreadeable, I observations are set to -9999. with quality index = 0.')
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

    #prepare std objects
    #cmc timestamp
    date_obj = RPNDate(valid_date)
    cmc_timestamp = date_obj.datev

    #open fst file
    logger.info('writing ' + output_file)
    iunit = rmn.fstopenall(output_file,rmn.FST_RW)

    #write >> ^^ to output file
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

    rmn.fstecr(iunit, rdpr_entry)
    rmn.fstecr(iunit, rdqi_entry)

    #close file
    rmn.fstcloseall(iunit)

    logger.info('Done writing ' + output_file)

    #make a figure for this std file if the argument figure_dir was provided
    if args.figure_dir is not None:
        radar_tools.plot_rdpr_rdqi(fst_file=output_file, 
                                   this_date=valid_date,
                                   fig_dir=args.figure_dir,
                                   fig_format=args.figure_format,
                                   args=args)

    return np.array([1])



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


def make_fst(t0, tf, dt, args):
    """ read odim H5, manipulate it, and write to fst

    depending on the number of cpus, serial execution or parallel execution with multiprocessing will be chosen 
    """

    import os
    import datetime
    import glob
    import logging
    import signal
    import multiprocessing

    import numpy as np

    from domcmc import fst_tools


    #logging
    logger = logging.getLogger(logging_basename)

    #make list of dates where radar data is needed
    t_len = (tf-t0) + datetime.timedelta(seconds=1)    #+ 1 second for inclusive end point
    elasped_seconds = t_len.days*3600.*24. + t_len.seconds
    date_list = [t0 + datetime.timedelta(seconds=x) for x in np.arange(0,elasped_seconds,dt)]

    logger.info('getting output domain from: '+ args.sample_pr_file)
    fst_template = fst_tools.get_data(args.sample_pr_file, var_name='PR', latlon=True)
    if fst_template is None:
        raise ValueError('Problem getting PR from: ',args.sample_pr_file )

    #if only 1 cpu, do serial execution in a for loop
    # makes for easier debugging 
    if args.ncores == 1 :
        #serial execution
        logger.info('Launching SERIAL execution of code')
        for this_date in date_list:
            to_fst(this_date, fst_template, args)
    else :
        #parallel conversion with nultiprocessing
        logger.info('Launching PARALLEL execution of code with multiprocessing')

        #setup parallel submission
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(args.ncores)
        signal.signal(signal.SIGINT, original_sigint_handler)

        #function that gets called when something goes wrong in the poop
        def kill_pool(err_msg):
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('Error message from failing task:')
            print(err_msg)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            pool.terminate()
        
        #jobs are launched in parallel
        res_list = []
        for this_date in date_list:
            res_list.append(
                    pool.apply_async( multi_to_fst, 
                                      args=(this_date, fst_template, args), 
                                      error_callback=kill_pool,
                                    ) 
                )

        #get results
        results = np.asarray([_res.get() for _res in res_list])

        # Normal termination
        pool.close()
        pool.join()

        # check that we received all correct termination
        if results.sum() != len(date_list) :
            print(results)
            print(len(date_tup_list))
            raise RuntimeError('did not receive correct termination from all processes')


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
                --output_dt        10                                                                         \
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
    import logging
    import domutils._py_tools as dpy


    #keep track of runtime
    time_start = time.time()

    #parse arguments
    desc="read radar H5 files, interpolate/smooth and write to FST"
    parser = argparse.ArgumentParser(description=desc, 
             prefix_chars='-+', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--radar_data_dir"   , type=str,   required=True,  help="path of source radar mosaics files")
    parser.add_argument("--output_dir"       , type=str,   required=True,  help="directory for output fst files")
    parser.add_argument("--fst_file_struc"   , type=str,   required=True,  help="strftime syntax for constructing fst filenames")
    parser.add_argument("--h5_file_struc"    , type=str,   required=True,  help="strftime syntax for constructing H5  filenames")
    parser.add_argument("--h5_latlon_file"   , type=str,   required=False, help="Pickle file containing the lat/lons of the Baltrad grid")
    parser.add_argument("--t0"               , type=str,   required=True,  help="yyyymmsshhmmss begining time; datestring")
    parser.add_argument("--tf"               , type=str,   required=False, help="yyyymmsshhmmss end      time; datestring")
    parser.add_argument("--fcst_len"         , type=float, required=False, help="duration of forecast (hours)")
    parser.add_argument("--accum_len"        , type=str,   required=False, help="duration of accumulation (minutes)")
    parser.add_argument("--output_dt"        , type=str,   required=True,  help="interval (minutes) between output radar mosaics")
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
    t0 = to_datetime(args.t0)
    if args.tf is not None:
        #if tf provided use it
        tf = to_datetime(args.tf)
    else:
        #otherwise get it from fcst len
        tf = t0 + datetime.timedelta(seconds=args.fcst_len*3600.)

    dt = parse_num(args.output_dt) * 60. #convert dt to seconds



    #make sure 'logs' directory exists and is empty
    if os.path.isdir('logs'):
        os.system('rm -f ./logs/main.log')
        os.system('rm -f ./logs/ForkPoolWorker*')
    else:
        #no need for parallel stuff here but the function already exists and will get the job done.
        dpy.parallel_mkdir('logs')

    # logging is configured to write everything to stdout in addition to a log file
    # in a 'logs' directory
    logging.captureWarnings(True)
    logger = logging.getLogger(logging_basename)
    logger.setLevel(args.log_level)
    #handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('logs/main.log', 'w')
    #levels
    stream_handler.setLevel(args.log_level)
    file_handler.setLevel(args.log_level)
    #format
    formatter = logging.Formatter('%(asctime)s - %(name)s in %(funcName)s - %(levelname)s - %(message)s')
    
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    #add handlers
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)



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


    #make std files
    make_fst(t0, tf, dt, args)

    #we are done
    time_stop = time.time()
    logger.info('Python code completed, Runtime was : '+str(time_stop-time_start)+' seconds')


if __name__ == "__main__":     
    main()

