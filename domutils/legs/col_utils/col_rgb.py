def col_rgb(col_txt_in, var_name=None, instructions=None):
    #returns rgb value associated with a given color name defined by a string or a list of strings
    from .. import col_utils
    from .. import validation_tools as validate
    from os import linesep as newline

    col_dict = {'light_blue' :  [169, 222, 255],
                'dark_blue' :   [  0,  81, 237],
                'light_purple': [196, 194, 255],
                 'dark_purple': [108,  36,  79],
                'light_green':  [134, 222, 134],
                 'dark_green':  [  0, 134,   0],
                'light_red':    [255, 190, 187],
                 'dark_red':    [158,   0,  13],
                'light_orange': [255, 194, 124],
                 'dark_orange': [255,  86,   0],
                'light_pink':   [255, 217, 255],
                 'dark_pink':   [220,   0, 255],
                'light_brown':  [223, 215, 208],
                 'dark_brown':  [ 96,  56,  19],
                'light_yellow': [255, 245, 169],
                 'dark_yellow': [255, 167,   0],
                'white':        [255, 255, 255],
                'black':        [  0,   0,   0]}

    if isinstance(col_txt_in,str):
        this_col = col_txt_in
        try:
            out_rgb = col_dict[this_col]
        except KeyError :
            if this_col[0:5] == 'grey_' or this_col[0:5] == 'gray_':
                #deal with grey_* colors
                col_n = int(this_col[5:])
                out_rgb = [col_n,col_n,col_n]
            else:
                err_mess      =  newline+' '                               + newline
                if var_name is not None:
                    err_mess +='Problem with the keyword "'+var_name+'"'   + newline
                err_mess     +='The color "'+this_col+'" is not supported.'+ newline 
                if instructions is not None:
                    err_mess += instructions
                raise ValueError(err_mess)
    elif isinstance(col_txt_in,list):
        out_rgb = []
        #insure all elements of col_txt_in are strings
        for this_col in col_txt_in:
            if not isinstance(this_col, str):
                err_mess      =  newline+' '                                      + newline
                if var_name is not None:
                    err_mess +=('Problem with the keyword "'+var_name+'"'         + newline)
                err_mess     +=('One element of the list provided is not a string'+ newline)
                if instructions is not None:
                    err_mess += instructions
                raise TypeError(err_mess)
        #conversion from txt to rgb
        for this_col in col_txt_in:
            try:
                out_rgb.append(col_dict[this_col])
            except KeyError :
                if this_col[0:5] == 'grey_' or this_col[0:5] == 'gray_':
                    #deal with grey_* colors
                    col_n = int(this_col[5:])
                    out_rgb.append([col_n,col_n,col_n])
                else:
                    err_mess      =  newline+' '                               + newline
                    if var_name is not None:
                        err_mess +='Problem with the keyword "'+var_name+'"'   + newline
                    err_mess     +='The color "'+this_col+'" is not supported.'+ newline 
                    if instructions is not None:
                        err_mess += instructions
                    raise ValueError(err_mess)
    else:
        if var_name is not None:
            err_mess +='Problem with the keyword "'+var_name+'"'   + newline
        err_mess += 'function "col_rgb" only accepts strings and list of strings.'
        raise TypeError(err_mess)
    
    return validate.rgb(out_rgb)
