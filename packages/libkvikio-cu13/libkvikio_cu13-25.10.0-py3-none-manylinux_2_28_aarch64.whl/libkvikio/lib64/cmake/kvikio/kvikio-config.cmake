#=============================================================================
# Copyright (c) 2025, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#=============================================================================

#[=======================================================================[

Provide targets for KvikIO.


Result Variables
^^^^^^^^^^^^^^^^

This module will set the following variables::

  KVIKIO_FOUND
  KVIKIO_VERSION
  KVIKIO_VERSION_MAJOR
  KVIKIO_VERSION_MINOR

#]=======================================================================]


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was config.cmake.in                            ########

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

cmake_minimum_required(VERSION 3.30.4)

set(rapids_global_languages )
foreach(lang IN LISTS rapids_global_languages)
  include("${CMAKE_CURRENT_LIST_DIR}/kvikio-${lang}-language.cmake")
endforeach()
unset(rapids_global_languages)

include("${CMAKE_CURRENT_LIST_DIR}/kvikio-dependencies.cmake" OPTIONAL)
include("${CMAKE_CURRENT_LIST_DIR}/kvikio-targets.cmake" OPTIONAL)

if()
  set(kvikio_comp_names )
  # find dependencies before creating targets that use them
  # this way if a dependency can't be found we fail
  foreach(comp IN LISTS kvikio_FIND_COMPONENTS)
    if(${comp} IN_LIST kvikio_comp_names)
      file(GLOB kvikio_component_dep_files LIST_DIRECTORIES FALSE
           "${CMAKE_CURRENT_LIST_DIR}/kvikio-${comp}*-dependencies.cmake")
      foreach(f IN LISTS  kvikio_component_dep_files)
        include("${f}")
      endforeach()
    endif()
  endforeach()

  foreach(comp IN LISTS kvikio_FIND_COMPONENTS)
    if(${comp} IN_LIST kvikio_comp_names)
      file(GLOB kvikio_component_target_files LIST_DIRECTORIES FALSE
           "${CMAKE_CURRENT_LIST_DIR}/kvikio-${comp}*-targets.cmake")
      foreach(f IN LISTS  kvikio_component_target_files)
        include("${f}")
      endforeach()
      set(kvikio_${comp}_FOUND TRUE)
    endif()
  endforeach()
endif()

include("${CMAKE_CURRENT_LIST_DIR}/kvikio-config-version.cmake" OPTIONAL)

# Set our version variables
set(KVIKIO_VERSION_MAJOR 25)
set(KVIKIO_VERSION_MINOR 10)
set(KVIKIO_VERSION_PATCH 00)
set(KVIKIO_VERSION 25.10.00)


set(rapids_global_targets kvikio)
set(rapids_namespaced_global_targets kvikio)
if((NOT "kvikio::" STREQUAL "") AND rapids_namespaced_global_targets)
  list(TRANSFORM rapids_namespaced_global_targets PREPEND "kvikio::")
endif()

foreach(target IN LISTS rapids_namespaced_global_targets)
  if(TARGET ${target})
    get_target_property(_is_imported ${target} IMPORTED)
    get_target_property(_already_global ${target} IMPORTED_GLOBAL)
    if(_is_imported AND NOT _already_global)
      set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
    endif()
  endif()
endforeach()

# For backwards compat
if("rapids_config_install" STREQUAL "rapids_config_build")
  foreach(target IN LISTS rapids_global_targets)
    if(TARGET ${target})
      get_target_property(_is_imported ${target} IMPORTED)
      get_target_property(_already_global ${target} IMPORTED_GLOBAL)
      if(_is_imported AND NOT _already_global)
        set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
      endif()
      if(NOT TARGET kvikio::${target})
        add_library(kvikio::${target} ALIAS ${target})
      endif()
    endif()
  endforeach()
endif()

unset(rapids_comp_names)
unset(rapids_comp_unique_ids)
unset(rapids_global_targets)
unset(rapids_namespaced_global_targets)

check_required_components(kvikio)

set(${CMAKE_FIND_PACKAGE_NAME}_CONFIG "${CMAKE_CURRENT_LIST_FILE}")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(${CMAKE_FIND_PACKAGE_NAME} CONFIG_MODE)


set(KvikIO_CUDA_SUPPORT [=[ON]=])
set(KvikIO_CUFILE_SUPPORT [=[1]=])
set(KvikIO_REMOTE_SUPPORT [=[ON]=])
if(KvikIO_CUDA_SUPPORT)
  find_package(CUDAToolkit REQUIRED QUIET)
  target_include_directories(kvikio::kvikio INTERFACE ${CUDAToolkit_INCLUDE_DIRS})

  if(KvikIO_CUFILE_SUPPORT AND NOT TARGET CUDA::cuFile)
    message(FATAL_ERROR "Compiled with cuFile support but cuFile not found")
  endif()
endif()

