# The Python test suite (test.py: the original hic2cool tests plus the fork's)
# runs against the extension module built here, from a copy of the package in
# the build tree. It needs a Python with pytest, h5py, numpy and cooler.

if(NOT HIC2COOL_BUILD_PYTHON)
    message(STATUS "hic2cool: tests need HIC2COOL_BUILD_PYTHON=ON; none registered")
    return()
endif()

set(TEST_ROOT ${CMAKE_CURRENT_BINARY_DIR}/suite)
add_test(NAME prepare_suite
    COMMAND ${CMAKE_COMMAND}
        -DSOURCE_DIR=${PROJECT_SOURCE_DIR}
        -DTEST_ROOT=${TEST_ROOT}
        -DMODULE=$<TARGET_FILE:_hic2cool>
        -P ${CMAKE_CURRENT_SOURCE_DIR}/prepare_suite.cmake)
set_tests_properties(prepare_suite PROPERTIES FIXTURES_SETUP suite)

add_test(NAME python_suite
    COMMAND ${Python_EXECUTABLE} -m pytest -q -p no:cacheprovider test.py
    WORKING_DIRECTORY ${TEST_ROOT})
set_tests_properties(python_suite PROPERTIES FIXTURES_REQUIRED suite TIMEOUT 1800)

add_test(NAME cli_help COMMAND $<TARGET_FILE:hic2cool> convert -h)
set_tests_properties(cli_help PROPERTIES PASS_REGULAR_EXPRESSION "usage: hic2cool convert")
add_test(NAME cli_version COMMAND $<TARGET_FILE:cool2hic> --version)
set_tests_properties(cli_version PROPERTIES PASS_REGULAR_EXPRESSION "cool2hic ${PROJECT_VERSION}")
add_test(NAME cli_error COMMAND $<TARGET_FILE:hic2cool> convert)
set_tests_properties(cli_error PROPERTIES WILL_FAIL TRUE)
