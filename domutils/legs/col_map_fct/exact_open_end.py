    
class exact_open_end():
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

        #for exact palettes ends, no values should exceed the palette
        #mark them as -1 for later error catching
        if inds.size != 0 :
            self.bound_error = 1

    def __init__(self, val, oper):
        self.val         = val
        self.oper        = oper
        self.bound_error = 0
        self.action = 'exact'

