"""
image handling routines that depend on external programs to be installed on machine. 

Those are mainly for personnal use on my workstation at ECCC. 
More work would be needed to make them generally useable
"""


def lmroman(picName):
    """
    horrible hack to use LMRoman typeface in svg figure    
    
    Never got it to work with  plt.rcParams["font.family"] = "LMRoman10"
    """

    import subprocess
    cmd = ['sed', '-i', 's/DejaVu\ Sans/LMRoman10/', picName]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

def convert(picName, imgType, delOrig=False, density=300, geometry='100%', delEPS=True):

    #convert figure to gif, png, ... while preservig hack for lmRoman typeface
    # this is very much work in progress

    import subprocess
    import os
    filename, fileExtension = os.path.splitext(picName)

    sourceFile = picName


    """
    STEP 1
      use inkscape to get a post-script from matplotlib's svg 
      inkscape will handle axes clipping correctly
      with delEPS=False you will even have post-scripts files for LateX
    """
    madeEPS = False
    if fileExtension == '.svg' :
        madeEPS = True
        epsName = filename+'.eps'
        cmd = ['inkscape', '-z', sourceFile, '-E', epsName]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        sourceFile = epsName

    """
    STEP 2
      use convert to get whatever format you like. 
      png, gif, jpg, etc... 
    """
    if imgType != 'eps' :
        #convert to gif using convert
        cmd = ['convert', '-density', str(density), '-geometry',geometry, sourceFile, filename+'.'+imgType]
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
    if delOrig :
        os.remove(picName)

    if madeEPS :
        if delEPS and not imgType == 'eps' :
            #ignore delEPS when desired fig type is eps
            os.remove(epsName)



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



