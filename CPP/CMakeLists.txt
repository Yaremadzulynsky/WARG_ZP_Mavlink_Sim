cmake_minimum_required(VERSION 3.10)
project(MAVLinkUDP)

set(CMAKE_CXX_STANDARD 11)

# Add the path to your MAVLink headers
include_directories(./c_library_v2/common)

add_executable(MAVLinkUDP main.cpp)
