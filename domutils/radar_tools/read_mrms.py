
from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping

def read_mrms(mrms_file:  str=None,
              quantity:   Optional[str] = 'reflectivity',
              latlon:     Optional[bool] = False,
              no_data:    Optional[float]= -9999.,
              undetect:   Optional[float]= -3333.) :

    """ Read precip_rate from MRMS grib data

    Args:
        grib_file:       /path/to/mrms/file.grib2 
        quantity:        What to retrieve, can be "reflectivity" or "precip_rate"
        latlon:          When true, will output latitudes and longitudes
        no_data:         Value that will be assigned to missing values
        undetect:        Value that will be assigned to valid measurement of no precipitation

    Returns:
        None:            If no or invalid file present

        or 

        { 
            'reflectivity':       (ndarray) 2D reflectivity (conditional on quantity = "reflectivity")
            
            'precip_rate':        (ndarray) 2D reflectivity (conditional on quantity = "precip_rate")

            'total_quality_index':  (ndarray) 2D quality index

            'valid_date':          (python datetime object) date of validity

            'latitudes':          (ndarray) 2d latitudes  of data (conditional on latlon = True)

            'longitudes':         (ndarray) 2d longitudes of data (conditional on latlon = True)
        }

    Example:

           >>> #read mrms file
           >>> import os, inspect
           >>> import domutils.radar_tools as radar_tools
           >>> currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
           >>> parentdir = os.path.dirname(currentdir) #directory where this package lives
           >>> out_dict = radar_tools.read_mrms(parentdir + '/test_data/mrms_grib2/PrecipRate_00.00_20210712-093000.grib2', quantity='precip_rate', latlon=True)
           >>> precip_rate         = out_dict['precip_rate']
           >>> total_quality_index = out_dict['total_quality_index']
           >>> valid_date          = out_dict['valid_date']
           >>> latitudes           = out_dict['latitudes']
           >>> print(precip_rate.shape)
           (3500, 7000)
           >>> print(total_quality_index.shape)
           (3500, 7000)
           >>> print(latitudes.shape)
           (3500, 7000)
           >>> print(valid_date)
           2021-07-12 09:30:00

    """

    import os, inspect
    import datetime
    import logging
    import numpy as np

    #logging
    logger = logging.getLogger()

    #checks that filename was provided and is valid
    if mrms_file is None :
        raise ValueError('mrms_file must be provided')
    else :
        if not os.path.isfile(mrms_file) :
            #no file present print warning and return None
            logger.warning(f'mrms_file: {mrms_file} does not exist. Returning None.')
            return None

    logger.info(f'Reading: {quantity} from: {mrms_file}')

    #check consistency between filename and the quantity that is desired
    if quantity == 'reflectivity':
        if 'Reflectivity' not in os.path.basename(mrms_file):
            raise ValueError(f'Reflectivity must be in filename: {os.path.basename(mrms_file)}')
        unit="dBZ"
        qc_file = mrms_file.replace('Reflectivity', 'RadarQualityIndex')
    elif quantity == 'precip_rate':
        if 'PrecipRate' not in os.path.basename(mrms_file):
            raise ValueError(f'PrecipRate must be in filename: {os.path.basename(mrms_file)}')
        qc_file = mrms_file.replace('PrecipRate', 'RadarQualityIndex')
        unit="mm/h"
    else:
        raise ValueError('quantity may only be "reflectivity" or "precip_rate"')

    #get valid date from filename
    date_string = mrms_file[-21:-6]
    valid_date = datetime.datetime.strptime(date_string, '%Y%m%d-%H%M%S')

    #get values using PySteps reader
    values, _, metadata = import_mrms_grib(mrms_file)
    #assign missing values correctly Nan to missing
    values = np.where(np.isfinite(values), values, no_data)

    #try to read quality index 
    if os.path.isfile(qc_file):
        #quality index file exists:
        quality_index, _, qc_metadata = import_mrms_grib(mrms_file)
        #divide by 200 for values between zero and 1   TODO figure out what is QI....
        logger.warning(f'Dividing quality index by 200 for Qi in the range [0,1], Not too sure what I am doing here...')
        quality_index /= 200.
        #assign Nan to missing
        quality_index = np.where(np.isfinite(quality_index), quality_index, no_data)
    else:
        logger.info(f'mrms quality index file: {qc_file} does not exist. Quality is set to "1" wherever data is valid')
        quality_index = np.where(np.isfinite(values), 1., no_data)

    #construct output dictionary
    out_dict = {quantity:              values,
                'total_quality_index': quality_index,
                'valid_date':          valid_date}

    if latlon : 
        #check that dimension of latlon is the same as that of data
        if metadata['latitudes'].shape != out_dict[quantity].shape :
            raise ValueError('Shape of latitudes not the same as that of data. Something is going wrong.')
        out_dict['latitudes']   = metadata['latitudes']
        out_dict['longitudes']  = metadata['longitudes']


    return out_dict

    











def import_mrms_grib(filename, extent=None, window_size=1, **kwargs):
    """

    This reader was taken from 
    https://github.com/pySTEPS
    Thanks to Andres Perez to pointing me there. 

    This code is under BSD3 license:
    https://tldrlegal.com/license/bsd-3-clause-license-(revised)




    Importer for NSSL's Multi-Radar/Multi-Sensor System
    ([MRMS](https://www.nssl.noaa.gov/projects/mrms/)) rainrate product
    (grib format).

    The rainrate values are expressed in mm/h, and the dimensions of the data
    array are [latitude, longitude]. The first grid point (0,0) corresponds to
    the upper left corner of the domain, while (last i, last j) denote the
    lower right corner.

    Due to the large size of the dataset (3500 x 7000), a float32 type is used
    by default to reduce the memory footprint. However, be aware that when this
    array is passed to a pystep function, it may be converted to double
    precision, doubling the memory footprint.
    To change the precision of the data, use the *dtype* keyword.

    Also, by default, the original data is downscaled by 4
    (resulting in a ~4 km grid spacing).
    In case that the original grid spacing is needed, use `window_size=1`.
    But be aware that a single composite in double precipitation will
    require 186 Mb of memory.

    Finally, if desired, the precipitation data can be extracted over a
    sub region of the full domain using the `extent` keyword.
    By default, the entire domain is returned.

    Notes
    -----
    In the MRMS grib files, "-3" is used to represent "No Coverage" or
    "Missing data". However, in this reader replace those values by the value
    specified in the `fillna` argument (NaN by default).

    Note that "missing values" are not the same as "no precipitation" values.
    Missing values indicates regions with no valid measures.
    While zero precipitation indicates regions with valid measurements,
    but with no precipitation detected.

    Parameters
    ----------
    filename: str
        Name of the file to import.
    extent: None or array-like

        Deactivated in domutils extent always = None


        Longitude and latitude range (in degrees) of the data to be retrieved.
        (min_lon, max_lon, min_lat, max_lat).
        By default (None), the entire domain is retrieved.
        The extent can be in any form that can be converted to a flat array
        of 4 elements array (e.g., lists or tuples).
    window_size: array_like or int

        Deactivated in domutils window_size always = 1

        Array containing down-sampling integer factor along each axis.
        If an integer value is given, the same block shape is used for all the
        image dimensions.
        Default: window_size=4.

    {extra_kwargs_doc}

    Returns
    -------
    precipitation: 2D array, float32
        Precipitation field in mm/h. The dimensions are [latitude, longitude].
        The first grid point (0,0) corresponds to the upper left corner of the
        domain, while (last i, last j) denote the lower right corner.
    quality: None
        Not implement.
    metadata: dict
        Associated metadata (pixel sizes, map projections, etc.).
    """

    del kwargs

    import numpy as np

    try:
        import pygrib
    except ImportError as e:
        raise MissingOptionalDependency(
            "pygrib package is required to import NCEP's MRMS products but it is not installed"
        )

    try:
        grib_file = pygrib.open(filename)
    except OSError:
        raise OSError(f"Error opening NCEP's MRMS file. " f"File Not Found: {filename}")

    if isinstance(window_size, int):
        window_size = (window_size, window_size)

    if extent is not None:
        extent = np.asarray(extent)
        if (extent.ndim != 1) or (extent.size != 4):
            raise ValueError(
                "The extent must be None or a flat array with 4 elements.\n"
                f"Received: extent.shape = {str(extent.shape)}"
            )

    # The MRMS grib file contain one message with the precipitation intensity
    grib_file.rewind()
    grib_msg = grib_file.read(1)[0]  # Read the only message

    # -------------------------
    # Read the grid information

    lr_lon = grib_msg["longitudeOfLastGridPointInDegrees"]
    lr_lat = grib_msg["latitudeOfLastGridPointInDegrees"]

    ul_lon = grib_msg["longitudeOfFirstGridPointInDegrees"]
    ul_lat = grib_msg["latitudeOfFirstGridPointInDegrees"]

    # Ni - Number of points along a latitude circle (west-east)
    # Nj - Number of points along a longitude meridian (south-north)
    # The lat/lon grid has a 0.01 degrees spacing.
    lats = np.linspace(ul_lat, lr_lat, grib_msg["Nj"])
    lons = np.linspace(ul_lon, lr_lon, grib_msg["Ni"])

    precip = grib_msg.values
    no_data_mask = precip == -3  # Missing values

    ## Create a function with default arguments for aggregate_fields
    #block_reduce = partial(aggregate_fields, method="mean", trim=True)

    #if window_size != (1, 1):
    #    # Downscale data
    #    lats = block_reduce(lats, window_size[0])
    #    lons = block_reduce(lons, window_size[1])

    #    # Update the limits
    #    ul_lat, lr_lat = lats[0], lats[-1]  # Lat from North to south!
    #    ul_lon, lr_lon = lons[0], lons[-1]

    #    precip[no_data_mask] = 0  # block_reduce does not handle nan values
    #    precip = block_reduce(precip, window_size, axis=(0, 1))

    #    # Consider that if a single invalid observation is located in the block,
    #    # then mark that value as invalid.
    #    no_data_mask = block_reduce(
    #        no_data_mask.astype("int"), window_size, axis=(0, 1)
    #    ).astype(bool)

    lons, lats = np.meshgrid(lons, lats)
    precip[no_data_mask] = np.nan

    #if extent is not None:
    #    # clip domain
    #    ul_lon, lr_lon = _check_coords_range(
    #        (extent[0], extent[1]), "longitude", (ul_lon, lr_lon)
    #    )

    #    lr_lat, ul_lat = _check_coords_range(
    #        (extent[2], extent[3]), "latitude", (ul_lat, lr_lat)
    #    )

    #    mask_lat = (lats >= lr_lat) & (lats <= ul_lat)
    #    mask_lon = (lons >= ul_lon) & (lons <= lr_lon)

    #    nlats = np.count_nonzero(mask_lat[:, 0])
    #    nlons = np.count_nonzero(mask_lon[0, :])

    #    precip = precip[mask_lon & mask_lat].reshape(nlats, nlons)

    #proj_params = _get_grib_projection(grib_msg)
    #pr = pyproj.Proj(proj_params)
    #proj_def = " ".join([f"+{key}={value} " for key, value in proj_params.items()])

    xsize = grib_msg["iDirectionIncrementInDegrees"] * window_size[0]
    ysize = grib_msg["jDirectionIncrementInDegrees"] * window_size[1]

    #x1, y1 = pr(ul_lon, lr_lat)
    #x2, y2 = pr(lr_lon, ul_lat)

    metadata = dict(
        institution="NOAA National Severe Storms Laboratory",
        xpixelsize=xsize,
        ypixelsize=ysize,
        accutime=2.0,
        transform=None,
        zerovalue=0,
        latitudes=lats, 
        longitudes=lons,
        #projection=proj_def.strip(),
        yorigin="upper",
        #threshold=_get_threshold_value(precip),
        #x1=x1 - xsize / 2,
        #x2=x2 + xsize / 2,
        #y1=y1 - ysize / 2,
        #y2=y2 + ysize / 2,
        cartesian_unit="degrees",
    )

    return precip, None, metadata


if __name__ == "__main__":
    #to run tests, go in domutils and run 
    # python radar_tools/read_h5_composite.py
    import doctest
    doctest.testmod()

