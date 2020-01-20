
def not_mapped_twice(data, action_record):
    #make sure that no data value have been assigned to more than one color
    import numpy as np
    from os import linesep as newline

    inds = np.flatnonzero(action_record >= 2) 
    if inds.size != 0 :
        max_ind = 5
        if inds.size > max_ind:
            dots = '...'
        else:
            dots = ''
        max_ind = min(max_ind, inds.size)
        problematic_data_vals = str(data[inds[0:max_ind]])
        err_mess = ( newline+' '                           + newline
                    +'Problem encountered during mapping:' + newline
                    +'  Some data values: '                + newline
                    +'  '+problematic_data_vals+dots       + newline
                    +'   have been mapped twice.'          + newline)
        raise RuntimeError(err_mess)


