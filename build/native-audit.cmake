# SPDX-License-Identifier: MIT
# A linker map observes actual incorporated archive members, including compiler
# defaults that are invisible in DT_NEEDED. It does not change CUDA/RDC options.
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK
  "${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/link_audit.py")
