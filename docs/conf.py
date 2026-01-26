# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath('..'))

on_rtd = os.environ.get('READTHEDOCS') == 'True'

# location of customs patch to add images links on read thedocs
sys.path.insert(0, os.path.abspath('_extensions'))


# -- Project information -----------------------------------------------------

project = 'domutils'
copyright = '2019, Dominik Jacques'
author = 'Dominik Jacques'

# The full version, including alpha/beta/rc tags
with open('../VERSION', encoding='utf-8') as f:
    version = f.read()
release = version

# Download test data if needed
if not os.path.isdir('../test_data') :
    #test_data is not there, download it

    try:
        #move up one directory
        current = os.getcwd()
        parent  = os.path.dirname(current)
        os.chdir(parent)
        #make script executable if it is not
        shell_script = './scripts/download_test_data.sh'
        if not os.access(shell_script, os.X_OK):
            os.chmod(shell_script, 0o755)
        #run script to download _static directory from zenodo archive
        subprocess.run([shell_script, 'figures_only'])
    except:
        raise RuntimeError('something went wrong downloading the test data')


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
#       'sphinx.ext.coverage',
#extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
extensions = ['sphinx.ext.napoleon',
              'sphinx.ext.doctest', 
              'sphinx.ext.autosectionlabel',
              'sphinx_autodoc_typehints',
              'sphinxarg.ext',
              'sphinx_gallery.gen_gallery',
              'patch_gallery_images'] # in _extensions; adds image links to examples

napoleon_include_private_with_doc = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build', '_build', 'Thumbs.db', '.DS_Store']


#options for gallery
sphinx_gallery_conf = {
     'examples_dirs': '../examples',   # path to your example scripts
     'gallery_dirs': 'auto_examples',  # path where to save gallery generated examples
     'plot_gallery': not on_rtd,
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = ["_themes", ]


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

