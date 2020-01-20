
def no_unmapped(data, action_record, low_map_obj=None, high_map_obj=None):
    #make sure that all data values have been mapped to a color
    import numpy as np
    import operator
    from os import linesep as newline

    #maximum number of data points to display in error messages
    max_pts = 5

    #from strings to operator
    oper = { ">" : operator.gt, 
             ">=": operator.ge,
             "<" : operator.lt,
             "<=": operator.le}
    
    #indices of all unmapped data points
    inds = np.flatnonzero(action_record == 0) 
    if inds.size != 0 :

        #check if some of the unmapped data are below an exact palette
        low_err_mess = ''
        try:
            low_bound_error = low_map_obj.bound_error
        except:
            low_bound_error = 0
        if low_bound_error == 1:
            low_inds = np.flatnonzero(oper[low_map_obj.oper](data, low_map_obj.val)) 
            unmapped_lows = np.intersect1d(data[inds],data[low_inds])
            if unmapped_lows.size > 0:
                #remaining data pts to check
                inds = np.setdiff1d(inds,low_inds)
                #make error message
                if unmapped_lows.size > max_pts:
                    dots = '...'
                else:
                    dots = ''
                max_ind = min(max_pts, unmapped_lows.size)
                problematic_low_vals = str(unmapped_lows[0:max_ind])

                low_err_mess = ( newline+' '                                                         + newline
                                +'Found data point(s) smaller than the minimum of an exact palette:' + newline
                                +'  '+problematic_low_vals+dots                                      + newline)

        #check if some of the unmapped data are above an exact palette
        high_err_mess = ''
        try:
            high_bound_error = high_map_obj.bound_error
        except:
            high_bound_error = 0
        if high_bound_error == 1:
            high_inds = np.flatnonzero(oper[high_map_obj.oper](data, high_map_obj.val)) 
            unmapped_highs = np.intersect1d(data[inds],data[high_inds])
            if unmapped_highs.size > 0:
                #remaining data pts to check
                inds = np.setdiff1d(inds,high_inds)
                #make error message
                if unmapped_highs.size > max_pts:
                    dots = '...'
                else:
                    dots = ''
                max_ind = min(max_pts, unmapped_highs.size)
                problematic_high_vals = str(unmapped_highs[0:max_ind])

                high_err_mess = ( newline+' '                                                       + newline
                                +'Found data point(s) larger than the maximum of an exact palette:' + newline
                                +'  '+problematic_high_vals+dots                                    + newline)

        err_mess = ''
        if low_err_mess != '' or high_err_mess != '':
            err_mess = (low_err_mess 
                        + high_err_mess
                        + newline +newline
                        + 'One possibility is that the data value(s) exceed the palette'                           + newline
                        +'while they should not.'                                                                  + newline
                        +'   For example: correlation coefficients greater than one.'                              + newline
                        +'   In this case, fix your data.'                                                         + newline
                        +''                                                                                        + newline
                        +'Another possibility is that data value(s) is (are) expected  '                           + newline
                        +'above/below the palette.'                                                                + newline
                        +'In this case:'                                                                           + newline
                        +'  1- Use the "over_under","over_high" or "under_low" keywords to explicitly'             + newline
                        +'     assign a color to data values below/above the palette.'                             + newline
                        +'  2- Assign a color to exception values using the "excep_val" and "excep_col" keywords.' + newline
                        +'     For example: excep_val=-9999., excep_col="red".'                                    + newline)
 
        #additionnal error message if there remains any points
        if inds.size > 0:
            if inds.size > max_pts:
                dots = '...'
            else:
                dots = ''
            max_ind = min(max_pts, inds.size)
            problematic_data_vals = str(data[inds[0:max_ind]])
            err_mess += (newline+' '                                                           + newline
                        +'Found data points that have not been mapped: '                       + newline
                        +'  Data values: '                                                     + newline
                        +'  '+problematic_data_vals+dots                                       + newline
                        +'   Check that the mapping function associated with these data values'+ newline
                        +'   is working appropriately.'                                        + newline)

        #finally raise error
        raise RuntimeError(err_mess)


