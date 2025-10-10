#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudf::cudf" for configuration "Release"
set_property(TARGET cudf::cudf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudf::cudf PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "nvcomp::nvcomp;kvikio::kvikio"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libcudf.so"
  IMPORTED_SONAME_RELEASE "libcudf.so"
  )

list(APPEND _cmake_import_check_targets cudf::cudf )
list(APPEND _cmake_import_check_files_for_cudf::cudf "${_IMPORT_PREFIX}/lib64/libcudf.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
