find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(gliner_cpp MODULE python.cpp)

target_link_libraries(gliner_cpp PRIVATE gliner)

target_include_directories(gliner_cpp PRIVATE
    ${PROJECT_SOURCE_DIR}/include
)

set_target_properties(gliner_cpp PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)

if(APPLE)
    set_target_properties(gliner_cpp PROPERTIES
        BUILD_RPATH "@loader_path"
        INSTALL_RPATH "@loader_path"
    )
elseif(UNIX)
    set_target_properties(gliner_cpp PROPERTIES
        BUILD_RPATH "$ORIGIN"
        INSTALL_RPATH "$ORIGIN"
    )
endif()

if(DEFINED ONNXRUNTIME_RUNTIME_LIBS)
    set(_onnxruntime_runtime_files)
    foreach(runtime_lib IN LISTS ONNXRUNTIME_RUNTIME_LIBS)
        if(EXISTS ${runtime_lib} AND NOT IS_DIRECTORY ${runtime_lib})
            list(APPEND _onnxruntime_runtime_files ${runtime_lib})
            add_custom_command(TARGET gliner_cpp POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    ${runtime_lib}
                    $<TARGET_FILE_DIR:gliner_cpp>
            )
        endif()
    endforeach()

    if(_onnxruntime_runtime_files)
        install(FILES ${_onnxruntime_runtime_files} DESTINATION .)
    endif()
endif()

install(TARGETS gliner_cpp
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .
    ARCHIVE DESTINATION .
)

install(FILES ${PROJECT_SOURCE_DIR}/bindings/gliner_cpp.pyi
    DESTINATION .
)
