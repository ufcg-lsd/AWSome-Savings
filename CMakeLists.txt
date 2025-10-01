cmake_minimum_required(VERSION 3.20)
project(awsome_savings CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ortools CONFIG REQUIRED)    # provided by your OR-Tools install
find_package(Protobuf REQUIRED)          # system protobuf

add_executable(opt
  implementations/cpp_sp_only/aws_model.cpp
  implementations/cpp_sp_only/build_simulation.cpp
  implementations/cpp_sp_only/csv_parser.cpp
  implementations/cpp_sp_only/validations.cpp
)

target_link_libraries(opt PRIVATE ortools::ortools protobuf::libprotobuf)
