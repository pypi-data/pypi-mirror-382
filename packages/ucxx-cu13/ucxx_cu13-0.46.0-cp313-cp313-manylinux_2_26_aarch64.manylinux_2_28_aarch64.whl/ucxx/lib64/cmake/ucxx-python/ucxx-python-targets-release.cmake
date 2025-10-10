#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ucxx::python" for configuration "Release"
set_property(TARGET ucxx::python APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ucxx::python PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/ucxx/lib64/libucxx_python.so"
  IMPORTED_SONAME_RELEASE "libucxx_python.so"
  )

list(APPEND _cmake_import_check_targets ucxx::python )
list(APPEND _cmake_import_check_files_for_ucxx::python "${_IMPORT_PREFIX}/ucxx/lib64/libucxx_python.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
