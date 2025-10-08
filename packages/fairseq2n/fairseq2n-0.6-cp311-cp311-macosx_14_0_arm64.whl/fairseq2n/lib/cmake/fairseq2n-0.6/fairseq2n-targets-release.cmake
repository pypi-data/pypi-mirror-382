#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "fairseq2n::fairseq2n" for configuration "Release"
set_property(TARGET fairseq2n::fairseq2n APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(fairseq2n::fairseq2n PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "SndFile::sndfile"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libfairseq2n.0.6.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libfairseq2n.0.dylib"
  )

list(APPEND _cmake_import_check_targets fairseq2n::fairseq2n )
list(APPEND _cmake_import_check_files_for_fairseq2n::fairseq2n "${_IMPORT_PREFIX}/lib/libfairseq2n.0.6.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
