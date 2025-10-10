#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cuml::cuml++" for configuration "Release"
set_property(TARGET cuml::cuml++ APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cuml::cuml++ PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "cumlprims_mg::cumlprims_mg"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libcuml++.so"
  IMPORTED_SONAME_RELEASE "libcuml++.so"
  )

list(APPEND _cmake_import_check_targets cuml::cuml++ )
list(APPEND _cmake_import_check_files_for_cuml::cuml++ "${_IMPORT_PREFIX}/lib64/libcuml++.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
