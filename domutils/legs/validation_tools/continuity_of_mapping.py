
def continuity_of_mapping(col_obj):
    #check consistency of mapping object and transforms data values to rgb values
    import numpy as np
    from os import linesep as newline

    #insure that values between -infty and +infty are mapped to a color
    oper_ins = (newline                                                                + newline
                +'Instructions: the operators in a mapping object must insure that ALL'+ newline 
                +'values between -infty and +infty are mapped to a color'              + newline
                +'For example:'                                                        + newline
                +'               |        palette        |              '              + newline
                +'               |           |           |              '              + newline
                +'             bound1      bound2  ... bound_n          '              + newline
                +' low values    <                                      '              + newline
                +'               >=   leg1   <                          '              + newline
                +'                           >=    ...   <=             '              + newline
                +'                                       >  high values '              + newline
                +'is correct.                                           '              + newline
                +'                                                      '              + newline
                +'However:                                              '              + newline
                +'                                                      '              + newline
                +'               |        palette        |              '              + newline
                +'               |           |           |              '              + newline
                +'             bound1      bound2  ... bound_n          '              + newline
                +' low values    <                                      '              + newline
                +'               >=   leg1   <                          '              + newline
                +'                           >=    ...   <              '              + newline
                +'                                       >  high values '              + newline
                +'would yield an error because the data value           '              + newline
                +'for bound_n is not mapped to anything.                '              + newline)
    #low operator
    err_mess = (newline+' '                                         + newline
                +'Problem: incompatibility of operators at bound1.' + newline
                +'The allowed combinations are:                   ' + newline 
                +'    "<"  and ">="                               ' + newline
                +'    or                                          ' + newline
                +'    "<=" and ">"                                ' 
                +oper_ins)
    if col_obj.lows.oper == '<=' :
        if col_obj.cols[0].oper_low != '>' :
            raise ValueError(err_mess)
    elif col_obj.lows.oper == '<':
        if col_obj.cols[0].oper_low != '>=' :
            raise ValueError(err_mess)
    else:
        err_mess = ( newline+' '                          + newline
                    +'Problem with the operator mapping data values below the palette.'  + newline
                    +'only "<" and "<=" are allowed.' 
                    +oper_ins)
        raise ValueError(err_mess)
    #continuity between value of lows and beginning of palette
    if not np.isclose(col_obj.lows.val, col_obj.cols[0].val_low):
        err_mess = ( newline+' '                          + newline
                    +'Problem: data value for low values not identical to the '  + newline
                    +'lowest bound of leg1.' 
                    +oper_ins)
        raise ValueError(err_mess)

    #continuity within and between color legs
    for ii in range(len(col_obj.cols)-1):
        #within legs
        err_mess = (newline+' '                                                + newline
                    +'Problem: incompatibility of operators within color legs.' + newline
                    +'The allowed combinations are:   are allowed.            ' + newline 
                    +'    ">"  and "<="                                       ' + newline
                    +'    or                                                  ' + newline
                    +'    ">=" and "<"                                        ' 
                    +oper_ins)
        #between legs
        if   col_obj.cols[ii].oper_high == '<=' :
            if col_obj.cols[ii+1].oper_low != '>' :
                raise ValueError(err_mess)
        elif col_obj.cols[ii].oper_high == '<' :
            if col_obj.cols[ii+1].oper_low != '>=' :
                raise ValueError(err_mess)
        else:
            err_mess = ( newline+' '                          + newline
                        +'Problem with the operator mapping data values within the palette.'  + newline
                        +'"oper_high" may only be "<" or "<=".' 
                        +oper_ins)
            raise ValueError(err_mess)
        #continuity between bound values within the palette 
        if not np.isclose(col_obj.cols[ii].val_high, col_obj.cols[ii+1].val_low):
            err_mess = ( newline+' '                          + newline
                        +'Problem: boundary values not matching for one leg of the palette. '  
                        +oper_ins)
            raise ValueError(err_mess)

    #high operator
    err_mess = (newline+' '                                          + newline
                +'Problem: incompatibility of operators at bound_n.' + newline
                +'The allowed combinations are:                    ' + newline 
                +'    "<"  and ">="                                ' + newline
                +'    or                                           ' + newline
                +'    ">=" and ">"                                 ' 
                +oper_ins)
    if col_obj.highs.oper == '>=' :
        if col_obj.cols[-1].oper_high != '<' :
            raise ValueError(err_mess)
    elif col_obj.highs.oper == '>':
        if col_obj.cols[-1].oper_high != '<=' :
            raise ValueError(err_mess)
    else:
        err_mess = ( newline+' '                          + newline
                    +'Problem with the operator mapping data values above the palette.'  + newline
                    +'only ">" and ">=" are allowed.' 
                    +oper_ins)
        raise ValueError(err_mess)
    #continuity between value of lows and beginning of palette
    if not np.isclose(col_obj.highs.val, col_obj.cols[-1].val_high):
        err_mess = ( newline+' '                          + newline
                    +'Problem: data value for high values not identical to the '  + newline
                    +'highest bound of leg_n.' 
                    +oper_ins)
        raise ValueError(err_mess)


