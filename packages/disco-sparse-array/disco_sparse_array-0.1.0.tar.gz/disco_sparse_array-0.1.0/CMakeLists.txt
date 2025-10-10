cmake_minimum_required(VERSION 3.18)
project(sparse_array LANGUAGES CXX)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_core src/sparse_array/_core.cpp)
target_compile_features(_core PRIVATE cxx_std_17)

install(TARGETS _core
        LIBRARY DESTINATION sparse_array
        ARCHIVE DESTINATION sparse_array
        RUNTIME DESTINATION sparse_array)
