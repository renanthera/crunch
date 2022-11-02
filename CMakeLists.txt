
cmake_minimum_required(VERSION 3.24)
project(crunch VERSION 0.1)
add_executable(crunch main.cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_BUILD_TYPE RelWithDebInfo)

# use this to embed keys into binary from external file that is .gitignored
# configure_file

add_subdirectory(libs)
list(APPEND EXTRA_LIBS libs)
list(APPEND EXTRA_INCLUDES "${PROJECT_SOURCE_DIR}/libs")

target_link_libraries(crunch PUBLIC ${EXTRA_LIBS})

target_include_directories(crunch PUBLIC
  "${PROJECT_BINARY_DIR}"
  "${EXTRA_INCLUDES}"
  )
