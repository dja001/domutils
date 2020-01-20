def col_pair(col_txt_in, var_name=None, instructions=None):
    #returns a dark/light pair for a given color for the purpose of building a semi-continuous leg
    from .. import col_utils 
    from .. import validation_tools as validate
    from os import linesep as newline

    supported_cols = ['blue',
                      'purple',
                      'green',
                      'red',
                      'orange',
                      'pink',
                      'brown',
                      'yellow',
                      'b_w']

    if isinstance(col_txt_in,str):
        this_col = col_txt_in
        if not any(this_col == this_str for this_str in supported_cols):
            #color not supported
            err_mess      =  newline+' '                               + newline
            if var_name is not None:
                err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
            err_mess     +=('The color "'+this_col+'" is not supported.'+ newline 
                           +'Supported colors are:\n"'+'"\n"'.join(supported_cols))
            if instructions is not None:
                err_mess += instructions
            raise ValueError(err_mess)
        if this_col == 'b_w' :
            out_rgb = [col_utils.col_rgb('white'), col_utils.col_rgb('black')]
        else:
            out_rgb = [col_utils.col_rgb('light_'+col_txt_in), col_utils.col_rgb('dark_'+col_txt_in)]
    elif isinstance(col_txt_in,list):
        out_rgb = []
        #make sure all elements are strings
        for this_col in col_txt_in:
            if not isinstance(this_col, str):
                err_mess      =  newline+' '                                      + newline
                if var_name is not None:
                    err_mess +=('Problem with the keyword "'+var_name+'"'         + newline)
                err_mess     +=('One element of the list provided is not a string'+ newline)
                if instructions is not None:
                    err_mess += instructions
                raise TypeError(err_mess)

        #make sure names colors are supported
        for this_col in col_txt_in:
            if not any(this_col == this_str for this_str in supported_cols):
                err_mess      =  newline+' '                               + newline
                if var_name is not None:
                    err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
                err_mess     +=('The color "'+this_col+'" is not supported.'+ newline 
                               +'Supported colors are:\n"'+'"\n"'.join(supported_cols))
                if instructions is not None:
                    err_mess += instructions
                raise ValueError(err_mess)
            if this_col == 'b_w' :
                out_rgb.append([col_utils.col_rgb('white'), col_utils.col_rgb('black')])
            else:
                out_rgb.append([col_utils.col_rgb('light_'+this_col), col_utils.col_rgb('dark_'+this_col)])
    else:
        err_mess = "col_pair only accepts strings and list of strings. "
        raise TypeError(err_mess)

    return validate.rgb(out_rgb)
