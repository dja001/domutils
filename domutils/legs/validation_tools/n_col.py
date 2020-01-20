def n_col(n_col):
    #the n_col keyword is used to specify a palette a certain number of with default colors 
    from os import linesep as newline
    n_col_ins = (newline                                                                            + newline
                 +'Instructions: the keyword "n_col" specifies how many color to display when using'+ newline 
                 +'the default color sequence. It must be convertible to an integer number.'        + newline
                 +'       It must be convertible to an integer number.'                             + newline
                 +'       It must be <= 8.'                                                         + newline)
    if n_col is not None :
        try:
            num_color = int(n_col)
        except :
            err_mess = ( newline+' '                         + newline
                        +'Problem with the keyword "n_col"'  + newline
                        +'Unable to convert to an integer:' 
                        +n_col_ins)
            raise TypeError(err_mess)
        if num_color > 8 :
            err_mess = ( newline+' '                         + newline
                        +'Problem with the keyword "n_col"'  + newline
                        +'Maximum of 8 color legs allowed by default' 
                        +n_col_ins)
            raise ValueError(err_mess)
    else:
        num_color=None
        

    return num_color


