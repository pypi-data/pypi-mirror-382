#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ucxx::ucxx" for configuration "Release"
set_property(TARGET ucxx::ucxx APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ucxx::ucxx PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libucxx.so"
  IMPORTED_SONAME_RELEASE "libucxx.so"
  )

list(APPEND _cmake_import_check_targets ucxx::ucxx )
list(APPEND _cmake_import_check_files_for_ucxx::ucxx "${_IMPORT_PREFIX}/lib64/libucxx.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
