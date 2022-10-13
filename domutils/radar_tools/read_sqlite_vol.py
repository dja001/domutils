from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def read_sqlite_vol(sqlite_file:      str=None,
                    latlon:           Optional[bool] = False,
                    radars:           Optional[Any]  = 'all',
                    vol_scans:        Optional[Any]  = 'all',
                    elevations:       Optional[Any]  = 'all',
                    quantities:       Optional[Any]  = 'all',
                    preserve_sqlite_structure:  Optional[bool] = False,
                    no_data:          Optional[float]= -9999.,
                    undetect:         Optional[float]= -3333.) :

    """ Read reflectivity and quality index from sqlite files destined to midas
        
    This code is for Volume scans in the sqlite files destines for data assimilation.

    For more verbose outputs, set logging level in calling handler

    Args:
        sqlite_file:      /path/to/sqlite_file.sqlite
        latlon:           When true, will output latitudes, longitudes and height above ground (4/3Re) of the returned PPIs
        elevations:       float or list of float for the desired nominal elevation. Set to 'all' to return all elevations in a file
        quantities:       desired quantities has to match column name in body table of sqlite files
                          (ie 
        no_data:          Value that will be assigned to missing values
        undetect:         Value that will be assigned to valid measurement of no precipitation

    Returns:

        a dict::

            # a dictionary which roughly mimics the structure of odim h5 files::
            # dict['elevation1']['quantity1'](2D numpy array, PPI) 
            #                   ['quantity2'](2D numpy array, PPI)
            #                      ...
            #                   ['quality_name1'](2D numpy array, PPI)
            #                   ['quality_name2'](2D numpy array, PPI)
            #                      ...
            #                   [nominal_elevation] float
            #                   [elevations] (1D numpy array, rows of values)
            #                   [azimuths]   (1D numpy array, rows of values)
            #                   [ranges]     (1D numpy array, columns of values)
            #                   [latitudes]  (2D numpy array)
            #                   [longitudes] (2D numpy array)
            # dict['elevation2']['quantity1'](2D numpy array)
            #                     ...
        or

        None:             If no or invalid file present, desires elevation or quantities not found.

    Example:

        >>> #read sqlite file
        >>> import os, inspect
        >>> import domutils.radar_tools as radar_tools
        >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
        >>> sqlite_file = parentdir+'/test_data/sqlite_radar_volume_scans/2019071118_ra'
        >>> res = radar_tools.read_sqlite_vol(sqlite_file=sqlite_file, 
        ...                                   elevations=[0.4], 
        ...                                   latlon=True)
        >>> #check returned radar dictionary
        >>> print(res.keys())
        dict_keys(['radar_height', 'radar_lat', 'radar_lon', 'date_str', '0.4'])
        >>> #
        >>> #check returned PPI dictionary
        >>> print(res['0.4'].keys())
        dict_keys(['dbzh', 'quality_beamblockage', 'quality_att', 'quality_broad', 'quality_qi_total', 'nominal_elevation', 'elevations', 'azimuths', 'ranges', 'latitudes', 'longitudes', 'm43_heights'])



    """
    import os, inspect
    import datetime
    import logging
    import pickle
    import time
    import numpy as np
    import pandas as pd
    import sqlite3
    import warnings
    import domutils.radar_tools as radar_tools
    import domutils.geo_tools   as geo_tools

    #logging
    logger = logging.getLogger()

    #checks that filename was provided and is valid
    if sqlite_file is None :
        raise ValueError('sqlite_file must be provided')
    else :
        if not os.path.isfile(sqlite_file) :
            #no file present print warning and return None
            logger.warning('sqlite_file: ' + sqlite_file + ' does not exist. Returning None.')
            return None


    #read the header table
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.row_factory = sqlite3.Row

    #
    #
    # Read header entries in sqlite file
    #
    query = (  'select DATE, TIME, ID_STN, LAT, LON, ANTENNA_ALTITUDE, NOMINAL_PPI_ELEVATION from header ;')
    c.execute(query)
    entries = c.fetchall()


    #
    #
    # Quantities to retrive in data table
    cursor = conn.execute('select * from data')
    column_names_in_files = [desc[0] for desc in cursor.description]
    logger.info(f'Available column names in file data table: {column_names_in_files}')
    if quantities == 'all':
        quantities_to_retrieve = column_names_in_files
    else:
        quantities_to_retrieve = []
        for this_quantity in quantities:
            if this_quantity in column_names_in_files:
                quantities_to_retrieve.append(this_quantity)
            else:
                logger.warning(f'desired quantity "{this_quantity}" is not in "{column_names_in_files}"')
    #some stuff we never want for output
    never_wanted = ['ID_DATA', 'ID_OBS', 'HALF_DELTA_RANGE', 'HALF_DELTA_AZIMUTH']
    for element in never_wanted:
        if element in quantities_to_retrieve:
            quantities_to_retrieve.remove(element)
    #other stuff, we always want to output
    always_wanted = ['ID_OBS', 'RANGE', 'HALF_DELTA_RANGE', 'HALF_DELTA_AZIMUTH']
    for element in always_wanted:
        if element not in quantities_to_retrieve:
            quantities_to_retrieve.append(element)

    logger.info('Reading: ' + str(quantities_to_retrieve) +' from: ' + sqlite_file)


    #
    #
    #make list of all radars available in file
    radars_in_file = {}
    for entry in entries:
        this_radar = entry['ID_STN']
        if this_radar not in radars_in_file :
            radars_in_file[this_radar] = {}
            radars_in_file[this_radar]['radar_lat']    = entry['LAT']
            radars_in_file[this_radar]['radar_lon']    = entry['LON']
            radars_in_file[this_radar]['radar_height'] = entry['ANTENNA_ALTITUDE']
    #restrict our reading to one or a few radars if required
    if radars == 'all' :
        radar_dict = radars_in_file
    else:
        radar_dict = {} 
        for this_radar in radars:
            if this_radar in radars_in_file.keys():
                radar_dict[this_radar] = radars_in_file[this_radar]
            else:
                warnings.warn(f'desired radar {this_radar} is not in file')

    #
    #
    #make list of volume scans in file
    vol_scan_in_file = []
    for entry in entries:
        if entry['ID_STN'] in radar_dict.keys():
            vol_scan_date = str(entry['DATE']).zfill(6) + str(entry['TIME']).zfill(6)
            if vol_scan_date not in vol_scan_in_file :
                vol_scan_in_file.append(vol_scan_date)
    #convert strings to datetime
    vol_scan_in_file = [ datetime.datetime.strptime(this_str,"%Y%m%d%H%M%S" ) for this_str in vol_scan_in_file ]
    vol_scan_in_file.sort()
    #logger.info('Available volume scan date(s) in file:')
    #for date in vol_scan_in_file:
    #    logger.info(date)
    #restrict our reading to one or a few volume scan times if required
    if vol_scans == 'all' :
        vol_scan_list = vol_scan_in_file
    else:
        vol_scan_list = []
        for this_vol_scan in vol_scans:
            if this_vol_scan in vol_scan_in_file:
                vol_scan_list.append(this_vol_scan)
            else:
                warnings.warn(f'desired vol_scan {this_vol_scan} is not in file')
    #sort list of volume scan time for prettier outputs
    vol_scan_list.sort()


    #
    #
    #make list of nominal elevations to retrieve
    elev_format = '{:4.1f}'
    elevs_in_file = []
    for entry in entries:
        if entry['ID_STN'] in radar_dict.keys():
            this_elevation    = elev_format.format(entry['NOMINAL_PPI_ELEVATION']).strip()
            if this_elevation not in elevs_in_file:
                elevs_in_file.append(this_elevation)
    #restrict our reading to one or a few PPIs if required
    if elevations == 'all' :
        elevation_list = elevs_in_file
    else:
        #check that desired elevations are present in the file
        elevation_list = []
        for this_elevation in elevations :
            elev_string = elev_format.format(this_elevation).strip()
            if elev_string in elevs_in_file:
                elevation_list.append(elev_string)
            else:
                warnings.warn(f'desired elevation {this_elevation} is not in file')
    #sort list of nominal elevations for prettier outputs
    elevation_float = np.sort(np.array(elevation_list,dtype=float))
    elevation_list = [ f'{this_elevation:.1f}' for this_elevation in elevation_float]

    #
    #
    #Some info on what is available when
    for this_radar in radar_dict.keys():
        for this_time in vol_scan_list:
            yyyymodd = this_time.strftime("%Y%m%d")
            hhmiss   = this_time.strftime("%H%M%S")
            #get elevations at this time
            query = (f'select NOMINAL_PPI_ELEVATION from header '
                     f'where ID_STN == "{this_radar}" '
                     f'and DATE == {yyyymodd} '
                     f'and TIME == {hhmiss}; '
                    )
            c.execute(query)
            elevations = c.fetchall()
            if len(elevations) == 0:
                warnings.warn('No elevations for query:'+query+' Something weird is going on.')
            else:
                elev_list = []
                for this_elev in elevations:
                    elev_rounded = np.round(this_elev['NOMINAL_PPI_ELEVATION']*100.)/100.
                    if not np.any(np.isclose(np.array(elev_list), elev_rounded)):
                        elev_list.append(elev_rounded)
            print(this_radar, this_time, 'elevs: ', np.sort(elev_list))

    #Fill output dictionary reconstructing one PPI at a time.
    output_is_empty = True
    out_dict = {}
    for this_radar in radar_dict.keys():
        out_dict[this_radar] = {}

        #radar info
        out_dict[this_radar]['radar_lat']    = radar_dict[this_radar]['radar_lat']
        out_dict[this_radar]['radar_lon']    = radar_dict[this_radar]['radar_lon']
        out_dict[this_radar]['radar_height'] = radar_dict[this_radar]['radar_height']

        for this_time in vol_scan_list:
            yyyymodd = this_time.strftime("%Y%m%d")
            hhmiss   = this_time.strftime("%H%M%S")
            out_dict[this_radar][this_time] = {}
            
            for nominal_elevation in elevation_list:

                small = 1e-3
                elev_low_bound  = float(nominal_elevation)-small
                elev_high_bound = float(nominal_elevation)+small
                #header tables
                query = (f'select ID_OBS, LAT, LON, CENTER_ELEVATION, CENTER_AZIMUTH, RANGE_START, RANGE_END, NOMINAL_PPI_ELEVATION from header '
                         f'where ID_STN == "{this_radar}" '
                         f'and DATE == {yyyymodd} '
                         f'and TIME == {hhmiss} '
                         f'and NOMINAL_PPI_ELEVATION > {elev_low_bound} and NOMINAL_PPI_ELEVATION < {elev_high_bound} ; ')
                c.execute(query)
                headers = c.fetchall()
                if len(headers) == 0:
                    warnings.warn('No results for query:'+query+'   skipping')
                else:
                    output_is_empty = False

                #figure out azimuths, elevations and id_obs for this PPI
                id_obs_arr      = np.zeros(len(headers), dtype=int)
                azimuth_in_ppi  = np.zeros(len(headers))
                elevation_in_ppi= np.zeros(len(headers))
                range_start_arr = np.zeros(len(headers))
                range_stop_arr  = np.zeros(len(headers))
                #delta_range_arr = np.zeros(len(headers))
                for ii, entry in enumerate(headers):
                    #record id_obs for sql query
                    id_obs_arr[ii] = entry['id_obs']

                    #record azimuth
                    azimuth_in_ppi[ii] = entry['CENTER_AZIMUTH']

                    #record elevation
                    elevation_in_ppi[ii] = entry['CENTER_ELEVATION']

                    #range info
                    range_start_arr[ii] = entry['RANGE_START']
                    range_stop_arr[ii]  = entry['RANGE_END']
                    #delta_range_arr[ii] = entry['rdel']

                #indices for an ordered PPI
                az_inds = np.argsort(azimuth_in_ppi)
                id_obs_arr         =       id_obs_arr[az_inds]
                azimuth_in_ppi     =   azimuth_in_ppi[az_inds]
                elevation_in_ppi   = elevation_in_ppi[az_inds]
                #delta_range_arr    =  delta_range_arr[az_inds]

                #read entries in data table with valid id_obs
                id_obs_query = '('+ ', '.join([ f'{id_obs}' for id_obs in id_obs_arr])+')'
                #columns to retrieve
                data_columns_str = ', '.join(quantities_to_retrieve)
                query = f'select {data_columns_str} from data where id_obs in {id_obs_query};'
                df = pd.read_sql(query, conn)

                #prepare output dictionary for this ppi
                out_dict[this_radar][this_time][nominal_elevation] = {}

                #sometimes, we want to preserve the "ray" based structure of sqlite files
                if preserve_sqlite_structure:
                    out_dict[this_radar][this_time][nominal_elevation]['azimuths']   = azimuth_in_ppi
                    out_dict[this_radar][this_time][nominal_elevation]['elevations'] = elevation_in_ppi
                    out_dict[this_radar][this_time][nominal_elevation]['id_obs_arr'] = id_obs_arr

                    #fill output dictionary respecting sqlite 'ray' based structure
                    for id_obs in id_obs_arr:
                        out_dict[this_radar][this_time][nominal_elevation][id_obs] = {}
                        ray = df.loc[df['ID_OBS'] == id_obs]
                        out_dict[this_radar][this_time][nominal_elevation][id_obs]['ranges']              = ray['RANGE'].to_numpy()
                        out_dict[this_radar][this_time][nominal_elevation][id_obs]['half_delta_ranges']   = ray['HALF_DELTA_RANGE'].to_numpy() 
                        out_dict[this_radar][this_time][nominal_elevation][id_obs]['half_delta_azimuths'] = ray['HALF_DELTA_AZIMUTH'].to_numpy()
                        for this_quantity in quantities_to_retrieve:
                            out_dict[this_radar][this_time][nominal_elevation][id_obs][this_quantity.lower()] = ray[this_quantity].to_numpy()

                else:
                    #Here, we attemps to build a PPI similar to those usually associated with radar data

                    #minimum delta range and delta azimuths in file
                    min_delta_r  = df['HALF_DELTA_RANGE'].min()
                    min_delta_az = df['HALF_DELTA_AZIMUTH'].min()

                    #determine range and azimuth arrays for PPI
                    #this depends on whether the PPi was averaged or not
                    query = f'select DESCRIPTION from info where NAME == "SUPEROBBING" ;'
                    c.execute(query)
                    superobb_on_off = c.fetchone()
                    if  superobb_on_off is None:
                        #info table missing, assume its averaged
                        superobb_on_off = 'ON'
                    else:
                        superobb_on_off = superobb_on_off[0]
                    if  superobb_on_off == 'ON':
                        averaged_ppi = True

                        #we fill a "high res" PPI looking a lot like the source data
                        delta_azimuth = 0.5 #degrees

                        #range array for this PPI
                        min_range = 0.    #m
                        max_range = 240000.
                        delta_r   = 500

                    elif superobb_on_off == 'OFF':

                        averaged_ppi = False

                        #     
                        min_range    = range_start_arr.min()
                        max_range    = range_stop_arr.max()

                        #get first ray
                        ray = df.loc[df['ID_OBS'] == id_obs_arr[0]]
                        half_delta_ranges   = ray['HALF_DELTA_RANGE'].to_numpy()
                        if np.any(half_delta_ranges == None):
                            raise ValueError('half_delta_range not in sqlite file')
                        [half_delta_r] = np.unique(half_delta_ranges)
                        if half_delta_r.size > 1 :
                            raise ValueError('Only constant delta range supported at the moment')
                        delta_r = half_delta_r * 2.

                        #get delta azimuth
                        half_delta_azimuth = ray['HALF_DELTA_AZIMUTH'].to_numpy()
                        half_delta_azimuth   = [None, None]
                        if np.any(half_delta_azimuth == None):
                            raise ValueError('half_delta_azimuth not in sqlite file')

                    else:
                        raise ValueError('SUPEROBBING may only be set to "ON" of "OFF"')

                    #ranges used in oputput PPI
                    range_bounds_arr = np.arange(min_range, max_range+delta_r, delta_r)
                    range_bin_arr = range_bounds_arr[0:-1] + (range_bounds_arr[1:] - range_bounds_arr[0:-1]) / 2.
                    n_range_bins   = range_bin_arr.size
                    # indices to construct range index = a*range + b 
                    ind_a = n_range_bins / (max_range - min_range)
                    ind_b = -ind_a * min_range

                    #azimuths for output PPI
                    #  Nominal azimuth bins for canadian radars change every 0.a or 1.0 5 deg.     e.g. -> 0.0, 0.5, 1.0, 1.5, etc
                    #  be aware that azimuth start and azimuth stop do not exactly overlap leaving ~0.02 degrees gap between rays
                    #  adding delta_az/2. to our reconstructed azimuths insures that they do not fall in the cracks
                    delta_azimuth = .5
                    azimuth_arr = np.arange(0., 360., delta_azimuth)+delta_azimuth/2.
                    n_azimuths = azimuth_arr.size 


                    #fill output dict for this PPI
                    out_dict[this_radar][this_time][nominal_elevation]['azimuths']   = azimuth_arr
                    out_dict[this_radar][this_time][nominal_elevation]['elevations'] = np.full((n_azimuths,), float(nominal_elevation))
                    out_dict[this_radar][this_time][nominal_elevation]['ranges']     = range_bin_arr
                    #initialize out_dict with nodata for each ppi to fill
                    for this_quantity in quantities_to_retrieve:
                        out_dict[this_radar][this_time][nominal_elevation][this_quantity.lower()] = np.full((n_azimuths, n_range_bins), no_data)

                    #fill output PPI in a manner similar to what we get from odim files
                    for [this_azimuth, actual_elevation, id_obs] in zip(azimuth_in_ppi, elevation_in_ppi, id_obs_arr):
                        #if this_azimuth > .3: 
                            #continue

                        #indices of points in average
                        ray = df.loc[df['ID_OBS'] == id_obs]
                        ranges         = ray['RANGE'].to_numpy()
                        half_delta_ranges   = ray['HALF_DELTA_RANGE'].to_numpy() 
                        half_delta_azimuths = ray['HALF_DELTA_AZIMUTH'].to_numpy()


                        #increasing range
                        for ee, [this_range, half_d_ra, half_d_az] in enumerate(zip(ranges, half_delta_ranges, half_delta_azimuths)):
                            #range index
                            rr_ind = np.logical_and(range_bin_arr >= this_range - half_d_ra, range_bin_arr < this_range + half_d_ra).nonzero()[0]
                            #azimuth index
                            diff_az = (azimuth_arr - this_azimuth)
                            diff_az_180 = np.where(diff_az >= 180., diff_az-360, diff_az)
                            az_ind = (np.isclose(diff_az_180, -half_d_az) | ((diff_az_180 >= -half_d_az) & (diff_az_180 < half_d_az))).nonzero()[0]
                            #combine
                            az_inds, r_inds = np.meshgrid(az_ind, rr_ind, indexing='ij')

                            #print('rr', this_range - half_d_ra, this_range + half_d_ra)
                            #print('RA', this_range)
                            #print('rr_ind', rr_ind)
                            #print('this_azimuth', this_azimuth)
                            #print(diff_az_180)
                            #print('az_ind',az_ind)
                            #print(az_inds)
                            #print(r_inds)
                            #print(actual_elevation)
                            #print()

                            #same elevation is assumed for each ray
                            if ee == 0 :
                            #if np.isclose(this_range, 95000.0):
                                #elevations arr is being filled 
                                #print('')
                                #print('azimuth range id_obs', this_range, id_obs, this_azimuth-half_d_az, this_azimuth+half_d_az, az_ind,ray['OBSVALUE'].iloc[ee]  )
                                ##print('diff_az_180', diff_az_180)
                                ##print(diff_az_180[az_ind])
                                #print('azimuth_arr', diff_az)
                                #print(half_d_az, azimuth_arr[az_ind])
                                out_dict[this_radar][this_time][nominal_elevation]['elevations'][az_ind] = actual_elevation

                            #fill 2D output dict in the same way
                            for this_quantity in quantities_to_retrieve:
                                out_dict[this_radar][this_time][nominal_elevation][this_quantity.lower()][az_inds,r_inds] = ray[this_quantity].iloc[ee]

                    #just testing
                    #out_dict[this_radar][this_time][nominal_elevation]['elevations'] = np.full((n_azimuths, n_range_bins), 20.0)
                    #out_dict[this_radar][this_time][nominal_elevation]['elevations'][0:2,:] = 0.4


                    if latlon:
                        #elevation and ranges as 2D grid
                        elevation_arr = out_dict[this_radar][this_time][nominal_elevation]['elevations']
                        melevs, mranges = np.meshgrid(elevation_arr, range_bin_arr, indexing='ij')

                        #distance following curvature of the earth  /1e3 since this function takes km in
                        dist_earth = radar_tools.model_43(elev=melevs, dist_beam=mranges/1e3, 
                                                          hrad=radar_dict[this_radar]['radar_height']/1e3, 
                                                          want='dist_earth')
                        m43_heights = radar_tools.model_43(elev=melevs, dist_beam=mranges/1e3, 
                                                           hrad=radar_dict[this_radar]['radar_height']/1e3, 
                                                           want='height')
                        #compute the lat/lon values associated with a given PPI
                        longitudes, latitudes = geo_tools.lat_lon_range_az(radar_dict[this_radar]['radar_lon'], 
                                                                           radar_dict[this_radar]['radar_lat'], 
                                                                           dist_earth, 
                                                                           azimuth_arr[:,np.newaxis])
                        #missing data has no elevations
                        longitudes = np.where(np.isclose(melevs,no_data), no_data, longitudes)
                        latitudes  = np.where(np.isclose(melevs,no_data), no_data, latitudes)
                        #save output
                        out_dict[this_radar][this_time][nominal_elevation]['latitudes']   = latitudes
                        out_dict[this_radar][this_time][nominal_elevation]['longitudes']  = longitudes
                        out_dict[this_radar][this_time][nominal_elevation]['m43_heights'] = m43_heights


    #we are done reading the file
    conn.close() 

    if output_is_empty:
        return None
    else:
        return out_dict 

           

if __name__ == "__main__":
    import doctest
    doctest.testmod()
