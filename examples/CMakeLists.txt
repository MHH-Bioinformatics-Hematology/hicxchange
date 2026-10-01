# The program the documentation shows. It is built with the library so that an
# example that stops compiling fails the build rather than the reader.
add_executable(convert convert.cpp)
target_link_libraries(convert PRIVATE hicxchange::core)
