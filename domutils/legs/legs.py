#TODO
# dimension checking of the color object
# check for copy that are not copies....
# solid_name keyword for categorical palettes


#make a bank of various solid palette for people to use
#eg:
#blue_orange = [ [ 13,  13, 134],      #dark blue
#                [  0,  81, 192],
#                [  0, 126, 237],
#                [  0, 169, 191],
#                [153, 216, 224],
#                [204, 249, 255],      #pale blue
#                [255, 255, 169],      #pale orange
#                [255, 205, 124],
#                [255, 159,  71],
#                [255, 119,  51],
#                [164,  53,   0],
#                [104,  10,   0] ]      #dark orange


class PalObj():
    """ A class for intuitive construction of color palettes

       - Easy construction of qualitative, semi-quantitative, categorical and divergent color mappings
       - Guarantees that a color is assigned for data values between -infinity and +infinity
       - Explicit handling of colors at and/or exceeding end points
       - Supports any number of exception values assigned to specific colors
       - Encourages the user to specify units of data being depicted
       - Consistency of the color palettes and colored representation of data is assured through 
         the use of the same color mapping functions. 

       Args:
          range_arr:    End points of the different color legs.  

                        Must be:

                        1. A two element array-like describing the maximum and minimum data values 
                           represented by the color palette

                           eg: ``[0.,1]``

                        2. A *n* element array-like describing the data values delimiting the bounds 
                           of each color leg.

                           eg: ``[0.,1.,10.,100, ...]``

                           In this case, the dimension of *range_arr* should be the number of legs +1

          color_arr:    Defines the different colors to be used in a palette.

                        For categorical palettes, it is used in conjunction with the *solid* keyword.

                        It can be:

                        1. A list of named colors

                           eg: ["red","green"]

                           for two semi-continuous color legs, one red and one green

                        2. An array-like of rgb colors describing dark and light values of each color leg.

                           eg: ``[[[158,  0, 13],[255,190,187]],[[  0,134,  0],[134,222,134]]]``

                           for two semi-continuous color legs, one red and one green  (same as above)
                           In this context, the number of elements in color_arr must be a multiple of 6
                           (two rgp value per legs)

                        3. For categorical color palettes *color_arr* must be an array-like of rgb 
                           colors describing solid colors for each color leg.  
                           This requires that the "solid" keyword be specified.

                           a) With solid="col_dark" or solid="col_light"
                              *color_arr* must be a list of strings of named colors

                              eg: ``["red","green"]``

                              The dark or light shade of this color will be used for each leg.

                           b) With solid="supplied"
                              "color_arr" must be an array-like of rgb colors

                              eg: ``[[255,000,000],[000,255,000]]``

                              for two color legs, one solid red, the other solid green.

          solid:        A string set to ``"supplied"``, ``"col_dark"`` or ``"col_light"``.
                        See the documentation of the *color_arr* argument for usage.


          dark_pos:     Defines whether the dark color is to be associated with high or low data value.
                        It is only meaningful when constructing a continuous or semi-continuous palettes.

                        - The default is to assign dark colors to the larger data values
                        - If set to "high" or "low" all legs will be set to the high or low data value
                        - If set to a list of strings, 

                          eg: ``["high","low"]``,
                          
                          it will determine the position of the dark color for the individual color 
                          legs.
                          In this case, the length of the list should be the same as the number of 
                          legs in the palette.

          n_col:        Specifies how many color to display when using the default color sequence. 

                        - It must be convertible to an integer number.
                        - It must be <= 8.

          over_high:    Determines what color gets assigned to data values larger than the palette 
                        range.

                        Accepted values are:

                        1. ``"exact"``: no data values expected beyond the range of the color mapping..
                           At the moment of applying the color mapping, an error will be raised if 
                           such data values are found.

                        2. ``"extend"``: The end-point color will be used for data beyond the range
                           of the color mapping

                        3. A named color:    
                        
                           eg: ``"red"``

                        4. A rgb color:      
                        
                           eg: ``[  0,  0,255]``

          under_low:    Determines what color gets assigned to data values smaller than the palette 
                        range.

                        Accepted values are:

                        1. ``"exact"``: no data values expected beyond the range of the color mapping..
                           At the moment of applying the color mapping, an error will be raised if 
                           such data values are found.

                        2. ``"extend"``: The end-point color will be used for data beyond the range
                           of the color mapping

                        3. A named color:    
                        
                           eg: ``"red"``

                        4. A rgb color:      
                        
                           eg: ``[  0,  0,255]``

          over_under:   Shortcut to specify both *over_high* and *under_low* at the same time

          excep_val:    Data values to which special colors will be assigned.
 
          excep_tol:    Tolerance within which a data value specified in *excep_val* is considered 
                        an exception

                        exception_range = *excep_val* +- *except_tol* inclusively

                        - *excep_tol* must have the same dimension as "excep_val"

          excep_col:    Color(s) to be assigned to data value specified in *excep_val*
          
                        Must be
                            
                        1. A string describing a named colors

                           eg:  ``"dark_red"``

                           This color will be assigned to all exceptions.

                        2. A 1D list of named colors

                           eg: ``["dark_red"   ,"dark_blue"  , ... , "dark_green" ]``

                        3. A 2D array-like of rgb colors

                           eg: ``[[000,000,255],[000,255,000], ... , [000,000,255]]``
   
                        For cases 2 and 3, the number of colors represented must be 
                        equal to the number of exceptions provided in "excep_val".


          map_f_arr:    Defines the name of the function that performs the mapping between data 
                        values and rgb values.

                        1. If a string, the function will be used for all color legs of a 
                           palette.

                        2. If a list of strings, it defines the mapping function for each individual 
                           legs.
                           In this case, the dimension of *map_f_arr* should be equal to the number 
                           of color legs.

                        - The default behavior is to use the "linmap" function.
                          For linear interpolation of rgb between two predefiuned colors.

                        - When the *solid* keyword is set, the "within" function is used instead.
       
    """

    from typing import Any, Callable, Iterator, Union, Optional, List, Iterable, MutableMapping
    import numpy as np

    def plot_palette(self, 
                     data_ax:       Optional[Any]   = None,
                     equal_legs:    Optional[bool]  = None,
                     pal_pos:       Optional[Any]   = None,
                     pal_sp:        Optional[float] = .1,
                     pal_w:         Optional[float] = .25,
                     pal_units:     Optional[str]   = 'Undefined Units',
                     pal_linewidth: Optional[float] = .3,
                     pal_format:    Optional[str]   = '{:3.3f}'
                     ):
                    
        """
        plot a color palette near an existing axes where data is displayed

        Args:
            data_ax:       The matplotlib axes where the data is plotted.
                           The palette will be plotted in an ax besides this
                           Has no effect if **pal_pos** is provided. 

            equal_legs:    Flag indicating that all color legs should have the same 
                           space in the palette.

                           The default is to set the space proportional to the data
                           interval spanned by individual color legs.

            pal_pos:       Position [x0,y0,width,height] for plotting palette.

            pal_sp:        Space [inches] between figure and palette

            pal_w:         Width [inches] of color palette

            pal_units:     The units of the palette being shown.

            pal_linewidth: Width of the lines

            pal_format:    Format string for the data values displayed beside tickmarks

        """
        import numpy as np
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import matplotlib.lines as mlines

        # if pal_pos not provided, make one from a data axes
        if pal_pos is None:
            # get figure size
            fig  = data_ax.get_figure()
            fig_w, fig_h = fig.get_size_inches()
            #set axes position for palette
            pos0 = data_ax.get_position()
            pal_sp_norm = pal_sp/fig_w   #space between data and palette normal [0,1] units
            pal_w_norm  = pal_w/fig_w    #width of palette normal [0,1] units
            pal_pos  = [pos0.x0+pos0.width+pal_sp_norm, pos0.y0, pal_w_norm, pos0.height]  #palette position in figure
        else:
            #pal_pos provided, use current figure
            fig  = plt.gcf()

        #axes pour palette
        ax = fig.add_axes(pal_pos)

        mpl.rcParams['axes.linewidth'] = pal_linewidth      #set the value globally
        for axis in ['top','bottom','left','right']:        #god is matplotlib messy....
              ax.spines[axis].set_linewidth(pal_linewidth)



        #setup color palette axis using a modified version of "colorbar.py" from the matplotlib library
        boundaries = [this_leg.val_low for this_leg in self.cols]
        boundaries.append(self.cols[-1].val_high)

        #make palette data
        if equal_legs == True:
            n_cols = len(self.cols)
            nn = 100              #number of data values per color leg
            nt = n_cols*nn #- 1   #total number of data values in this palette
            pal_data = np.zeros(nt)
            for ii in range(n_cols):
                if self.cols[ii].oper_low == '>':
                    small_low = 1e-9
                elif self.cols[ii].oper_low == '>=':
                    small_low = 0.
                else:
                    err_mess='oper_low attribute should not have values other than ">" or ">=".'
                    raise ValueError(err_mess)
                if self.cols[ii].oper_high == '<':
                    small_high = -1e-9
                elif self.cols[ii].oper_high == '<=':
                    small_high = 0.
                else:
                    err_mess='oper_high attribute should not have values other than "<" or "<=".'
                    raise ValueError(err_mess)

                #reduce number of pixels by 1 for perfect alignment with boundaries
                nn_sub=0
                if ii == n_cols-1:
                    pass
                    #nn_sub = 1

                pal_data[ii*nn:(ii+1)*nn] = np.linspace(self.cols[ii].val_low+small_low,
                                                        self.cols[ii].val_high+small_high, nn-nn_sub)
        else:
            nn = 1000
            pal_data = np.linspace(boundaries[0], boundaries[-1], nn)
        pal_data = np.flipud(pal_data)[:,np.newaxis]
        #transform palette data into rbg image
        pal_rgb = self.to_rgb(pal_data)

        labels = []
        for this_num in boundaries:
            labels.append(pal_format.format(this_num))
        if equal_legs == True:
            boundaries = np.linspace(self.cols[0].val_low,self.cols[-1].val_high,n_cols+1)

        ax.imshow(pal_rgb, axes=ax, aspect='auto',extent=[0.,1,boundaries[0],boundaries[-1]],interpolation='nearest')
        ax.set_xticks([])
        ax.set_yticks(boundaries)
        ax.set_yticklabels(labels)
        ax.yaxis.tick_right()
        ax.tick_params(width=pal_linewidth)

        #axis label
        ax.set_ylabel(pal_units)
        ax.yaxis.set_label_position("right")

        #extentions
        tri_h = 0.03    # length of triangle (% of palette long side)
        if self.lows.action == 'extend':
            #position of extension triangle
            tri_x = np.array([0.,.5,1])
            tri_y = 0.+np.array([0.,-tri_h,0.])
            tri_xy = np.zeros([3,2])
            for ii in range(3):
                tri_xy[ii,:] = [tri_x[ii],tri_y[ii]]
            #extension color
            tri_down_col = self.lows.color/255.   #/255 to get RGB 0-1
            #poligon object
            tri_down = patches.Polygon(tri_xy, facecolor=tri_down_col, edgecolor='black',
                                       closed=True,clip_on=False, linewidth=pal_linewidth,
                                       transform=ax.transAxes)
            ax.add_patch(tri_down)
            #no need for an lower line anymore
            ax.spines['bottom'].set_linewidth(0.)

        if self.highs.action == 'extend':
            #position of extension triangle
            tri_x = np.array([0.,.5,1])
            tri_y = 1.+np.array([0.,tri_h,0.])
            tri_xy = np.zeros([3,2])
            for ii in range(3):
                tri_xy[ii,:] = [tri_x[ii],tri_y[ii]]
            #extension color
            tri_up_col = self.highs.color/255.   #/255 to get RGB 0-1
            #poligon object
            tri_up = patches.Polygon(tri_xy, facecolor=tri_up_col, edgecolor='black',
                                     closed=True,clip_on=False, linewidth=pal_linewidth,
                                     transform=ax.transAxes)
            ax.add_patch(tri_up)
            #no need for an upper line anymore
            ax.spines['top'].set_linewidth(0.)








    def plot_data(self, 
                  ax:         Any, 
                  data:       np.ndarray, 
                  palette:    Optional[str]      = None, 
                  zorder:     Optional[int]      = None, 
                  aspect:     Optional[Any]      ='auto',
                  rot90:      Optional[int]      = None,
                  **kwargs,
                 ):
        """
        Applies the mapping from data space to color space and plots the result into
        an existing axes.

        Args:
            ax:       The matplotlib Axes object where imshow will plot the data
            data:     Data to be plotted
            palette:  Flag to show a palette beside the data axes.
            aspect:   aspect ratio, see documentation for axes.set_aspect()
            rot90:    Number of counter-clockwise rotations to be applied to data before plotting
            zorder:   Matplotlib zorder for the imshow call
        """

        import numpy as np

        #if desired, rotate data
        if rot90 is not None:
            rdata = np.rot90(data,rot90)
        else:
            rdata = data

        #make rgb img from data
        out_rgb = self.to_rgb(rdata)

        #get ax extent in data space units
        try:
            #this will work for a Cartopy geo_axes 
            x1, x2, y1, y2 = ax.get_extent()
        except:
            #default to regular axis bound
            x1, x2 = ax.get_xlim()
            y1, y2 = ax.get_ylim()

        #call imshow to plot the data
        ax.imshow(out_rgb, axes=ax, interpolation='nearest',
                  extent=[x1,x2,y1,y2], zorder=zorder)
        ax.set_aspect(aspect)

        #plot palette if desired
        if palette is not None:
            if palette == 'right':
                #plot palette
                self.plot_palette(ax,**kwargs)
            else:
                err_mess='Only "right" is implemented at this moment'
                raise ValueError(err_mess)




    def to_rgb(self, data_in: np.ndarray ) -> np.ndarray :
        """
        Applies the mapping from data space to color space and returns resulting rgb array

        Args:
            data:     Data to be plotted
        """
        #this method applies the color mapping object and outputs a rgb array of the same size as data_in

        import numpy as np
        from . import validation_tools as validate

        #insure that data values from -infty to +infty are taken care of
        validate.continuity_of_mapping(self)

        #insure that data is of type numpy array; flat array is returned so we don't need to care about dimensions later
        data_flat = validate.input_data(data_in)

        ##initialize output and action_record arrays
        out_rgb = np.zeros(data_flat.shape+(3,),dtype='uint8')
        action_record = np.zeros(data_flat.shape,dtype='int')

        #map data below palette
        self.lows.map(data_flat, out_rgb, action_record)

        #map data for each color leg
        for this_leg in self.cols:
            this_leg.map(data_flat, out_rgb, action_record)

        #map data above palette
        self.highs.map(data_flat, out_rgb, action_record)

        #check that no values have been mapped twice
        validate.not_mapped_twice(data_flat, action_record)

        #map exceptions, its okay for exceptions to superseed colors already mapped
        for this_excep in self.excepts:
            this_excep.map(data_flat, out_rgb, action_record)

        #check that all data pts have been mapped
        validate.no_unmapped(data_flat, action_record, self.lows, self.highs)

        return out_rgb.reshape(np.atleast_1d(data_in).shape+(3,))



    def __init__(self, range_arr:  Optional[List[float]]=None, 
                       dark_pos:   Optional[List[str]]  =None, 
                       color_arr:  Optional[Any]        =None,
                       n_col:      Optional[int]        =None, 
                       map_f_arr:  Optional[Callable]   =None, 
                       solid:      Optional[str]        =None,
                       over_high:  Optional[str]        =None, 
                       under_low:  Optional[str]        =None, 
                       over_under: Optional[str]        =None,
                       excep_val:  Optional[List[float]]=None, 
                       excep_tol:  Optional[List[float]]=None, 
                       excep_col:  Optional[Any]        =None ):
        """
        Make a mapping object of class pal object

        Args:
            range_arr: Limits for the different color legs

        """

        from . import validation_tools as validate
        from . import col_map_fct as map_fct


        #validate user input and set default othwewise
        #order is important as some variables get passed to subsequent functions

        #n_col
        num_color = validate.n_col(n_col)

        #col_arr
        (color_arr_rgb,
         default_excep_col,
         num_color)         = validate.color_arr_and_solid(color_arr, solid, num_color)

        #dark_pos
        dark_flip           = validate.dark_pos(dark_pos,   num_color)

        #map_f_arr
        map_f_arr_out       = validate.map_f_arr(map_f_arr, num_color,solid)

        #range_arr
        range_lh            = validate.range_arr(range_arr, num_color)

        #exceptions keywords
        (n_excep,
         excep_val_np,
         excep_tol_np,
         excep_col_rgb)     = validate.exceptions(excep_val, excep_tol, excep_col, default_excep_col)

        #for data values over and below palette
        (action_high,
         color_high,
         action_low,
         color_low)         = validate.over_under(over_under, under_low, over_high)


        #Creating the list containing the mapping object for each legs of a palette
        col_legs = []
        for ii in range(num_color):
            #range specific to this leg
            val_high = range_lh[ii+1]
            val_low  = range_lh[ii]
            #operators defining data values to which this leg is applicable
            oper_high = '<'
            oper_low  = '>='

            #continuous palette; linear interpolation between two RGB values
            if map_f_arr_out[ii] == 'linmap':
                #indices for position of light and dark color
                if dark_flip[ii] == True:
                    ind_high = 0
                    ind_low  = 1
                else:
                    ind_high = 1
                    ind_low  = 0
                #colors specific to this leg
                if   len(color_arr_rgb.shape) == 2:
                    col_high = color_arr_rgb[ind_high,:]
                    col_low  = color_arr_rgb[ind_low, :]
                elif len(color_arr_rgb.shape) == 3:
                    col_high = color_arr_rgb[ii, ind_high,:]
                    col_low  = color_arr_rgb[ii, ind_low, :]
                #instantiate color mapping object
                this_map = map_fct.lin_map(val_high, val_low, oper_high, oper_low, col_high, col_low)

            #categorical palette; assign one color to all data values within an interval
            if map_f_arr_out[ii] == 'within':
                #colors specific to this leg
                color = color_arr_rgb[ii,:]
                #instantiate color mapping object
                this_map = map_fct.solid_map(val_high, val_low, oper_high, oper_low, color)

            #all mapping objects in a list
            col_legs.append(this_map)

        #values below palette
        bound = col_legs[0].val_low
        if   col_legs[0].oper_low == '>=':
            oper  = '<'
        elif col_legs[0].oper_low == '>':
            oper  = '<='
        else:
            err_mess = 'Problem defining operator for map_low'
            raise ValueError
        #type of mapping object depends on action defined earlier
        if action_low == 'exact':
            #force inclusive end points for exact palette
            col_legs[0].oper_low == '>='
            oper  = '<'
            map_low = map_fct.exact_open_end(bound, oper)
        if action_low == 'extend' :
            if color_low is None:   #low color is an extension of the lowest color of the palette
                color_low = col_legs[0].extend_low()
            map_low = map_fct.extend_open_end(bound, oper, color_low)

        #values above palette
        bound = col_legs[-1].val_high
        if   col_legs[-1].oper_high == '<=':
            oper  = '>'
        elif col_legs[-1].oper_high == '<':
            oper  = '>='
        else:
            err_mess = 'Problem defining operator for map_high'
            raise ValueError
        #type of mapping object depends on action defined earlier
        if action_high == 'exact':
            #force inclusive end points for exact palette
            col_legs[-1].oper_high = '<='
            oper = '>'
            map_high = map_fct.exact_open_end(bound, oper)
        if action_high == 'extend':
            if color_high is None:  #high color is an extension of the lowest color of the palette
                color_high = col_legs[-1].extend_high()
            map_high = map_fct.extend_open_end(bound, oper, color_high)

        #list containing mapping objects for exceptions
        excepts = []
        for ii in range(int(n_excep)):
            #instantiate exception mapping object
            this_map = map_fct.solid_map(excep_val_np[ii]+excep_tol_np[ii], excep_val_np[ii]-excep_tol_np[ii],
                                         '<=', '>=',
                                         excep_col_rgb[ii])
            excepts.append(this_map)


        #returned value
        self.highs    = map_high
        self.cols     = col_legs
        self.lows     = map_low
        self.excepts  = excepts

def main():
    pass

if __name__ == "__main__":
    main()
