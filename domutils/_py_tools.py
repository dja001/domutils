"""
image handling routines that depend on external programs to be installed on machine. 

Those are mainly for personal use on my workstation at ECCC.
More work would be needed to make them generally usable
"""


def lmroman(pic_name):
    """
    horrible hack to use LMRoman typeface in svg figure    
    
    Never got it to work with  plt.rcParams["font.family"] = "LMRoman10"
    """

    import subprocess
    cmd = ['sed', '-i', 's/DejaVu\ Sans/LMRoman10/', pic_name]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

def convert(pic_name, img_type, del_orig=False, density=300, geometry='100%', del_eps=True):

    #convert figure to gif, png, ... while preserving hack for lmRoman typeface
    # this is very much work in progress

    import subprocess
    import os
    file_name, file_extension = os.path.splitext(pic_name)

    source_file = pic_name


    """
    STEP 1
      use inkscape to get a post-script from matplotlib's svg 
      inkscape will handle axes clipping correctly
      with del_eps=False you will even have post-scripts files for LateX
    """
    made_eps = False
    if file_extension == '.svg' :
        made_eps = True
        eps_name = file_name+'.eps'
        cmd = ['inkscape', '-z', source_file, '-E', eps_name]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        source_file = eps_name

    """
    STEP 2
      use convert to get whatever format you like. 
      png, gif, jpg, etc... 
    """
    if img_type != 'eps' :
        #convert to gif using convert
        cmd = ['convert', '-density', str(density), '-geometry', geometry, source_file, file_name +'.' + img_type]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()

    #recipe for conversion to pdf
    #these days, I tend to output svg which I then edit with Inkscape and then save as pdf for use with beamer
    #ps2pdf -dEPSCrop -dColorConversionStrategy=/LeaveColorUnchanged  -dEncodeColorImages=false  -dEncodeGrayImages=false  -dEncodeMonoImages=false

    """
    STEP 3
      cleanup
    """
    #delete temp file
    if del_orig :
        os.remove(pic_name)

    if made_eps :
        if del_eps and not img_type == 'eps' :
            #ignore del_eps when desired fig type is eps
            os.remove(eps_name)



def info(var):
    """
    get info on different variables
    this should definitely be put someplace else...
    """
    import numpy as np
    if isinstance(var, (np.ndarray, np.generic) ):
        print('numpy')
        print('type', var.dtype)
        print('shape', var.shape)
        print('min / max: ', var.min(), var.max())

    if isinstance(var, dict):
        print('dictionary')
        print(var.keys())



