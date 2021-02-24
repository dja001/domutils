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
            >>> #rotated coordinates
            >>> print(rotated)
            [0.70710678 0.70710678 0.        ]

    """
    
    import numpy as np
    import math

    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0) #b=i*sin(theta)  c=j*sin(theta) d=k*sin(theta)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])



def rotation_matrix_components(axis: Any, 
                               theta:float):
    """ Rotation matrix for counterclockwise rotation on a sphere

        This version returns only the components of the rotation matrix(ces)
        This allows to use numpy array operations to 
        simultaneously perform many application of these rotation matrices 

        Args:
           axis:    Array-Like containing i,j,k coordinates that defines an axes of rotation
                    starting from the center of the sphere (0,0,0)
                    dimension of array must be (m,3) for m points each defined by i,j,k components
           theta:   The amount of rotation (radians) desired.
                    shape = (m,)

        Returns:
            A, B, C, D, E, F, G, H, I ::

                | A B C |
                | D E F |
                | G H I |

            Each of the components above will be of shape (m,)


        Example:
            >>> import numpy as np
            >>> import domutils.geo_tools as geo_tools
            >>> #four rotation axes [x,y,z]; two pointing up, two pointing along y axis
            >>> axes = [[0.,0.,1.], [0.,0.,1.], [0.,1.,0.], [0.,1.,0.]]
            >>> # first and third points will be rotated by 45 degrees (pi/4) second and fourth by 90 degrees (pi/2)
            >>> thetas = [np.pi/4., np.pi/2., np.pi/4., np.pi/2.]
            >>> #make rotation matrices
            >>> a, b, c, d, e, f, g, h, i = geo_tools.rotation_matrix_components(axes, thetas)
            >>> #Four rotation matrices are here generated
            >>> print(a.shape)
            (4,)
            >>> # points on the sphere [x,y,z] which will be rotated
            >>> # here we use the same point for simplicity but any points can be used
            >>> oi,oj,ok = np.array([[1.,0.,0.],[1.,0.,0.],[1.,0.,0.],[1.,0.,0.]]).T #transpose to unpack columns
            >>> #i, j and k components of each position vector
            >>> print(oi.shape)
            (4,)
            >>> #apply rotation by hand (multiplication of each point (i,j,k vector) by rotation matrix)
            >>> rotated = np.array([a*oi+b*oj+c*ok, d*oi+e*oj+f*ok, g*oi+h*oj+i*ok]).T
            >>> print(rotated.shape)
            (4, 3)
            >>> print(rotated)
            [[ 7.07106781e-01  7.07106781e-01  0.00000000e+00]
             [ 2.22044605e-16  1.00000000e+00  0.00000000e+00]
             [ 7.07106781e-01  0.00000000e+00 -7.07106781e-01]
             [ 2.22044605e-16  0.00000000e+00 -1.00000000e+00]]

    """
    
    import numpy as np

    axis  = np.asarray(axis)
    theta = np.asarray(theta)
    #normalize
    axis = axis / np.sqrt(np.sum(np.square(axis),axis=1))[...,np.newaxis]
    #components of rotation matrices
    a = np.cos(theta / 2.0)
    #b=i*sin(theta)  c=j*sin(theta) d=k*sin(theta)
    b, c, d = (-axis * np.sin(theta / 2.0)[...,np.newaxis] ).T #transpose here just to unpack columns of numpy array
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d

    #          A             B         C            D           E              F            G           H         I
    return aa+bb-cc-dd, 2.*(bc+ad), 2.*(bd-ac), 2.*(bc-ad), aa+cc-bb-dd, 2.*(cd + ab), 2.*(bd+ac), 2.*(cd-ab), aa+dd-bb-cc


if __name__ == "__main__":
    import doctest
    doctest.testmod()

