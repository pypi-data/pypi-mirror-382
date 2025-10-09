cmake_minimum_required(VERSION 3.15)
project(mcap_bag_parser)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Option to enable rosx_introspection support
option(BUILD_ROSX_SUPPORT "Build rosx_introspection support" ON)

if(BUILD_ROSX_SUPPORT)
    # Enable Python bindings for rosx_introspection
    set(ROSX_PYTHON_BINDINGS ON CACHE BOOL "Build Python bindings" FORCE)
    set(ROSX_HAS_JSON OFF CACHE BOOL "Disable JSON support to avoid rapidjson issues" FORCE)

    # Add rosx_introspection as subdirectory
    add_subdirectory(external/rosx_introspection)

    # After building the submodule, install the Python extension properly
    if(TARGET rosx_introspection_py)
        # Install the extension to our package (keep original name)
        install(TARGETS rosx_introspection_py
                LIBRARY DESTINATION rosx_introspection
                RUNTIME DESTINATION rosx_introspection)
    endif()
endif()