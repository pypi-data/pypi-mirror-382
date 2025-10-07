cmake_minimum_required(VERSION 3.18)
project(gliner LANGUAGES CXX VERSION 0.0.2)

# Update submodules
option(UPDATE_SUBMODULES "Update submodules" ON)
if(UPDATE_SUBMODULES)
    include(cmake/UpdateSubmodules.cmake)
endif()

set(PATCH_TOKENIZERS_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/scripts/patch_tokenizers_cmake.py)
if(EXISTS ${PATCH_TOKENIZERS_SCRIPT})
    find_package(Python3 COMPONENTS Interpreter QUIET)
    if(Python3_Interpreter_FOUND)
        execute_process(
            COMMAND ${Python3_EXECUTABLE} ${PATCH_TOKENIZERS_SCRIPT}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            RESULT_VARIABLE PATCH_TOKENIZERS_RESULT
        )
        if(NOT PATCH_TOKENIZERS_RESULT EQUAL 0)
            message(FATAL_ERROR "Failed to patch tokenizers CMake files (exit code: ${PATCH_TOKENIZERS_RESULT}).")
        endif()
    else()
        message(WARNING "Python3 interpreter not found; skipping tokenizers-cpp CMake patching.")
    endif()
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(PCRE2_VERSION "10.44")

if (MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

include(FetchContent)

FetchContent_Declare(
    pcre2
    GIT_REPOSITORY https://github.com/PCRE2Project/pcre2.git
    GIT_TAG pcre2-${PCRE2_VERSION}
)

set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "Build 8bit PCRE2 library")
set(PCRE2_BUILD_PCRE2_16 OFF CACHE BOOL "Build 16bit PCRE2 library")
set(PCRE2_BUILD_PCRE2_32 OFF CACHE BOOL "Build 32bit PCRE2 library")
set(PCRE2_BUILD_TESTS OFF CACHE BOOL "Build PCRE2 tests")
set(PCRE2_BUILD_PROGRAMS OFF CACHE BOOL "Build PCRE2 programs")
set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "Build pcre2grep utility")

# Fetch and make PCRE2 available
FetchContent_MakeAvailable(pcre2)

set(PCRE2_INCLUDE_DIRS ${pcre2_SOURCE_DIR}/src ${pcre2_BINARY_DIR}/src)
set(PCRE2_LIBRARIES pcre2-8)

foreach(_pcre_prog IN ITEMS pcre2grep pcre2test)
    if(TARGET ${_pcre_prog})
        set_target_properties(${_pcre_prog} PROPERTIES EXCLUDE_FROM_ALL TRUE EXCLUDE_FROM_DEFAULT_BUILD TRUE)
    endif()
endforeach()

option(BUILD_EXAMPLES "Build example programs" OFF)
option(BUILD_PYTHON "Build Python bindings" OFF)

# ONNX Runtime setup
set(ONNXRUNTIME_ROOTDIR "" CACHE PATH "Root directory containing the ONNX Runtime headers and libraries")
set(ONNXRUNTIME_VERSION "1.19.2" CACHE STRING "ONNX Runtime version used when downloading a prebuilt package")
option(DOWNLOAD_ONNXRUNTIME "Automatically download a suitable prebuilt ONNX Runtime package" ON)

if(NOT ONNXRUNTIME_ROOTDIR AND DEFINED ENV{ONNXRUNTIME_ROOTDIR})
    set(ONNXRUNTIME_ROOTDIR $ENV{ONNXRUNTIME_ROOTDIR})
endif()

if(NOT ONNXRUNTIME_ROOTDIR)
    if(DOWNLOAD_ONNXRUNTIME)
        if(WIN32)
            set(_onnxruntime_package "onnxruntime-win-x64-${ONNXRUNTIME_VERSION}")
            set(_onnxruntime_archive "${_onnxruntime_package}.zip")
        elseif(APPLE)
            set(_onnxruntime_package "onnxruntime-osx-universal2-${ONNXRUNTIME_VERSION}")
            set(_onnxruntime_archive "${_onnxruntime_package}.tgz")
        elseif(UNIX)
            set(_onnxruntime_package "onnxruntime-linux-x64-${ONNXRUNTIME_VERSION}")
            set(_onnxruntime_archive "${_onnxruntime_package}.tgz")
        else()
            message(FATAL_ERROR "Automatic ONNX Runtime download is not supported on this platform. Please set ONNXRUNTIME_ROOTDIR manually.")
        endif()

        set(_onnxruntime_url "https://github.com/microsoft/onnxruntime/releases/download/v${ONNXRUNTIME_VERSION}/${_onnxruntime_archive}")
        message(STATUS "Fetching ONNX Runtime from ${_onnxruntime_url}")

        FetchContent_Declare(onnxruntime_prebuilt
            URL ${_onnxruntime_url}
        )

        FetchContent_GetProperties(onnxruntime_prebuilt)
        if(NOT onnxruntime_prebuilt_POPULATED)
            FetchContent_Populate(onnxruntime_prebuilt)
        endif()

        set(ONNXRUNTIME_ROOTDIR ${onnxruntime_prebuilt_SOURCE_DIR})
        if(EXISTS ${ONNXRUNTIME_ROOTDIR}/${_onnxruntime_package})
            set(ONNXRUNTIME_ROOTDIR ${ONNXRUNTIME_ROOTDIR}/${_onnxruntime_package})
        endif()
    else()
        message(FATAL_ERROR "The ONNXRuntime path must be specified. Set ONNXRUNTIME_ROOTDIR or enable DOWNLOAD_ONNXRUNTIME.")
    endif()
endif()

if(NOT EXISTS ${ONNXRUNTIME_ROOTDIR})
    message(FATAL_ERROR "Resolved ONNXRUNTIME_ROOTDIR (${ONNXRUNTIME_ROOTDIR}) does not exist")
endif()

set(ONNXRUNTIME_LIB_DIR ${ONNXRUNTIME_ROOTDIR}/lib)
if(NOT EXISTS ${ONNXRUNTIME_LIB_DIR} AND EXISTS ${ONNXRUNTIME_ROOTDIR}/lib64)
    set(ONNXRUNTIME_LIB_DIR ${ONNXRUNTIME_ROOTDIR}/lib64)
endif()

if(NOT EXISTS ${ONNXRUNTIME_LIB_DIR})
    message(FATAL_ERROR "Could not locate ONNX Runtime libraries under ${ONNXRUNTIME_ROOTDIR}. Expected lib or lib64 directory.")
endif()

set(ONNXRUNTIME_INCLUDE
    ${ONNXRUNTIME_ROOTDIR}/include
    ${ONNXRUNTIME_ROOTDIR}/include/onnxruntime
    ${ONNXRUNTIME_ROOTDIR}/include/onnxruntime/core/session
)

include_directories(
    ${ONNXRUNTIME_INCLUDE}
)

link_directories(${ONNXRUNTIME_LIB_DIR})

file(GLOB ONNXRUNTIME_SHARED_LIBS
    "${ONNXRUNTIME_LIB_DIR}/*${CMAKE_SHARED_LIBRARY_SUFFIX}"
)
if(UNIX AND NOT APPLE)
    file(GLOB ONNXRUNTIME_VERSIONED_SHARED_LIBS
        "${ONNXRUNTIME_LIB_DIR}/*${CMAKE_SHARED_LIBRARY_SUFFIX}.*"
    )
    list(APPEND ONNXRUNTIME_SHARED_LIBS ${ONNXRUNTIME_VERSIONED_SHARED_LIBS})
endif()
if(WIN32)
    file(GLOB ONNXRUNTIME_BIN_DLLS
        "${ONNXRUNTIME_ROOTDIR}/bin/*.dll"
    )
    list(APPEND ONNXRUNTIME_SHARED_LIBS ${ONNXRUNTIME_BIN_DLLS})
endif()

if(ONNXRUNTIME_SHARED_LIBS)
    list(REMOVE_DUPLICATES ONNXRUNTIME_SHARED_LIBS)
    set(ONNXRUNTIME_RUNTIME_LIBS ${ONNXRUNTIME_SHARED_LIBS} CACHE INTERNAL "ONNX Runtime shared libraries to bundle")
endif()

option(GPU_CHECK "Check GPU dependencies." OFF)
if (GPU_CHECK)
    execute_process(
        COMMAND nvidia-smi
        RESULT_VARIABLE NVIDIA_SMI_RESULT
        OUTPUT_QUIET
        ERROR_QUIET
    )

    if(NOT NVIDIA_SMI_RESULT EQUAL 0)
        message(WARNING "NVIDIA GPU driver was not detected or nvidia-smi command not available")
        set(GPU_CHECK OFF)
    endif()

    execute_process(
        COMMAND nvcc --version
        RESULT_VARIABLE NVCC_RESULT
        OUTPUT_QUIET
        ERROR_QUIET
    )

    if(NOT NVCC_RESULT EQUAL 0)
        message(WARNING "NVIDIA GPU compiler was not detected or nvcc --version command not available.")
        set(GPU_CHECK OFF)
    endif()

    find_library(CUDNN_LIB
        NAMES cudnn
        PATHS CMAKE_CXX_STANDARD_LIBRARIES CMAKE_C_STANDARD_LIBRARIES
        DOC "Path to cuDNN library"
    )

    if(NOT CUDNN_LIB)
        message(WARNING "cuDNN not found. Ensure that cuDNN is installed and available in the system paths.")
        set(GPU_CHECK OFF)
    endif()

    if (NOT GPU_CHECK)
        message(FATAL_ERROR "CUDA GPU dependencies were not resolved. Please check the logs and try again.")
    endif()
endif()

find_library(ONNXRUNTIME_LIB
    NAMES onnxruntime libonnxruntime
    PATHS ${ONNXRUNTIME_LIB_DIR}
    NO_DEFAULT_PATH
)

if(NOT ONNXRUNTIME_LIB)
    message(FATAL_ERROR "ONNXRuntime library not found. Please check the library path.")
endif()

execute_process(
    COMMAND cargo --version
    RESULT_VARIABLE CARGO_RESULT
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT CARGO_RESULT EQUAL 0)
    message(FATAL_ERROR "Cargo is not available. You can install it by following the instructions here: https://www.rust-lang.org/tools/install")
    set(GPU_CHECK OFF)
endif()

add_subdirectory(deps)
add_subdirectory(src)

if(BUILD_PYTHON)
    add_subdirectory(bindings)
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build (Debug or Release)" FORCE)
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    include(CTest)
    add_subdirectory(tests)
endif()
