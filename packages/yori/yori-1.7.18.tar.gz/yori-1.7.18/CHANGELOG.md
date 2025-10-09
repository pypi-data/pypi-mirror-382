# Changelog

## 1.7.17 (2025-09-26)

### Bug Fixes

## 1.7.16 (2025-09-25)

### Bug Fixes

- aggregation of min/max was still not working properly. Previous fix didn't
  solve the issue

- fixed a bug with the computation of min in the aggregation where valid zero
  values where replaced with NaN
- fixed warnings for divide by zero

## 1.7.15 (2025-04-16)

### Bug Fixes

- fixed an issue with `yori-grid` not saving the `edges` parameter needed for
  the computation of the median in `yori-aggr`

## 1.7.14 (2025-03-10)

### Improvements/Changes

- added the new option `log_scale` for the median in the configuration file to enable
  logarithmic bins for the computation of the distribution. This should help in reducing
  the number of bins needed to represent the distribution.

## 1.7.13 (2025-02-27)

### Bug Fixes

- logic to filter for `min-valid-days` was broken. This is now fixed

### Improvements/Changes

- Python 3.8 is past EOL and support for it has been dropped.
- the median computation is now much faster. Yori now approximates the median
  using the remedian algorithm (see Cantone and Hofri, 2013) during the
  gridding process while buffers the values of each cell during the aggregation
  and then uses the numpy.median function to provide the result. This process
  is much faster than the previous version but the results might not be as
  accurate (see documentation for more details).

### References

Cantone and Hofri, 2013 - Further Analysis of the Remedian Algorithm

## 1.7.12 (2024-10-23)

### Bug Fixes

- fixed `batch-size` argument not properly converted to int in aggregation code

## 1.7.11 (2024-08-14)

### Bug Fixes

- fixed an issue in `yori-aggr` that would cause an error if the
  `only_histograms` option was used in combination with `min_valid_days`

## 1.7.10 (2024-06-24)

### Bug Fixes

- fixed an issue where `yori-aggr` would crash when using the `--min-pixel-counts` flag
  with files that have gridded with the median option

### Other Changes

- `valid_min` and `valid_max` attributes now appear under `Mean` and `Median` variables
  in addition to the group those variables belong to

## 1.7.9 (2023-07-24)

### Bug Fixes

- `units` attribute now gets properly assigned to the `median`

### New Features

- New option `-F`, `--final` in `yori-aggr` allows users to save a "finalized"
  version of L3 that doesn't include any of the quantities used to propagate the
  statistics (i.e. Sum, Sum_Squares, Median_Distribution). This action will
  reduce the file size, but will make the output unusable with Yori.

### Other Changes

- Reduced number of variables in fulltest_config and generated new reference
  test files

## 1.7.8 (2023-07-13)

### Changes

- cli tools have been modified to work well with pyinstaller

## 1.7.7 (2023-06-26)

### Changes

- Python requirement dropped to 3.8 from 3.9

## 1.7.6 (2023-03-23)

### Bug Fixes

- addressed issue with non integer fill values. Yori now throws a warning and
  forces the fill passed fill value to int

## 1.7.5 (2023-03-07)

### Improvements and Changes

- CI has been simplified
- changes to to CI to auto-upload new tags to PyPI

### Bug Fixes

- deprecation warning while reading the configuration file has been addressed. The
  warning was still present despite reporting it fixed in 1.7.2.

### Notes

There will be one or more patches to make sure that these changes work as intended.
Once I'm confident that everything looks good, I'll bump the minor version.

## 1.7.4 (2023-02-03)

- Packaging backend switched to Hatch
- Yori is now available on PyPI.

## 1.7.3 (2022-11-07)

- The MIT license has been added to Yori

## 1.7.2 (2022-04-18)

### New Features

- `min` and `max` computation has been added as an optional statistics. See
  documentation for usage

### Improvements and Fixes

- deprecation warning while reading the configuration file has been addressed
- default compression level in yori-grid changed from 0 to 5

## 1.7.1 (2022-03-28)

### Bug Fixes

- corrected a bug in the computation of the median that returned valuegs with a larger
  bias than intended. Most likely this was caused by an indexing error.
- CI now is working again properly

## 1.7.0 (2022-03-14)

### New Features

- `median` is now available as an option in `yori-grid`. See documentation for how to
  use it (should be updated within a few days from this update).
- new option `--batch-size` is available in `yori-aggr`. This option allows to tune the
  resource usage of `yori-aggr` by changing the number of gridded variables kept in
  memory during the aggregation.

### Improvements and Fixes

- the code has been updated to work with Python 3.9
- New installation uses requirements.txt file to have a more rigorous control on the
  versions of the installed modules.

### Known Issues

- the `--replace` flag in `yori-merge` has not been implemented yet
- some of the checks in `yori-merge` need to be fully implemented
- some file attributes, mainly `daily_defn_of_day_adjustment`, are not properly
  propagated in the merged output
- CI is currently broken because of the changes made to the installation process

## 1.6.7 (2021-09-20) - Latest version for GEWEX

The versions 1.6.1 through 1.6.6 have not been tracked in the changelog. The 1.6.x code
is from now on archived and the latest and greatest version (1.6.7 as of Sep, 24th 2021)
is the reference code to use to create files that use the GEWEX conventions. Here below
is a list of the features implemented specifically for the project. This list is only
intended for 1.6.x and, unless otherwise specified, newer versions of Yori will not
contain any of the feature here listed. The code will be rebased to 1.5.0 and the
development will continue from there, while keeping the 1.6.x versions "isolated".

### New Features

- Introduction of new quantities for GEWEX, namely `GEWEX_Mean`,
  `GEWEX_Standard_Deviation`, `Sum_Mean`, `Sum_Squares_Mean`.
- a list of hardcoded variables has been included in the aggregation, to account for the
  fact that variables such as CAE could not be derived directly from L2 data
- various exceptions were hardcoded in the aggregation part of the code to handle the
  differences between the CAE\* variables and AIWP, ALWP, AIWPH.
- The `batching` variable has been changed from 2 to 10 in yori_aggregate to attempt to
  improve performance and memory usage. Future versions of Yori will have this as an
  option for the user.

## 1.6.0 (2021-04-28)

### New Features

- new option `--gewex` added to `yori-aggr`. This option allows the user to compute
  statistics according to GEWEX specifications. See documentation for more info.

## 1.5.0 (2021-03-26)

### New Features

- `yori-merge` tool added to the Yori package. The new tool merges two files previously
  processed with Yori, and containing unique SDS names, into a single output.

### Known Issues

- the `--replace` flag in `yori-merge` has not been implemented yet
- some of the checks in `yori-merge` need to be fully implemented
- some file attributes, mainly `daily_defn_of_day_adjustment`, are not properly
  propagated in the merged output

## 1.4.4 (2020-12-17)

### Fixes

- fixed an issue with `Num_Days` that was erroneously included in the D3 files and, as a
  result, affected the computation of `Num_Days` in the M3 files

## 1.4.3 (2020-11-18)

### Fixes

- fixed incorrect placement of valid_days counter that caused incorrect computation of
  `Num_Days`

### Improvements

- changes have been made to `yori_aggregate` to simplify the new code blocks and make
  them more readable

## 1.4.2 (2020-10-26)

### Fixes

- corrected an issue in the computation of the weighted standard deviation

## 1.4.1 (2020-10-14)

### Changes/Fixes

- the number of valid days is now computed correctly within the code
- `min_pixel_counts` temporary variable removed from the final output. Additional
  code has been written to account for temporary variables not being removed properly
- `Num_Days` variable added to the final output
- various debugging messages removed
- an exception to handle ruamel.yaml vs ruamel_yaml imports has been added

## 1.4.0 (2020-07-22)

# New Features

- computation of weighted statistics is now available by adding an option to the
  configuration file
- filtering variable aggregation based on minimum number of pixels or minimum number
  of days per grid cell has been added

Please see documentation for details

## 1.3.16 (2020-06-25)

## Changes

- name of global attribute `daily` in the aggregated files has been changed to
  `daily_defn_of_day_adjustment` to be more clear of its meaning

## 1.3.15 (2020-06-15)

### Changes/Fixes

- A change that deprecated the use of `lat_in` and `lon_in` in the configuration file
  has been rolled back.
- The input files for `test_grid_dummy` have been slightly modified to include the
  testing of the coordinates naming.

## 1.3.14 (2020-05-21)

### Changes

- Dimension name slightly changed again for clarity. Now dimensions for Histogram and
  Joint Histogram will have the prefix "histo*" and "jhisto*" to identify what they
  are referring to
- `lat_in` and `lon_in` options in the configuration file have been deprecated and they
  will not be read by Yori. The default input names for the coordinates are `latitude`
  and `longitude`. An error has been added in order to be able to track this error easily
  if needed.

### Fixes

- the "print" statements present in the previous tag have been removed. The code now
  should run smoothly without outputting anything that is not intended.

## 1.3.13 (2020-04-15)

### Changes

- The netcdf output of the code now contains dimensions with more meaningful names.
  Dimension names are derived from the variable they represent and the actual value
  is also appended at the end. The resulting format is `variable_name_00`. The only
  exceptions are `latitude` and `longitude`.

### Known Issues

- some "print" instructions intended for debugging are still in the code, as a result
  Yori prints out a lot of unintended messages in the terminal. This doesn't have any
  effect on the end results.

## 1.3.12 (2020-03-03)

### Improvements

- The aggregation component of the code has been reworked to be less resource-hungry.
  As a direct consequence the whole yori-aggr is not only more efficient but also faster.

## 1.3.11 (2020-02-14)

### New Features

- A new set of tests for CI to verify the consistency of results during changes has been
  implemented.
- Test and reference files have been created and added to the repository.
- The code has been cleaned up of all the unused parts.
- New, simplified tools for writing output files have been created to replace the old
  ioutils.

### Fixed Bugs

- Solved fill value issue #24. Default fill value changed to -9999
- `--verbose` mode in `yori-grid` has been completely removed since it is not useful
  anymore

## 1.3.10 (2019-09-12)

### Fixes

corrected an issue that could cause an error if no attributes were defined
in the conifguration file

## 1.3.9 (2019-07-29)

### Fixes

The `units` attribute was accidentally removed from the `Mean` and
`Standard_Deviation` variables in the previous patch.

## 1.3.8 (2019-07-09)

### Changes

The attribute 'title' has been added to the variables in order to make the
output files work better with Panoply

## 1.3.7 (2019-04-11)

### New features

The definition of day in `yori-aggr` has been changed to match the one used
by NASA. `--daily` now requires the extra argument `--method` that accepts
the options `c6aqua` and `c6terra` for C6 Aqua and Terra respectively.

## 1.3.6 (2019-02-15)

### General Comment

The aggregation process has been strongly optimized and it is now much faster
than in previous versions. Other than this, the code has not been changed.

## 1.3.5 (2018-12-07)

### General Comment

The `Pixel_Counts`, that was previously initialized as FillValues, is now
initialized as 0, because it makes more sense: if there is no data in a given
grid cell the pixel count is zero, same reasoning for the histograms. All other
variables are still initialized as FillValues.

### New Features

- `only_histograms` option makes possible to skip the creation of standard
  statistics (i.e. mean, std, etc,...) and save only histograms and 2D histograms
- histogram bins are now saved as attributes in the output files

### Fixed Bugs

- `only_histograms` now works with `yori-aggr`

## 1.3.4 (2018-11-29)

### Fixed Bugs

- correctly implemented the optimization to affect `yori-aggr` as well

### Known Issues

- attributes for histograms and joint histograms bins missing
- `only_histograms` option not yet implemented in the aggregation

## 1.3.3 (2018-11-28)

### New features

- `yori-grid` optimized to make it faster

### Known Issues

- the changes to the I/O functions are not called correctly

### Known Issues

- attributes for histograms and joint histograms bins
- `only_histograms` option not yet implemented in the aggregation

## 1.3.2 (2018-11-09)

### Fixed Bugs

- all zero values are now fills
- `master_masks` removed

### Known Issues

- Pixel_Counts value for the (89.5S; 179.5W) grid cell is wrong
- Yori does not work when integer data is passed

## 1.3.1 (2018-11-07)

### New Features

- default value for compression level set to 5 to be consistent with SIPS
- Pixel_Counts and Histograms converted to `int` in order to reduce file size
- changes to data type allow for much more manageable file size
- introduction of the `master_masks` option to define masks that sets the
  masked values to Fill instead of zero (see documentation)

### Fixed Bugs

- fixed the default compression level in `yori-aggr` that was causing the code
  to crash

### Known Issues

- Pixel_Counts reports zeros even when it should have fill values (i.e. when
  there is no satellite overpass).
- Histograms and Joint Histograms still do not work with the `master_masks`
  option

## 1.3.0 (2018-09-23)

NOTE: The use of this version is strongly encouraged beacuse of the fixed bugs.
Some of the changes make the files gridded with older versions of yori
impossible to aggregate with the current version.

### New Features

- The computed quantities have been renamed to match those used in
  MODIS L3 as follows:
  - `mean` > `Mean`
  - `standard_deviation` > `Standard_Deviation`
  - `n_points` > `Pixel_Counts`
  - `sum` > `Sum`
  - `sum_squares` > `Sum_Squares`
  - `histograms` > `Histogram_Counts`
- it is now possible to define different bins for histograms and 2D histograms
  within the same variable (see documentation under 2D histograms)
- `yori-aggr` now saves a temp file instead of keeping everything into memory.
  This allows for aggregation of very large files but slows down the entire
  process.
- `long_name` and `units` have been added to `Mean` and `Standard_Deviation`
  to streamline automated imaging.
- it is now possible to compress aggregated outputs

### Fixed Bugs

- `Pixel_Counts` was incorrectly computed. This caused minor biases in
  aggregated `Mean` and `Standard_Deviation`.
- The `Pixel_Counts` was still set to FillValue instead of zero in some limited
  cases.`Sum` and `Sum_Squares` had the same issue
- file compression was not properly utilized in the aggregation

## 1.2.5 (2018-08-15)

Note: The code has been migrated to Python 3

### New Features

- Fill values used to represent "no data" in n_points, sum and sum_squares
- `lat_out`, `lon_out` removed from the configuration file. Now the coordinates in the
  gridded files will always be called `latitude` and `longitude`.
- `yori-grid` now offers the option to compress the output files using `-c` (see
  documentation for more info)
- `File_List` attribute in aggregated files has been changed to `input_files` to
  match SIPS standards

### Fixed Bugs

- `run_grid()` caused the code to crash if an array containing only one value was
  processed

### Known Issues

- `--force` flag inactive in the `-yori-aggr` command line tool
- the CSV config is not compatible with this version

## 1.2.4 (2018-04-30)

### New Features

- `--force` flag removed because unnecessary. If `yori-aggr` is run on files created
  with the `--daily` flag active, a warning is thrown instead
- `attributes` are now defined in a different, more flexible way in the configuration
  file (see documentation).

## 1.2.3 (2018-04-26)

### Fixed Bugs

- `attribute` and `units` in the configuration file cause the code to crash if used

## 1.2.2 (2018-04-23)

### New Features

- `units` has been added as an option in the configuration file (see documentation)
- The CSV configuration file is now again compatible with Yori
- New global attribute in the aggregated files takes note of whether `--daily` has been
  used
- `yori-aggr` now checks if the input files have being created with `--daily` and stops
  if the user tries to aggregate them again
- New `--force` flag added to override the error when the user tries to aggregate files
  created with the `--daily` flag

### Fixed Bugs

- Crash when `--daily` is used and `yori-aggr` processes the 0300Z file of the next day

## 1.2.1 (2018-04-19)

### New Features

- User defined fill values can be specified in the configuration file using the keyword
  `fill_value`

### Fixed Bugs

- `NaN` values at the gridding stage in certain cases cause issues at the aggregation step

### Known Issues

- The CSV configuration file is not compatible with this version yet

## 1.2.0 (2018-03-22)

### New Features

- `yori-aggr` now has the `--daily` flag to allow for daily aggregation. This solves the
  discontinuities around the international date line
- Masks and inverse masks can now be defined simultaneously

### Fixed Bugs

- Documentation on sips.ssec.wisc.edu is pointing to README instead of CHANGELOG
- Masks in joint histograms are not necessarily behaving as intended
- Use of multiple inverse masks can create unexpected results if any of the masks is not
  binary by definition (e.g. not day/night)
- `yori-aggr` throws an unnecessary warning when an empty grid box is processed. This is
  caused by some residual code for the compensated summation

## 1.1.13 (2018-02-01)

### New Features

- Inverse masks
- Changelog available

### Fixed Bugs

- Fill Values attribute not saved correctly

## 1.1.12 (2017-11-30)

### Fixed Bugs

- A few test commands left in the code after the previous update print useless information
  to the user

## 1.1.11 (2017-11-29)

### Fixed Bugs

- Fill values are not read properly in some specific cases

## 1.1.10 (2017-11-01)

### New Features

- Metadata moved to global attributes
- `yori-aggr` now saves the list of files used to create the aggregated file
- `yori-grid` and `yori-aggr` now store the software version used to create the
  gridded/aggregated files
- `yori-aggr` throws a warning if the version used to create the gridded inputs does not
  match its current version
- Yori documentation published on SIPS website

### Fixed Bugs

- `yori-grid` does not work as intended when no masks are provided
- Formatting issue with csv file saved with certain old versions of MS Excel

## 1.1.9 (2017-10-30)

### New Features

- Yori prints an error when attempting to convert a csv configuration file into a yaml
  file that already exists

### Fixed Bugs

- Error in configuration file conversion from YAML to CSV
- Fill values not written by `yori-aggr`
