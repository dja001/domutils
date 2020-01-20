
def over_under(over_under=None, under_low=None, over_high=None):
    #Keywords "over_under", "over_high" and "under_low" 
    #determine how data values outside palette range are to be treated
    from os import linesep as newline
    from .. import validation_tools as validate

    excep_col_ins = (newline                                                                                         + newline
                     +'Instructions: the keywords "over_under", "over_high" and "under_low"  '                       + newline
                     +'              determine what colors get assigned to data values outside the palette range. '  + newline
                     +'    The keyword "over_under" is just a shortcut to specify both "over_high" and "under_low"'  + newline 
                     +'    at the same time'                                                                         + newline
                     +'    Accepted values are:'                                                                     + newline
                     +'        1- "exact"           no data values expected beyond the range of the color mapping '  + newline
                     +'                             An error will be raised is such data values are found. '         + newline
                     +'        2- "extend"          lowest and/or highest colors are used for data beyond the range '+ newline
                     +'                             of the color mapping'                                            + newline
                     +'        3- a named color:    eg: "red"  '                                                     + newline
                     +'        4- a rgb color:      eg: [000,000,255]  ')
    
    #boundary conditions
    if over_under is not None:
        if under_low is None:
            (low_action, 
             low_color) = validate.over_under_value(over_under,'over_under',excep_col_ins)
        else:
            err_mess = (newline+' '                                                            + newline
                         +'Problem with the keyword "under_low"'                               + newline
                         +'Keywords "over_under" and "under_low" specified at the same time.'  + newline
                         +'Use only "over_under"  or  "under_low" together with "over_under".'
                         +excep_col_ins)
            raise ValueError(err_mess)

        if over_high is None:
            (high_action, 
             high_color) = validate.over_under_value(over_under,'over_under',excep_col_ins)
        else:
            err_mess = (newline+' '                                                            + newline
                         +'Problem with the keyword "over_high"'                               + newline
                         +'Keywords "over_under" and "under_low" specified at the same time.'  + newline
                         +'Use only "over_under"  or  "under_low" together with "over_under".'
                         +excep_col_ins)
            raise ValueError(err_mess)
    else:
        if under_low is not None:
            (low_action, 
             low_color)      = validate.over_under_value(under_low,'under_low',excep_col_ins)
        else:
            (low_action, 
             low_color)      = validate.over_under_value()

        if over_high is not None:
            (high_action, 
             high_color)     = validate.over_under_value(over_high,'over_high',excep_col_ins)
        else:
            (high_action, 
             high_color)     = validate.over_under_value()

    return high_action, high_color, low_action, low_color


