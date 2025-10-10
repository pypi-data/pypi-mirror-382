#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "raft::raft_lib" for configuration "Release"
set_property(TARGET raft::raft_lib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(raft::raft_lib PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libraft.so"
  IMPORTED_SONAME_RELEASE "libraft.so"
  )

list(APPEND _cmake_import_check_targets raft::raft_lib )
list(APPEND _cmake_import_check_files_for_raft::raft_lib "${_IMPORT_PREFIX}/lib64/libraft.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
