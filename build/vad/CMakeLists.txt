add_executable(bashkitten-vad main.cpp)
target_include_directories(bashkitten-vad PRIVATE "${CMAKE_SOURCE_DIR}/include")
target_link_libraries(bashkitten-vad PRIVATE whisper)
set_target_properties(bashkitten-vad PROPERTIES CXX_STANDARD 17 RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
