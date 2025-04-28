add_library(TriangulationModule STATIC
        DCEL.cpp
        Monotone.cpp
        Triangulate.cpp
)

target_include_directories(TriangulationModule PUBLIC ${CMAKE_ROOT_DIR}/include)