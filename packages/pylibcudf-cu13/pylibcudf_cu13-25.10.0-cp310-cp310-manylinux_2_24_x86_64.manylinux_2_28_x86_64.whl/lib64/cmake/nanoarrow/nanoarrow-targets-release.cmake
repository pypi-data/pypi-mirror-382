#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "nanoarrow::nanoarrow" for configuration "Release"
set_property(TARGET nanoarrow::nanoarrow APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nanoarrow::nanoarrow PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnanoarrow.a"
  )

list(APPEND _cmake_import_check_targets nanoarrow::nanoarrow )
list(APPEND _cmake_import_check_files_for_nanoarrow::nanoarrow "${_IMPORT_PREFIX}/lib/libnanoarrow.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
