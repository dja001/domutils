
class lin_map():
    def extend_high(self):
        return self.col_high

    def extend_low(self):
        return self.col_low

    def map(self, data, out_rgb, action_record):
        #linear mapping of RGB values between min_val and max_val
        import numpy as np
        import operator

        #from strings to operator
        oper = { ">" : operator.gt, 
                 ">=": operator.ge,
                 "<" : operator.lt,
                 "<=": operator.le}

        #indices of data pts affected by comparison
        inds = np.flatnonzero( np.logical_and(oper[self.oper_low](data, self.val_low),
                                              oper[self.oper_high](data, self.val_high)) ) 

        #if there are data pts in the interval, compute associated color
        if inds.size != 0 :
            #add one to all indices affected by this mapping
            action_record[inds] += 1 
            #linear interpolation red, blue and green
            for col_ind in range(0,3):
                out_rgb[inds,col_ind] = np.interp(data[inds],[self.val_low,self.val_high],[self.col_low[col_ind],self.col_high[col_ind]])

    def __init__(self, val_high, val_low, oper_high, oper_low, col_high, col_low):
        self.val_high  = val_high 
        self.val_low   = val_low  
        self.oper_high = oper_high
        self.oper_low  = oper_low 
        self.col_high  = col_high 
        self.col_low   = col_low  


