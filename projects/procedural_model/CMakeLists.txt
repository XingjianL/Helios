# Helios standard CMakeLists.txt file version 1.10
cmake_minimum_required(VERSION 3.15)
project(helios)

#-------- USER INPUTS ---------#

#provide the path to Helios base directory, either as an absolut path or a path relative to the location of this file
set( BASE_DIRECTORY "../.." )
	
#define the name of the executable to be created
set( EXECUTABLE_NAME "procedural_model" )

#provide name of source file(s) (separate multiple file names with semicolon)
set( SOURCE_FILES "main.cpp" )

#specify which plug-ins to use (separate plug-in names with semicolon)
set( PLUGINS "plantarchitecture" )
set( PYTHON_SCRIPTS 
    "${CMAKE_CURRENT_SOURCE_DIR}/preprocess_mesh.py" 
    "${CMAKE_CURRENT_SOURCE_DIR}/unique_leaves.py"
)
# --- COPY SCRIPTS DURING BUILD ---
# 1. Define the destination as the current build directory where the executable lives
set( SCRIPT_DEST_DIR ${CMAKE_CURRENT_BINARY_DIR} ) 

# 2. Define a custom target that uses the CMake -E copy command
add_custom_target(CopyScriptsToBuild ALL
    COMMAND ${CMAKE_COMMAND} -E copy ${PYTHON_SCRIPTS} ${SCRIPT_DEST_DIR}
    COMMENT "Copying Python scripts to the build directory"
)

# 3. Ensure the main executable depends on this target
# This guarantees that the copy happens every time you build the executable.
#-------- DO NOT MODIFY ---------#
include( "${BASE_DIRECTORY}/core/CMake_project.cmake" )
add_dependencies(${EXECUTABLE_NAME} CopyScriptsToBuild)

find_path(ASIO_INCLUDE_DIR asio.hpp)
find_package(PkgConfig REQUIRED)
pkg_check_modules(BSON REQUIRED libbson-1.0)

include_directories(${BSON_INCLUDE_DIRS})
link_directories(${BSON_LIBRARY_DIRS})

target_link_libraries(${EXECUTABLE_NAME} PRIVATE ${BSON_LIBRARIES})