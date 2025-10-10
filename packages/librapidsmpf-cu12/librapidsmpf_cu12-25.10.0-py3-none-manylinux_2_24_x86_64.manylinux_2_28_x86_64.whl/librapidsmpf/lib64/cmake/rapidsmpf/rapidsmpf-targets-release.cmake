#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "rapidsmpf::rapidsmpf" for configuration "Release"
set_property(TARGET rapidsmpf::rapidsmpf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(rapidsmpf::rapidsmpf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/librapidsmpf.so"
  IMPORTED_SONAME_RELEASE "librapidsmpf.so"
  )

list(APPEND _cmake_import_check_targets rapidsmpf::rapidsmpf )
list(APPEND _cmake_import_check_files_for_rapidsmpf::rapidsmpf "${_IMPORT_PREFIX}/lib64/librapidsmpf.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
