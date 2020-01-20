
def over_under_value(value=None,var_name=None,excep_col_ins=''):
    #Keywords "over_under", "over_high" and "under_low" 
    #determine how data values outside palette range are to be treated
    from .. import col_utils
    from .. import validation_tools as validate
    from os import linesep as newline

    if value is None:
        #default
        bound_action = 'exact'
        bound_color  = None
    elif isinstance(value, str):
        if   (value == 'exact'):
            #record action 
            bound_action = value
            bound_color  = None
        elif (value == 'extend'):
            #record action 
            bound_action = value
            bound_color  = None     #color gets assigned later in legs
        else:
            #we may have a named color
            bound_action = 'extend'
            bound_color = col_utils.col_rgb(value, var_name=var_name, instructions=excep_col_ins)
        
    else:
        #we may have a rgb value 
        bound_action = 'extend'
        bound_color = validate.rgb(value, var_name=var_name, instructions=excep_col_ins)

    return bound_action, bound_color


