#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Ecole::ecole-lib" for configuration "Release"
set_property(TARGET Ecole::ecole-lib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Ecole::ecole-lib PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "fmt::fmt"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libecole.so.0.9.4"
  IMPORTED_SONAME_RELEASE "libecole.so.0.9"
  )

list(APPEND _cmake_import_check_targets Ecole::ecole-lib )
list(APPEND _cmake_import_check_files_for_Ecole::ecole-lib "${_IMPORT_PREFIX}/lib/libecole.so.0.9.4" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
