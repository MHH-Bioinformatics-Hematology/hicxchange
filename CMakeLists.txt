cmake_minimum_required(VERSION 3.21)

project(hicxchange
    VERSION 2.0.0
    DESCRIPTION "Converting Hi-C matrices between the Juicer .hic and the cooler .cool/.mcool formats, both directions; C++ fork of 4dn-dcic/hic2cool"
    LANGUAGES CXX)

include(GNUInstallDirs)

option(HICXCHANGE_BUILD_PYTHON "Build the Python module hicxchange._hicxchange" OFF)
option(HICXCHANGE_BUILD_TESTS "Build and register the tests" ${PROJECT_IS_TOP_LEVEL})

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# The installed hicxchange keeps the directories HDF5 and zlib were
# found in, so that they run outside the build tree without LD_LIBRARY_PATH.
# Package builds (conda, distributions) set their own rpath handling.
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

find_package(HDF5 REQUIRED COMPONENTS C)
find_package(ZLIB REQUIRED)
find_package(Threads REQUIRED)

# hiccpp (.hic reading and writing, 0.4 or newer): an installed package,
# or a source tree given with HICXCHANGE_HICCPP_SOURCE_DIR, or fetched.
if(NOT TARGET hiccpp::hiccpp)
    set(HICXCHANGE_HICCPP_SOURCE_DIR "" CACHE PATH "hiccpp source tree to build with")
    set(HICXCHANGE_HICCPP_GIT_REPOSITORY "" CACHE STRING "hiccpp git repository to fetch")
    set(HICXCHANGE_HICCPP_GIT_TAG "main" CACHE STRING "hiccpp git tag to fetch")
    if(HICXCHANGE_HICCPP_SOURCE_DIR)
        set(HICCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(HICCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
        add_subdirectory(${HICXCHANGE_HICCPP_SOURCE_DIR} ${CMAKE_BINARY_DIR}/hiccpp EXCLUDE_FROM_ALL)
    elseif(HICXCHANGE_HICCPP_GIT_REPOSITORY)
        include(FetchContent)
        set(HICCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(HICCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
        FetchContent_Declare(hiccpp
            GIT_REPOSITORY ${HICXCHANGE_HICCPP_GIT_REPOSITORY}
            GIT_TAG ${HICXCHANGE_HICCPP_GIT_TAG})
        FetchContent_MakeAvailable(hiccpp)
    else()
        find_package(hiccpp 0.4 REQUIRED)
    endif()
endif()

# coolercpp (cool file reading, writing and editing, 0.4 or newer): an installed
# package, or a source tree given with HICXCHANGE_COOLERCPP_SOURCE_DIR, or fetched.
if(NOT TARGET coolercpp::coolercpp)
    set(HICXCHANGE_COOLERCPP_SOURCE_DIR "" CACHE PATH "coolercpp source tree to build with")
    set(HICXCHANGE_COOLERCPP_GIT_REPOSITORY "" CACHE STRING "coolercpp git repository to fetch")
    set(HICXCHANGE_COOLERCPP_GIT_TAG "main" CACHE STRING "coolercpp git tag to fetch")
    if(HICXCHANGE_COOLERCPP_SOURCE_DIR)
        set(COOLERCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(COOLERCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
        add_subdirectory(${HICXCHANGE_COOLERCPP_SOURCE_DIR} ${CMAKE_BINARY_DIR}/coolercpp EXCLUDE_FROM_ALL)
    elseif(HICXCHANGE_COOLERCPP_GIT_REPOSITORY)
        include(FetchContent)
        set(COOLERCPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(COOLERCPP_BUILD_HARNESS OFF CACHE BOOL "" FORCE)
        FetchContent_Declare(coolercpp
            GIT_REPOSITORY ${HICXCHANGE_COOLERCPP_GIT_REPOSITORY}
            GIT_TAG ${HICXCHANGE_COOLERCPP_GIT_TAG})
        FetchContent_MakeAvailable(coolercpp)
    else()
        find_package(coolercpp 0.4 REQUIRED)
    endif()
endif()

configure_file(include/hicxchange/version.hpp.in ${CMAKE_CURRENT_BINARY_DIR}/generated/hicxchange/version.hpp @ONLY)

add_library(hicxchange_core STATIC
    src/convert.cpp
    src/cool2hic.cpp
    src/extract_norms.cpp
    src/hic_header.cpp
    src/runtime.cpp
    src/pyformat.cpp
    src/update.cpp)
target_include_directories(hicxchange_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_BINARY_DIR}/generated
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(hicxchange_core
    PUBLIC hiccpp::hiccpp coolercpp::coolercpp
    PRIVATE HDF5::HDF5 ZLIB::ZLIB Threads::Threads)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(hicxchange_core PRIVATE -Wall -Wextra)
endif()

add_library(hicxchange::core ALIAS hicxchange_core)

# As a subproject (add_subdirectory from another project) only the library is
# provided: no executables, Python module or tests.
if(NOT PROJECT_IS_TOP_LEVEL)
    return()
endif()

# One executable with the subtools hic2cool and cool2hic.
add_executable(hicxchange
    apps/hicxchange_main.cpp
    apps/hic2cool_tool.cpp
    apps/cool2hic_tool.cpp)
target_link_libraries(hicxchange PRIVATE hicxchange_core)

if(SKBUILD)
    install(TARGETS hicxchange RUNTIME DESTINATION ${SKBUILD_SCRIPTS_DIR})
else()
    install(TARGETS hicxchange RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if(HICXCHANGE_BUILD_PYTHON)
    find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)
    pybind11_add_module(_hicxchange python/module.cpp)
    target_link_libraries(_hicxchange PRIVATE hicxchange_core)
    if(SKBUILD)
        install(TARGETS _hicxchange LIBRARY DESTINATION hicxchange)
    endif()
endif()

if(HICXCHANGE_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
