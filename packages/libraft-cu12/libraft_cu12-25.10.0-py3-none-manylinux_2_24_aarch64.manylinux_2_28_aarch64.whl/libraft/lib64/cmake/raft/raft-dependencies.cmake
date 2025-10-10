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

include(CMakeFindDependencyMacro)

set(CCCL_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../rapids/cmake/cccl")
set(NvidiaCutlass_ROOT "${CMAKE_CURRENT_LIST_DIR}/../")
find_dependency(CUDAToolkit)

find_dependency(OpenMP)

find_package(rapids_logger 0.1.0 QUIET)
find_dependency(rapids_logger)

find_package(CCCL 3.0.3 QUIET)
find_dependency(CCCL)

if(CCCL_FOUND)
    target_compile_definitions(CCCL::CCCL INTERFACE CUB_DISABLE_NAMESPACE_MAGIC)
    target_compile_definitions(CCCL::CCCL INTERFACE CUB_IGNORE_NAMESPACE_MAGIC_ERROR)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_DISABLE_ABI_NAMESPACE)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_IGNORE_ABI_NAMESPACE_ERROR)
    target_compile_definitions(CCCL::CCCL INTERFACE CCCL_DISABLE_PDL)
    

endif()
find_package(rmm 25.10 QUIET)
find_dependency(rmm)

find_dependency(NvidiaCutlass)

find_package(cuco 0.0.1 QUIET)
find_dependency(cuco)


set(rapids_global_targets CCCL;CCCL::CCCL;CCCL::CUB;CCCL::libcudacxx;rmm::rmm;rmm::rmm_logger;rmm::rmm_logger_impl;nvidia::cutlass::cutlass;cuco::cuco)


foreach(target IN LISTS rapids_global_targets)
  if(TARGET ${target})
    get_target_property(_is_imported ${target} IMPORTED)
    get_target_property(_already_global ${target} IMPORTED_GLOBAL)
    if(_is_imported AND NOT _already_global)
        set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
    endif()
  endif()
endforeach()

unset(rapids_global_targets)
unset(rapids_clear_cpm_cache)
