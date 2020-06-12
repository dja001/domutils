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
    cmd = ['sed', '-i', r's/DejaVu\ Sans/LMRoman10/', pic_name]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

def convert(pic_name, img_type, del_orig=False, density=300, geometry='100%', del_eps=True):

    #convert figure to gif, png, ... while preserving hack for lmRoman typeface
    # this is very much work in progress

    import subprocess
    import os
    import shutil

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


def render_similarly(new_image_file, reference_image_file, 
                      output_dir=None, tol=0.1, verbose=1):
    """ compare two raster images, returns True if they render similarly

    compute mean absolute difference between the RGB arrays of two images  
    if they are the same within a certain tolerance, True is returned
    if images are not the same, an image showing the difference is generated
    in the outpur directory

    Typically, 
        new_image_file       is a newly generated image
        reference_image_file is a reference image previously generated
    
    if images are svg, they are converted to png before the comparison

    default output directory is "test_results/render_similarly" at the root of the package directory
    images are copied there before the comparison

    tol is the tolerence to errors
    tol=0.1 allows for an error of 1 (byte) every 10 pixels which 
             is approximatively the kind of errors one gets from compression noise

    """

    import os
    import shutil
    import numpy as np
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    from . import _py_tools as py_tools
    import domutils


    #if image size is not the same type, then images are considered different
    bname_new, extension_new = os.path.splitext(new_image_file)
    bname_ref, extension_ref = os.path.splitext(reference_image_file)
    if extension_new != extension_ref:
        if verbose > 0 :
            msg = 'images are of different types'
            print(msg)
        os.remove(new_file_cp)
        os.remove(ref_file_cp)
        return False

    #default dir is 'test_results'
    if output_dir is None:
        domutils_dir = os.path.dirname(domutils.__file__)
        output_dir   = os.path.dirname(domutils_dir)+'/test_results/render_similarly/'
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

    #make a copy of each image in output_dir
    basename_new = os.path.basename(bname_new)
    new_file_cp = output_dir+basename_new+'_new'+extension_new
    shutil.copyfile(new_image_file, new_file_cp)
    basename_ref = os.path.basename(bname_ref)
    ref_file_cp = output_dir+basename_ref+'_ref'+extension_ref
    shutil.copyfile(reference_image_file, ref_file_cp)

    #ensure raster images
    if extension_new == '.svg' or extension_new == '.pdf' or extension_new == '.eps' or extension_new == '.ps':
        convert(new_file_cp, 'png', del_orig=True)
        convert(ref_file_cp, 'png', del_orig=True)
        b_new, e_new = os.path.splitext(new_file_cp)
        new_file_cp = b_new+'.png'
        b_ref, e_ref= os.path.splitext(ref_file_cp)
        ref_file_cp = b_ref+'.png'

    #start looking at image content
    image1 = Image.open(new_file_cp)
    image2 = Image.open(ref_file_cp)

    #if image size is not the same, then images are considered different
    if image1.size != image2.size:
        if verbose > 0 :
            msg = 'image size difference for: '+os.path.basename(new_file_cp)+'  '+str(image1.size)+' vs '+str(image2.size)
            print(msg)
        return False

    image1_arr = np.array(image1,dtype=np.int32)    #int32 is important here to avoid byte overflow during diff calculation
    image2_arr = np.array(image2,dtype=np.int32)

    abs_err = np.abs(image1_arr - image2_arr )
    mae = np.mean(abs_err)

    if mae < tol :
        #images are close to one another
        os.remove(new_file_cp)
        os.remove(ref_file_cp)
        return True

    else :
        #images are different
        #make an image to highlight the differences

        #make output_dir if it does not exists
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        #output figure that shows where errors are
        bn1 = os.path.basename(new_file_cp).split('.')[0]
        bn2 = os.path.basename(ref_file_cp).split('.')[0]
        diff_file = output_dir+'differences_in_images__'+bn1+'_'+bn2+'.png'

        #the difference image
        abs_err[:,:,3] = 255
        mosaic = np.hstack((image1_arr, abs_err, image2_arr)).astype(np.uint8)
        image_diff = Image.fromarray(mosaic)
        draw = ImageDraw.Draw(image_diff)
        font = ImageFont.truetype("Vera.ttf", 40)
        
        #annotations to understand what is going on
        x0 = int(.15*3.*image1.size[0])
        rec_w = 305
        draw.rectangle((x0-5, 0, x0+rec_w, 50), fill=(255,255,255), outline=(158,0,13))
        draw.text((x0, 0),"New image",(0,0,0), font=font)
        #
        x0 = int(.45*3.*image1.size[0])
        rec_w = 305
        draw.rectangle((x0-5, 0, x0+rec_w, 100), fill=(255,255,255), outline=(158,0,13))
        draw.text((x0, 0),"Difference",(0,0,0), font=font)
        draw.text((x0, 50),"MAE="+str(mae),(0,0,0), font=font)
        #
        x0 = int(.8*3.*image1.size[0])
        rec_w = 305
        draw.rectangle((x0-5, 0, x0+rec_w, 50), fill=(255,255,255), outline=(158,0,13))
        draw.text((x0, 0),"Original image",(0,0,0), font=font)

        image_diff.save(diff_file, format='png')
        if verbose > 0:
            print('saved ', os.path.basename(diff_file), 'mae=',mae)

        os.remove(new_file_cp)
        os.remove(ref_file_cp)
        return False


