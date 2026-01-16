import numpy as np

def latlon_to_unit_sphere_xyz(lon, lat, *, combined=True):
    """
    Convert lon/lat (degrees) to unit-sphere Cartesian coordinates.

    Parameters
    ----------
    lon, lat : array-like
        Longitudes and latitudes in degrees
    combined : bool
        If True, return array (..., 3)
        If False, return x, y, z separately

    Returns
    -------
    xyz or (x, y, z)
    """
    lon = np.deg2rad(lon)
    lat = np.deg2rad(lat)

    clat = np.cos(lat)
    x = clat * np.cos(lon)
    y = clat * np.sin(lon)
    z = np.sin(lat)

    if combined:
        return np.column_stack((x, y, z))
    else:
        return x, y, z


def unit_sphere_xyz_to_latlon(x, y=None, z=None, *, combined=True):
    """
    Convert unit-sphere Cartesian coordinates to lon/lat (degrees).

    Parameters
    ----------
    x, y, z : array-like
        Cartesian coordinates (ignored if combined=True)
    combined : bool
        If True, x is array (..., 3)
        If False, x, y, z are separate arrays
    normalize : bool
        If True, normalize vectors to unit length before conversion

    Returns
    -------
    lon, lat : arrays in degrees
    """
    if combined:
        xyz = np.asarray(x, dtype=np.float64)
        x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    else:
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        z = np.asarray(z, dtype=np.float64)

    lon = np.arctan2(y, x)
    lat = np.arcsin(np.clip(z, -1.0, 1.0))

    return np.rad2deg(lon), np.rad2deg(lat)


