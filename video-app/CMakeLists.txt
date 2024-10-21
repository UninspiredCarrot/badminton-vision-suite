cmake_minimum_required(VERSION 3.14)
project(video-app C CXX)

set(CMAKE_CXX_STANDARD 14)

# Find and link to OpenGL and glfw
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)

# Include FFmpeg subdirectory
add_subdirectory(lib/FFmpeg)

# Add source files for the project
list(APPEND SOURCES
    src/main.cpp
    src/load_frame.cpp
)

# Create the video-app executable
add_executable(video-app ${SOURCES})

# Link against FFmpeg, OpenGL, and glfw
target_link_libraries(video-app FFmpeg OpenGL::GL glfw)
