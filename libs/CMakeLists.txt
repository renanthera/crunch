add_library(libs LinkedList.cpp)

target_include_directories(libs
INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
)
