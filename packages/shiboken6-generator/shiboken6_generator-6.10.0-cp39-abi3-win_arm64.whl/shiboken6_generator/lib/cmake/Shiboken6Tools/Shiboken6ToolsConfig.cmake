
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was Shiboken6ToolsConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

cmake_minimum_required(VERSION 3.18)

include(CMakeFindDependencyMacro)
if(NOT CMAKE_CROSSCOMPILING)
    find_dependency(Python COMPONENTS Interpreter Development)

    if(NOT SHIBOKEN6TOOLS_SKIP_FIND_DEPENDENCIES)
        # Dynamically determine Python_SITELIB using Python itself
        execute_process(
            COMMAND ${Python_EXECUTABLE} -c
            "import site; print(next(p for p in site.getsitepackages() if 'site-packages' in p))"
            OUTPUT_VARIABLE Python_SITELIB
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        list(APPEND CMAKE_PREFIX_PATH
            "${Python_SITELIB}/shiboken6/lib/cmake"
            "${Python_SITELIB}/PySide6/lib/cmake"
        )
        find_dependency(Shiboken6 REQUIRED)
        find_dependency(PySide6 REQUIRED)
    endif()
endif()

if(NOT TARGET Shiboken6::shiboken6)
    include("${CMAKE_CURRENT_LIST_DIR}/Shiboken6ToolsTargets.cmake")
endif()

include("${CMAKE_CURRENT_LIST_DIR}/Shiboken6ToolsMacros.cmake")
