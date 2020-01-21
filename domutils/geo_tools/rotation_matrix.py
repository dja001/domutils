from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any

def rotation_matrix(axis: Any, 
                    theta:float):
    """ Rotation matrix for counterclockwise rotation on a sphere

        This formulation was found on SO
        https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
        Thanks, "unutbu" 
   
        Args:
           axis:    Array-Like containing i,j,k coordinates that defines an axis of rotation
                    starting from the center of the sphere (0,0,0)
           theta:   The amount of rotation (radians) desired.

        Returns:
            A 3x3 matrix (numpy array) for performing the rotation

        Example:
            >>> import numpy as np
            >>> import domutils.geo_tools as geo_tools
            >>> #a rotation axis [x,y,z] pointing straight up
            >>> axis = [0.,0.,1.]
            >>> # rotation of 45 degrees = pi/4 ratians
            >>> theta = np.pi/4.
            >>> #make rotation matrix
            >>> mm = geo_tools.rotation_matrix(axis, theta)
            >>> print(mm.shape)
            (3, 3)
            >>> # a point on the sphere [x,y,z] which will be rotated
            >>> origin = [1.,0.,0.]
            >>> #apply rotation
            >>> rotated = np.matmul(mm,origin)
            >>> #rotsted coordinates
            >>> print(rotated)
            [0.70710678 0.70710678 0.        ]

    """
    
    import numpy as np
    import math

    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
