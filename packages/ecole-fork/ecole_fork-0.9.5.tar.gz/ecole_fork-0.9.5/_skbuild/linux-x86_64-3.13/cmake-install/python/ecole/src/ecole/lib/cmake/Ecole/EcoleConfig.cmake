
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was EcoleConfig.cmake.in                            ########

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

option(ECOLE_DOWNLOAD_DEPENDENCIES "Download the static and header libraries used in Ecole public interface" ON)
if(ECOLE_DOWNLOAD_DEPENDENCIES)
	include("${CMAKE_CURRENT_LIST_DIR}/DependenciesResolver.cmake")
	include("${CMAKE_CURRENT_LIST_DIR}/public.cmake")
endif()

include(CMakeFindDependencyMacro)
find_dependency(xtensor 0.23.1 REQUIRED)
find_dependency(SCIP  REQUIRED)
find_dependency(span-lite 0.9.0 REQUIRED)
find_package(Threads REQUIRED)

if(NOT TARGET Ecole::ecole-lib)
	include("${CMAKE_CURRENT_LIST_DIR}/EcoleTargets.cmake")
endif()
