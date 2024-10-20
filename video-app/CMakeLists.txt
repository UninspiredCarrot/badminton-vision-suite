cmake_minimum_required(VERSION 3.14)
project(video-app C CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)

add_executable(video-app src/main.cpp)
target_link_libraries(video-app OpenGL::GL glfw)
