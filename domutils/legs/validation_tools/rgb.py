def rgb(col_rgb, var_name=None, instructions=None):
    #basics checks on color values and conversion to uint8

    import numpy as np
    from os import linesep as newline
    try: 
        col_rgb_int16 = np.asarray(col_rgb, dtype=np.int16)
    except:
        err_mess      =  newline+' '                               + newline
        if var_name is not None:
            err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
        err_mess     +=('Provided values must be convertible to a numpy integer array.')
        if instructions is not None:
            err_mess += instructions
        raise TypeError(err_mess)

    #check range of values
    if (col_rgb_int16 < 0).any() or (col_rgb_int16 > 255).any():
        err_mess      =  newline+' '                               + newline
        if var_name is not None:
            err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
        err_mess     +=('Invalid value, at least one element smaller than 0 or greater than 255.')
        if instructions is not None:
            err_mess += instructions
        raise ValueError(err_mess)

    #RGB values should come in three
    if np.remainder(col_rgb_int16.size, 3) != 0:
        err_mess      =  newline+' '                               + newline
        if var_name is not None:
            err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
        err_mess     +=('Dimension of color arrays should be multiple of 3.')
        if instructions is not None:
            err_mess += instructions
        raise ValueError(err_mess)

    return col_rgb_int16.astype('uint8')
