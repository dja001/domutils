
def range_arr(range_arr=None, n_col=None):
    #range_lh is an nparray containing the boundaries between the different legs
    import numpy as np
    from os import linesep as newline

    range_arr_ins = (newline                                                                     + newline
                    +'Instructions: the keyword "range_arr" must be '                            + newline 
                    +'    1- A two element array describing the maximum and minimum data values' + newline
                    +'       represented by the color palette'                                   + newline
                    +'                                           eg: [0.,1] '                    + newline 
                    +'    2- A n element array describing the data values delimiting the bounds '+ newline 
                    +'       of each color leg.'                                                 + newline 
                    +'                                           eg: [0.,1.,10.,100, ...]'       + newline
                    +'       in this case, the dimension of range_arr should be num colors +1'   + newline) 
    #here, we make range_lh from the range_arr passed by the user
    if range_arr is None:
            if n_col is None:
                #range_arr==None -> use lame default value
                range_lh = np.array([0.,1])
            else:
                range_lh = np.linspace(0., 1, n_col+1)
    else:
        try:
            range_lh = np.asfarray(range_arr)
        except:
            err_mess = ( newline+' '                             + newline
                        +'Problem with the keyword "range_arr"'  + newline
                        +'List values must be convertible to a numpy array.'
                        +range_arr_ins)
            raise TypeError(err_mess)
        n_range = range_lh.size

        if (n_range < 2):
            err_mess = ( newline+' '                             + newline
                        +'Problem with the keyword "range_arr"'  + newline
                        +'It must contain at least two elements.'
                        +range_arr_ins)
            raise ValueError(err_mess)
        elif (n_range == 2):
            if (n_col == 1):
                #range_lh already described the boundaries of the one leg; do nothing
                pass
            elif (n_col > 1):
                #divide range into n_col segments
                range_lh = np.linspace(range_arr[0], range_arr[1], n_col+1)
            else:
                err_mess = ( newline+' '                                                          + newline
                            +'Problem validating the keyword "range_arr"'                         + newline
                            +'n_col should be a positive integer greater than 0, something weird is going on'
                            +range_arr_ins)
                raise ValueError(err_mess)
        else:
            #range for multiple legs were specified, insure compatibility between n_range and n_col
            if (n_range != n_col+1):
                err_mess = ( newline+' '                                                          + newline
                            +'Problem with the keyword "range_arr"'                               + newline
                            +'In this context, the dimension of range_arr should be num colors +1'
                            +range_arr_ins)
                raise ValueError(err_mess)
            #check that range_arr is sorted, it is meaningless otherwise
            for i in range(n_range-1):
                if range_arr[i+1] < range_arr[i] :
                    err_mess = ( newline+' '                                                          + newline
                                +'Problem with the keyword "range_arr"'                               + newline
                                +"Keyword range_arr should be sorted from lowest to largest value."
                                +range_arr_ins)
                    raise ValueError(err_mess)

    return range_lh

