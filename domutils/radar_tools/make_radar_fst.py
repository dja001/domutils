
import domutils.radar_tools.obs_process as obs_process
def to_fst(*args, **kwargs):
    import warnings
    
    warnings.warn('Module "make_radar_fst" is deprecated.' )
    warnings.warn('Please use obs_process instead' )
    return obs_process.to_fst(*args, **kwargs)

