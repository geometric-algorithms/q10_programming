cmake_minimum_required(VERSION 3.31)
project(SimplePolygonTriangulation)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})
set(CMAKE_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

include_directories(${CMAKE_ROOT_DIR}/include)

add_subdirectory(${CMAKE_SOURCE_DIR})

add_executable(triangulate
        main.cpp)

target_link_libraries(triangulate TriangulationModule)

