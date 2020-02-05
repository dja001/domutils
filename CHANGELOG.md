# Changelog
All notable changes to this project will be documented in this file.

Please use the following tags when editing this file:
*Added* for new features.
*Changed* for changes in existing functionality.
*Deprecated* for soon-to-be removed features.
*Removed* for now removed features.
*Fixed* for any bug fixes. 


## [2.0.0] - 2020-01-24
### Changed
- First release of domutils on github
- Now adheres to PEP8 for the naming of functions and keywords. 
  This change does break backward compatibility. Sorry for the bother but better now than 
  later I guess. 

## [2.0.1] - 2020-01-31
### Fixed
- documentation for ProjInds class now displays correctly in documentation

## [2.0.2] - 2020-01-31
### Changed
- for some unknown reason wheels now included test_data in the pypi distribution...
  am now manually excluding those with MANIFEST.in

## [2.0.3] - 2020-02-05
### Changed
- All test data and images now on zenodo
  https://doi.org/10.5281/zenodo.3635906    
  A new download script downloads it automatically at the first time of running tests
