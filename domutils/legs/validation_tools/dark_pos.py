
def dark_pos(dark_pos,n_col):
    #in the case of semi-continuous palette, dark_pos specifies if the dark color is associated with high or low data value
    from os import linesep as newline

    dark_pos_ins = (newline                                                                                   + newline
                    +'Instructions: the keyword "dark_pos" defines whether the dark color is to be associated'+ newline 
                    +'with high or low data value.        '                                                   + newline 
                    +'It is only meaningful when consructing a continuous or semi-continuous palettes.'       + newline 
                    +'    - The default is to assign dark colors to high data values         '                + newline 
                    +'    - If set to "high" or "low" all legs will be set to the high or low data value'     + newline 
                    +'    - If set to a list of strings,'                                                     + newline 
                    +'                                  e.g. ["high","low"]                     '             + newline 
                    +'      it will determine the position of the dark color for individual legs.'            + newline 
                    +'    In this case, the lenght of the list should be the same as the number of'           + newline 
                    +'    legs in the palette.'                                                               + newline)
    if dark_pos is None :
        #dark_pos not set ; default is to assign dark colors to high data values
        dark_lh = ['high'] * n_col  #replicate 'high' n_col times
    elif isinstance(dark_pos, str):
        if (dark_pos == 'high'):
            dark_lh = ['high'] * n_col 
        elif (dark_pos == 'low'):
            dark_lh = ['low'] * n_col 
        else:
            err_mess = ( newline+' '                              + newline
                        +'Problem with the keyword "dark_pos"'    + newline
                        +'It can only be set to "high" or "low".' 
                        +dark_pos_ins)
            raise ValueError(err_mess)
    elif isinstance(dark_pos, list):
        #ensure entries are all string
        err_mess = ( newline+' '                              + newline
                    +'Problem with the keyword "dark_pos"'    + newline
                    +'It can only be a string or list of strings set to "high" or "low".' 
                    +dark_pos_ins)
        for item in dark_pos:
            if not isinstance(item, str):
                raise TypeError(err_mess)
            if not ((item == 'high') or (item == 'low')):
                raise ValueError(err_mess)
        #check number of elements
        if (len(dark_pos) != n_col):
            err_mess = ( newline+' '                              + newline
                        +'Problem with the keyword "dark_pos"'    + newline
                        +'It must have same dimension as the number of legs in palette.' 
                        +dark_pos_ins)
            raise ValueError(err_mess)
        #all tests passed
        dark_lh = dark_pos
    else:
        err_mess = ( newline+' '                              + newline
                    +'Problem with the keyword "dark_pos"'    + newline
                    +'It can only be a string or list of strings set to "high" or "low".' 
                    +dark_pos_ins)
        raise TypeError(err_mess)

    #default behavior is to have dark color associated with index 0 of color array
    #dark_flip is true for legs where dark and light colors must be flipped with one another
    #indices for when legs
    dark_flip = [ val == 'low' for val in dark_lh ]
    return dark_flip


