# Copies the package, test.py and test_data into TEST_ROOT and puts the built
# extension module next to the package's Python files.
file(REMOVE_RECURSE ${TEST_ROOT})
file(MAKE_DIRECTORY ${TEST_ROOT})
file(COPY ${SOURCE_DIR}/hic2cool ${SOURCE_DIR}/test_data ${SOURCE_DIR}/test.py DESTINATION ${TEST_ROOT})
file(COPY ${MODULE} DESTINATION ${TEST_ROOT}/hic2cool)
