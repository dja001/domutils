
#functions relating elevation, range, height and distance following the earth
from typing import Callable, Iterator, Union, Optional, List, Iterable, MutableMapping, Any
        
def model_43(dist_beam:   Optional[Any] = None,
             dist_earth:  Optional[Any] = None,
             height:      Optional[Any] = None,
             elev:        Optional[Any] = None,
             hrad:        Optional[float] = 0., 
             R:           Optional[float] = 6371.0072,
             want:        Optional[str] = None):

    """Geometric transformations using a 4/3 earth model

     Uses the 4/3 model by Doviak and Zrnic

     Args:
        dist_beam:         [km] distance along the radar beam; rang
        dist_earth:        [km] distance to radar followinf the curved surface of the earth
        height:            [km] altitude of radar beam AGL 
        elev:              [degrees] elevation angle
        hrad               [km] altitude of radar antenna AGL  
        R                  [km] radius of the earth default=6371.0072 km which is
                                authalic radius of the eart ("equal area - hypothetical perfect sphere")
        want:              [string] desired quantity for output one of: 'dist_beam', 'dist_earth', 'height' or 'elev'
    
        Inputs must be broadcastable to one another
         
        This routine is a translation of IDL functions by 
        Bernat Puigdomenech Treserras 
        Bernat is a genuinely good guy, I miss working with him. 

    Examples:

           >>> #you can verify relationships against one another
           >>> import domutils.radar_tools as radar_tools
           >>> radar_tools.model_43(elev=30, dist_beam=100., want='height')
           50.43885848738864
           >>> radar_tools.model_43(elev=30, dist_beam=100., want='dist_earth')
           86.09282939359983
           >>> radar_tools.model_43(elev=30, dist_earth=86.09282939359983, want='height')
           50.43885848738864
           >>> radar_tools.model_43(elev=30, dist_earth=86.09282939359983, want='dist_beam')
           99.99999999999999
           >>> radar_tools.model_43(dist_earth=86.09282939359983, height=50.43885848738864, want='elev')
           30.000000000000107
           >>> #
           >>> #rate of change for height as a function of dist_earth
           >>> radar_tools.model_43(dist_earth=100., elev=30., want='d_height__d_dist_earth')
           0.5972551219854002
           >>> #is very close to one we can estimate numerically
           >>> dx = 1.
           >>> h2 = radar_tools.model_43(dist_earth=100.+dx/2., elev=30., want='height')
           >>> h1 = radar_tools.model_43(dist_earth=100.-dx/2., elev=30., want='height')
           >>> (h2-h1)/dx
           0.5972551244358328
           >>> #
           >>> #input values will be broadcaster together
           >>> radar_tools.model_43(elev=30, dist_beam=[25., 50, 100.], want=('height'))
           array([12.52755023, 25.11003868, 50.43885849])
           >>> radar_tools.model_43(elev=[10., 20., 30], dist_beam=[25., 50, 100.], want=('height'))
           array([ 4.3768646 , 17.23068271, 50.43885849])
    """

    import numpy as np
    
    #4/3 earth
    Re=R*(4./3)

    #elev in radians if passed as input
    if elev is not None:
        elev_rad=np.deg2rad(elev)

    if dist_beam is not None:
        dist_beam = np.asarray(dist_beam)
    if dist_earth is not None:
        dist_earth = np.asarray(dist_earth)
    if height is not None:
        height = np.asarray(height)

    if want == 'height':
        if dist_beam is not None and elev is not None:

            if dist_earth is not None:
                raise ValueError('Both dist_beam and dist_earth are provided to compute height. Please provide only one')

            # height from Doviak and Zrnic (2.28b)
            return np.sqrt(dist_beam**2. + (Re+hrad)**2. + 2.*dist_beam * (Re+hrad) * np.sin(elev_rad)) - Re

        elif dist_earth is not None and elev is not None:

            if dist_beam is not None:
                raise ValueError('Both dist_beam and dist_earth are provided to compute height. Please provide only one')

            # height from Doviak and Zrnic (2.28a)
            return (np.cos(elev_rad) / np.cos(elev_rad + dist_earth/Re)) * (Re+hrad) - Re
        else :
            raise ValueError('combination of inputs not supported for quantity height')


    if want == 'd_height__d_dist_earth':

        if dist_earth is None or elev is None:
            raise ValueError('Need dist_earth and elev to compute d height / d dist_earth')
        
        #rate of change of radar beam height as a function of dist_earth
        return ( np.cos(elev_rad) * (Re+hrad) * np.sin(elev_rad + dist_earth/Re) ) / ( Re * np.cos(elev_rad + dist_earth/Re)**2. ) 
        

    elif want == 'dist_beam':
        if dist_earth is not None and elev is not None:
            # dist_beam from Doviak and Zrnic (2.28c)
            return np.tan(dist_earth/Re) * (Re+hrad) / (np.cos(elev_rad) - np.sin(elev_rad) * np.tan(dist_earth/Re))
        else:
            raise ValueError('combination of inputs not supported for quantity dist_beam')

    elif want == 'dist_earth':
        if dist_beam is not None and elev is not None:

            # dist_earth from Doviak and Zrnic (2.28c)
            return np.arctan(dist_beam * np.cos(np.deg2rad(elev)) / (dist_beam * np.sin(np.deg2rad(elev)) + Re + hrad)) * Re
            #   same results with:  np.sin(dist_beam * np.cos(elev_rad) / (Re + height)) * Re 
        else: 
            raise ValueError('combination of inputs not supported for quantity dist_earth')

    elif want == 'elev':

        if dist_earth is not None and height is not None:
            distRe=(dist_earth / Re)
        
            # elev from Doviak and Zrnic (2.28a)
            elev=((-1.)/np.sin(distRe)) * (((Re+hrad) / (height+Re)) - np.cos(distRe))
            return np.rad2deg(np.arctan(elev))
        else:
            raise ValueError('combination of inputs not supported for quantity elev')
    else:
        raise ValueError("'want' should be one of: 'dist_beam', 'dist_earth', 'height' or 'elev' ")

       
if __name__ == "__main__":
    import doctest
    doctest.testmod()
