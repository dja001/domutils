
from setuptools import setup, find_packages

# README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

#get version
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(
    name='domutils',
    version=version,
    url='https://github.com/dja001/domutils.git',
    license='GPL-3.0-or-later',
    author='Dominik Jacques',
    author_email='dominik.jacques@gmail.com',
    description="dominik's tools for custom color mappings and geographical projections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),    
    install_requires=['python >= 3.7.0', 'matplotlib >= 3.1.1', 'numpy >= 1.17.0', 'cartopy >= 0.17.0', 'h5py >= 2.9.0'],
)
