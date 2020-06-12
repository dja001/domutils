# Changelog
All notable changes to this project will be documented in this file.

Please use the following tags when editing this file:
*Added* for new features.
*Changed* for changes in existing functionality.
*Deprecated* for soon-to-be removed features.
*Removed* for now removed features.
*Fixed* for any bug fixes. 



## [2.0.6] - 2020-06-11
### Added 
- the rendering of a few images is now checked to ensure proper display of 
   figures uwing cartopy+imshow
- now geo_tools properly handle NaN and infty on cartopy outputs for pixels with no projections
### Fixed
- numpy was complaining about floats used as integers in a couple of places
- fix origin='upper' for all imshow in the code to prevent upside down images on doctest

## [2.0.5] - 2020-06-10
### Added 
- new option to specify the latlon file for Odim H5 radar data in HDF5 format

## [2.0.4] - 2020-05-26
### Fixed
- geo\_tools now works well with Cartopy projection with no extent (ie Robinson).
- grey\_??? / gray\_??? does not crash legs whe called as the first color
- No more dimension problem when specifying only one color
### Added
- Unitest can now be run with `python -m unittest discover`

## [2.0.3] - 2020-02-05
### Changed
- All test data and images now on zenodo
  https://doi.org/10.5281/zenodo.3635906    
  A new download script downloads it automatically at the first time of running tests

## [2.0.2] - 2020-01-31
### Changed
- for some unknown reason wheels now included test_data in the pypi distribution...
  am now manually excluding those with MANIFEST.in

## [2.0.1] - 2020-01-31
### Fixed
- documentation for ProjInds class now displays correctly in documentation

## [2.0.0] - 2020-01-24
### Changed
- First release of domutils on github
- Now adheres to PEP8 for the naming of functions and keywords. 
  This change does break backward compatibility. Sorry for the bother but better now than 
  later I guess. 
