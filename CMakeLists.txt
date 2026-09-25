cmake_minimum_required(VERSION 3.21)

project(hic2cool
    VERSION 2.0.0
    DESCRIPTION "Converter between .hic files (Juicer) and .cool/.mcool files (cooler); C++ fork of 4dn-dcic/hic2cool"
    LANGUAGES CXX)

include(GNUInstallDirs)

option(HIC2COOL_BUILD_PYTHON "Build the Python module hic2cool._hic2cool" OFF)
option(HIC2COOL_BUILD_TESTS "Build and register the tests" ${PROJECT_IS_TOP_LEVEL})

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# The installed hic2cool and cool2hic keep the directories HDF5 and zlib were
# found in, so that they run outside the build tree without LD_LIBRARY_PATH.
# Package builds (conda, distributions) set their own rpath handling.
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

find_package(HDF5 REQUIRED COMPONENTS C)
find_package(ZLIB REQUIRED)
find_package(Threads REQUIRED)

# hicfilecpp (.hic reading and writing, 0.4 or newer): an installed package,
# or a source tree given with HIC2COOL_HICFILECPP_SOURCE_DIR, or fetched.
set(HIC2COOL_HICFILECPP_SOURCE_DIR "" CACHE PATH "hicfilecpp source tree to build with")
set(HIC2COOL_HICFILECPP_GIT_REPOSITORY "" CACHE STRING "hicfilecpp git repository to fetch")
set(HIC2COOL_HICFILECPP_GIT_TAG "main" CACHE STRING "hicfilecpp git tag to fetch")
if(HIC2COOL_HICFILECPP_SOURCE_DIR)
    set(HICFILECPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(HICFILECPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
    add_subdirectory(${HIC2COOL_HICFILECPP_SOURCE_DIR} ${CMAKE_BINARY_DIR}/hicfilecpp EXCLUDE_FROM_ALL)
elseif(HIC2COOL_HICFILECPP_GIT_REPOSITORY)
    include(FetchContent)
    set(HICFILECPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(HICFILECPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(hicfilecpp
        GIT_REPOSITORY ${HIC2COOL_HICFILECPP_GIT_REPOSITORY}
        GIT_TAG ${HIC2COOL_HICFILECPP_GIT_TAG})
    FetchContent_MakeAvailable(hicfilecpp)
else()
    find_package(hicfilecpp 0.4 REQUIRED)
endif()

# coolercpp (cool file reading, writing and editing, 0.4 or newer): an installed
# package, or a source tree given with HIC2COOL_COOLERCPP_SOURCE_DIR, or fetched.
set(HIC2COOL_COOLERCPP_SOURCE_DIR "" CACHE PATH "coolercpp source tree to build with")
set(HIC2COOL_COOLERCPP_GIT_REPOSITORY "" CACHE STRING "coolercpp git repository to fetch")
set(HIC2COOL_COOLERCPP_GIT_TAG "main" CACHE STRING "coolercpp git tag to fetch")
if(HIC2COOL_COOLERCPP_SOURCE_DIR)
    set(COOLERCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(COOLERCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
    add_subdirectory(${HIC2COOL_COOLERCPP_SOURCE_DIR} ${CMAKE_BINARY_DIR}/coolercpp EXCLUDE_FROM_ALL)
elseif(HIC2COOL_COOLERCPP_GIT_REPOSITORY)
    include(FetchContent)
    set(COOLERCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(COOLERCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(coolercpp
        GIT_REPOSITORY ${HIC2COOL_COOLERCPP_GIT_REPOSITORY}
        GIT_TAG ${HIC2COOL_COOLERCPP_GIT_TAG})
    FetchContent_MakeAvailable(coolercpp)
else()
    find_package(coolercpp 0.4 REQUIRED)
endif()

configure_file(include/hic2cool/version.hpp.in ${CMAKE_CURRENT_BINARY_DIR}/generated/hic2cool/version.hpp @ONLY)

add_library(hic2cool_core STATIC
    src/convert.cpp
    src/cool2hic.cpp
    src/extract_norms.cpp
    src/hic_header.cpp
    src/runtime.cpp
    src/pyformat.cpp
    src/update.cpp)
target_include_directories(hic2cool_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(hic2cool_core
    PUBLIC hicfilecpp::hicfilecpp coolercpp::coolercpp
    PRIVATE HDF5::HDF5 ZLIB::ZLIB Threads::Threads)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(hic2cool_core PRIVATE -Wall -Wextra)
endif()

add_executable(hic2cool apps/hic2cool_main.cpp)
target_link_libraries(hic2cool PRIVATE hic2cool_core)
add_executable(cool2hic apps/cool2hic_main.cpp)
target_link_libraries(cool2hic PRIVATE hic2cool_core)

if(SKBUILD)
    install(TARGETS hic2cool cool2hic RUNTIME DESTINATION ${SKBUILD_SCRIPTS_DIR})
else()
    install(TARGETS hic2cool cool2hic RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if(HIC2COOL_BUILD_PYTHON)
    find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)
    pybind11_add_module(_hic2cool python/module.cpp)
    target_link_libraries(_hic2cool PRIVATE hic2cool_core)
    if(SKBUILD)
        install(TARGETS _hic2cool LIBRARY DESTINATION hic2cool)
    endif()
endif()

if(HIC2COOL_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
