
class extend_open_end():
    def map(self, data, out_rgb, action_record):
        import numpy as np
        import operator

        #from strings to operator
        oper = { ">" : operator.gt, 
                 ">=": operator.ge,
                 "<" : operator.lt,
                 "<=": operator.le}

        #indices of data pts affected by comparison
        inds = np.flatnonzero(oper[self.oper](data, self.val)) 

        #assign all exceeding values to a predefined colors
        if inds.size != 0 :
            action_record[inds] += 1 
            out_rgb[inds] = self.color

    def __init__(self, val, oper, color):
        self.val   = val
        self.oper  = oper
        self.color = color
        self.action = 'extend'

