#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "kvikio::kvikio" for configuration "Release"
set_property(TARGET kvikio::kvikio APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(kvikio::kvikio PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libkvikio.so"
  IMPORTED_SONAME_RELEASE "libkvikio.so"
  )

list(APPEND _cmake_import_check_targets kvikio::kvikio )
list(APPEND _cmake_import_check_files_for_kvikio::kvikio "${_IMPORT_PREFIX}/lib64/libkvikio.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
