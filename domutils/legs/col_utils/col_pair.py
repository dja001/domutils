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

    #make sure input is of appropriate type
    if isinstance(col_txt_in,list):
        col_txt_list  = col_txt_in
    elif isinstance(col_txt_in,str):
        col_txt_list = [col_txt_in]
    else:
        err_mess = "col_pair only accepts strings and list of strings. "
        raise TypeError(err_mess)

    out_rgb = []
    for this_col in col_txt_list:

        if this_col == 'b_w' :
            #b_w is a special case
            out_rgb.append([col_utils.col_rgb('white'), col_utils.col_rgb('black')])
        elif any(this_col == this_str for this_str in supported_cols):
            #we got a supported color
            out_rgb.append([col_utils.col_rgb('light_'+this_col), col_utils.col_rgb('dark_'+this_col)])
        elif this_col[0:5] == 'grey_' or this_col[0:5] == 'gray_':
            #we got the grey color
            this_rgb = col_utils.col_rgb(this_col)
            out_rgb.append([this_rgb, this_rgb])
        else:
            #color not supported
            err_mess      =  newline+' '                               + newline
            if var_name is not None:
                err_mess +=('Problem with the keyword "'+var_name+'"'   + newline)
            err_mess     +=('The color "'+this_col+'" is not supported.'+ newline 
                           +'Supported colors are:\n"'+'"\n"'.join(supported_cols))
            if instructions is not None:
                err_mess += instructions
            raise ValueError(err_mess)

    #if only one element in list, outer layer of nested list can be removed
    if len(out_rgb) == 1 :
        out_rgb = out_rgb[0]

    return validate.rgb(out_rgb)
