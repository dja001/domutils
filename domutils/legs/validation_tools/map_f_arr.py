
def map_f_arr(map_f_arr=None,n_col=None,solid=None):
    #name of the method performing the mapping between data values and RGB values
    from os import linesep as newline

    map_f_arr_ins = (newline                                                                                       + newline
                     +'Instructions: the keyword "map_f_arr" defines the function that performs the mapping '      + newline 
                     +'between data values and RGB values.'                                                        + newline 
                     +'  1- If it is a string, the function will be used for all color legs of a palette. '        + newline 
                     +'  2- If it is a list of strings, it defines the mapping function for each individual legs.' + newline 
                     +'     In this case, the dimension of "map_f_arr has to match the number of color legs.'      + newline 
                     +'  The default behavior is to use the "linmap" function.  '                                  + newline 
                     +'  When the "solid" keyword is set, the "within" function is used instead. '                 + newline)
    #map_f_arr contains the mapping function for each leg
    #note how the solid keyword is simply a shortcut for specifying color_arr and map_f_arr at the same time.
    if map_f_arr is None :
        #map_f_arr is not set, use default values
        if solid is not None :
            #solid is set; we are making a categorical palette
            if (solid == 'supplied') or (solid == 'col_light') or (solid == 'col_dark'):
                map_f_arr_out = ['within'] * n_col
            else:
                err_mess = ( newline+' '                              + newline
                            +'Problem with the keyword "map_f_arr"'   + newline
                            +'Code should never get here if the "solid" keyword was properly validated before.'
                            +map_f_arr_ins)
                raise ValueError(err_mess)
        else:
            #solid is not set use linear mapping as default
            map_f_arr_out = ['linmap'] * n_col
    elif isinstance(map_f_arr, str):
        #use provided function for all legs
        map_f_arr_out = [map_f_arr] * n_col
    elif isinstance(map_f_arr, list):
        #check number of elements
        if (len(map_f_arr) != n_col):
            err_mess = ( newline+' '                              + newline
                        +'Problem with the keyword "map_f_arr"'   + newline
                        +'The dimension of "map_f_arr has to match the number of color legs.'
                        +map_f_arr_ins)
            raise ValueError(err_mess)
        #check type
        for item in map_f_arr:
            if not isinstance(item, str):
                err_mess = ( newline+' '                              + newline
                            +'Problem with the keyword "map_f_arr"'   + newline
                            +'Keyword "map_f_arr" can only be a string or a list of strings'
                            +map_f_arr_ins)
                raise TypeError(err_mess)
        #all tests passed
        map_f_arr_out = map_f_arr
    else:
        err_mess = ( newline+' '                              + newline
                    +'Problem with the keyword "map_f_arr"'   + newline
                    +'Keyword "map_f_arr" can only be a string or a list of strings'
                    +map_f_arr_ins)
        raise TypeError(err_mess)

    return map_f_arr_out


