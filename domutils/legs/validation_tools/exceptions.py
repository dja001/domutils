
def exceptions(excep_val=None, excep_tol=None, excep_col=None,default_excep_col='black'):
    #excep_val contain data values that should be treated as exceptions
    import numpy as np
    from os import linesep as newline
    from .. import col_utils
    from .. import validation_tools as validate

    excep_val_ins = (newline                                                                    + newline
                    +'Instructions: the keyword "excep_val" must be an array of data values to '+ newline
                    +'              which special colors will be assigned.')
    #excep_tol is an optional keyword that specifies the tolerance within which a data value is considered an exception
    excep_tol_ins = (newline                                                                    + newline
                    +'Instructions: the keyword "excep_tol" must be an array of data values describing '+ newline
                    +'              the tolerance on exceptino values.'                                 + newline
                    +'                          e.g. exception_range = exception_val +- exception_tol'  + newline
                    +'              In general, "excep_tol" must have the same dimension as excep_val.' + newline
                    +'              If "excep_tol" has only one element, it will be used for all exceptions.')
    #excep_col defines the color used for each exception
    excep_col_ins = (newline                                                                                             + newline
                    +'Instructions: the keyword "excep_col" must be '                                                    + newline 
                    +'    1- A string describing a named colors: eg:  "dark_red"'                                        + newline 
                    +'       This color will be assigned to all exceptions.'                                             + newline 
                    +'    2- A 1D array of named colors:         eg: ["dark_red"   ,"dark_blue"  , ... , "dark_green" ] '+ newline 
                    +'    3- A 2D array of rgb   colors:         eg: [[000,000,255],[000,255,000], ... , [000,000,255]] '+ newline 
                    +'For cases 2 and 3, the number of colors represented must be the same as the number of exceptions  '+ newline
                    + 'provided in "excep_val".')

    #default tolerance on exceptions
    default_excep_tol = 1e-3

    #here we validate user input and set some defaults
    if excep_val is not None:
        #generate excep_val_np
        try: 
            excep_val_np = np.atleast_1d(np.asfarray(excep_val))
        except:
            err_mess = ( newline+' '                             + newline
                        +'Problem with the keyword "excep_val"'  + newline
                        +'List values must be convertible to a numpy array.'
                        +excep_val_ins)
            raise TypeError(err_mess)
        n_excep = excep_val_np.size

        #validate excep_tol and set default otherwise
        #generate excep_tol_np
        if excep_tol is None:
            #default
            excep_tol_np = np.full(n_excep, default_excep_tol)
        else:
            try: 
                excep_tol_np = np.atleast_1d(np.asfarray(excep_tol))
            except:
                err_mess = ( newline+' '                             + newline
                            +'Problem with the keyword "excep_tol"'  + newline
                            +'List values must be convertible to a numpy array.'
                            + excep_tol_ins)
                raise TypeError(err_mess)
        if (excep_tol_np.size != n_excep):
            if (excep_tol_np.size == 1):
                #only one tolerance passed, use it for all exceptions
                excep_tol_np = np.full(n_excep, excep_tol_np)
            else:
                err_mess = ( newline+' '                             + newline
                            +'Problem with the keyword "excep_tol"'  + newline
                            +'It should have the same dimension as "excep_val"'
                            + excep_tol_ins)
                raise ValueError(err_mess)

        #validate excep_col and set default otherwise
        if excep_col is None:
            #default
            excep_col = [default_excep_col] * n_excep    #python list multiplication is NOT element wise mult
            excep_col_rgb = col_utils.col_rgb(excep_col,var_name='excep_col', instructions=excep_col_ins)
        elif isinstance(excep_col, str):
            excep_col_ex = [excep_col]*n_excep
            excep_col_rgb = col_utils.col_rgb(excep_col_ex, var_name='excep_col', instructions=excep_col_ins)
        elif isinstance(excep_col, list):
            if isinstance(excep_col[0], str):
                #first entry is a string ; make sure all other entries are strings
                for this_col in excep_col:
                    if not isinstance(this_col, str):
                        err_mess = ( newline+' '                             + newline
                                    +'Problem with the keyword "excep_col"'  + newline
                                    +'Invalid element in input list.'
                                    +excep_col_ins)
                        raise TypeError(err_mess)
                if len(excep_col) != n_excep:
                    err_mess = ( newline+' '                             + newline
                                +'Problem with the keyword "excep_col"'  + newline
                                +'The number of colors for exception values should match the number of exceptions'
                                +excep_col_ins)
                    raise ValueError(err_mess)
                excep_col_rgb = col_utils.col_rgb(excep_col, var_name='excep_col', instructions=excep_col_ins)
            else:
                #RGB values are passed
                #basic checks and conversion to uint8
                excep_col_rgb = validate.rgb(excep_col, var_name='excep_col', instructions=excep_col_ins)

                #check number of elements, repeat if needed
                n_excep_col = excep_col_rgb.size
                if n_excep_col / 3 == 1 :
                    excep_col_rgb = np.tile(excep_col_rgb,[n_excep,1])
                elif n_excep_col / 3 != n_excep :
                    err_mess = ( newline+' '                             + newline
                                +'Problem with the keyword "excep_col"'  + newline
                                +'The number of colors for exception values should match the number of exceptions'
                                +excep_col_ins)
                    raise ValueError(err_mess)

        else:
            err_mess = ( newline+' '                             + newline
                        +'Problem with the keyword "excep_col"'  + newline
                        +'Invalid element in input list.'
                        +excep_col_ins)
            raise TypeError(err_mess)
        
    else:
        #no exceptions specified
        n_excep = np.array([0.])
        excep_val_np =None
        excep_tol_np =None
        excep_col_rgb=None

    return n_excep, excep_val_np, excep_tol_np, excep_col_rgb
        

