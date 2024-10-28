cmake_minimum_required(VERSION 3.15)

project(
    Learn
    VERSION 1.0
    LANGUAGES CXX
)

add_executable(main src/main.cpp)

add_subdirectory(lib/glfw)

target_link_libraries(main PRIVATE glfw)
target_link_libraries(main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/lib/libglad.a)

target_include_directories(main PRIVATE lib/glfw/include)
target_include_directories(main PRIVATE include)