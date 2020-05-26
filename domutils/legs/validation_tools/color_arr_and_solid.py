
def color_arr_and_solid(color_arr=None, solid=None, n_col=None):
    #color_arr contains the description of colors to be used by the different legs of the palette
    from .. import col_utils 
    from .. import validation_tools as validate
    import numpy as np
    from os import linesep as newline
    color_arr_ins = (newline                                                                     + newline
                    +'Instructions: the keyword "color_arr" defines the different colors to be used in a palette.   '+ newline 
                    +'   For categorical palettes, it is used in conjunction with the "solid" keyword.              '+ newline 
                    +'   1- A list of named colors                                                                  '+ newline 
                    +'      eg: color_arr=["red","green"]                                                           '+ newline 
                    +'      for two semi-continuous color legs, one red and one green                               '+ newline 
                    +'   2- An array of rgb colors describing dark and light values of each color leg.              '+ newline 
                    +'      eg: color_arr= [[[158,  0, 13],[255,190,187]],[[  0,134,  0],[134,222,134]]]            '+ newline 
                    +'      for two semi-continuous color legs, one red and one green  (same as above).             '+ newline 
                    +'      In this context, the number of elements in color_arr must be a multiple of 6.           '+ newline 
                    +'   3- For categorical color palettes                                                          '+ newline 
                    +'      "color_arr" must be an array of rgb colors describing solid colors for each color leg.  '+ newline 
                    +'      This requires that the "solid" keyword be specified.                                    '+ newline 
                    +'      a) With solid="col_dark" or solid="col_light"                                           '+ newline  
                    +'         color_arr must be an array of named colors                                           '+ newline  
                    +'         eg: color_arr=["red","green"]                                                        '+ newline 
                    +'         The dark or light shade of this color will be used for each leg.                     '+ newline 
                    +'      b) With solid="supplied"                                                                '+ newline  
                    +'         "color_arr" must be an array of rgb colors                                           '+ newline  
                    +'         eg: color_arr= [[255,000,000],[000,255,000]]                                         '+ newline 
                    +'         for two color legs, one solid red, the other solid green.                            ')

    #default exception color; will be changed for defaut black and white color mapping
    default_excep_col = 'black'

    #the solid keyword is used to specify solid color mappings
    err_mess = ( newline+' '                          + newline
                +'Problem with the keyword "solid."'  + newline
                +'It can only be a string set to "supplied", "col_dark" or "col_light". ' 
                +color_arr_ins)
    if solid is not None:
        #make sure color_arr is set
        if color_arr is None:
            err_mess = ( newline+' '                          + newline
                        +'Problem with the keyword "color_arr"'  + newline
                        +'When keyword solid is used, "color_arr" must be set.' 
                        +color_arr_ins)
            raise ValueError(err_mess)
        #check solid value 
        if isinstance(solid, str):
            if not ((solid == 'supplied') or (solid == 'col_dark') or (solid == 'col_light')):
                raise ValueError(err_mess)
        else: 
            raise TypeError(err_mess)

    #testing validity of color_array
    if color_arr is None :
        #use defaults
        if n_col is None:
            n_col = 1
            default_color     = 'b_w'
            default_excep_col = 'dark_red'
            color_arr_rgb = col_utils.col_pair(default_color)
        else:
            default_color_arr = ['brown','blue','green','orange','red','pink','purple','yellow','b_w']
            color_arr_rgb = col_utils.col_pair(default_color_arr[0:n_col])
            #change default exception value for contrast with the palette colors
    else:
        try:
            #this passes if we are provided rgb arrays (eg.  [[123,234,255],[...],...])
            color_arr_rgb = validate.rgb(color_arr, var_name='color_arr', instructions=color_arr_ins)
        except:
            if solid is None or solid == 'col_dark' or solid == 'col_light':
                #Continuous (or semi-continous) color palette
                color_arr_rgb = col_utils.col_pair(color_arr, var_name='color_arr', instructions=color_arr_ins)
            else:
                #Categorical palette
                color_arr_rgb = col_utils.col_rgb(color_arr, var_name='color_arr', instructions=color_arr_ins)

        #determine the number of color legs
        if solid is None:
            #Continuous (or semi-continous) color palette
            #check size
            if np.remainder(color_arr_rgb.size, 6) != 0:
                err_mess = ( newline+' '                                                + newline
                            +'Problem with the keyword "color_arr"'                     + newline
                            +'For a continuous or semi-continuous palette, the number of '+ newline
                            +'elements in "color_arr" must be a multiple of 6.'         + newline
                            +color_arr_ins)
                raise ValueError(err_mess)
            else:
                n_col = np.int_(color_arr_rgb.size / 6)
        else:
            #Categorical palette
            if color_arr is None:
                err_mess = ( newline+' '                             + newline
                            +'Problem with the keyword "color_arr"'  + newline
                            +'When building a categorical palette, "color_arr" must be specified'
                            +color_arr_ins)
                raise ValueError(err_mess)
                
            #pick right color if demander by the solid keyword
            if solid == 'col_dark':
                if len(color_arr_rgb.shape) == 2:
                    color_arr_rgb = color_arr_rgb[1]
                else:
                    color_arr_rgb = color_arr_rgb[:,1,:]
            if solid == 'col_light':
                if len(color_arr_rgb.shape) == 2:
                    color_arr_rgb = color_arr_rgb[0]
                else:
                    color_arr_rgb = color_arr_rgb[:,0,:]

            #check size
            if np.remainder(color_arr_rgb.size, 3) != 0:
                err_mess = ( newline+' '                                                + newline
                            +'Problem with the keyword "color_arr"'                     + newline
                            +'For a categorical palette, the number of '+ newline
                            +'elements in "color_arr" must be a multiple of 3.'         + newline
                            +color_arr_ins)
                raise ValueError(err_mess)
            else:
                 n_col = np.int_(color_arr_rgb.size / 3)

            #make sure rgb array is at least 2d for compatibility with rest of code
            color_arr_rgb = np.atleast_2d(color_arr_rgb)
            
    return color_arr_rgb, default_excep_col, n_col 

