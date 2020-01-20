
def input_data(data_in):
    #make sure input data is of numpy type
    import numpy as np
    from os import linesep as newline

    input_ins = (newline                                                + newline
                +'Instructions: Input data should be a numpy array or ' + newline
                +'something convertible to a numpy array.' + newline)
    if not isinstance(data_in, np.ndarray):
        try:
            data_out = np.atleast_1d(np.asfarray(data_in))
        except:
            err_mess = ( newline+' '                          + newline
                        +'Problem: input data should be convertible to a numpy array.'
                        +input_ins)
            raise TypeError(err_mess)
    else:
        data_out = data_in

    return np.ravel(data_out)


