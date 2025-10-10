#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cumlprims_mg::cumlprims_mg" for configuration "Release"
set_property(TARGET cumlprims_mg::cumlprims_mg APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cumlprims_mg::cumlprims_mg PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libcumlprims_mg.so"
  IMPORTED_SONAME_RELEASE "libcumlprims_mg.so"
  )

list(APPEND _cmake_import_check_targets cumlprims_mg::cumlprims_mg )
list(APPEND _cmake_import_check_files_for_cumlprims_mg::cumlprims_mg "${_IMPORT_PREFIX}/lib64/libcumlprims_mg.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
