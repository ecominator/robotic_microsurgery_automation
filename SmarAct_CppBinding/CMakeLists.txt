cmake_minimum_required(VERSION 3.1)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

project(SmarAct)

include_directories("${CMAKE_SOURCE_DIR}/Cpp/include/headers")
include_directories("${CMAKE_SOURCE_DIR}/Binding")

file(GLOB SOURCE_FILES "Cpp/src/*.cpp")
file(GLOB HEADER_FILES "Cpp/include/headers/*.h")
file(GLOB BINDING_FILES "Binding/*.cpp")

source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${SOURCE_FILES} ${HEADER_FILES} ${BINDING_FILES})

find_package(pybind11 REQUIRED)
pybind11_add_module(SmarAct
	${SOURCE_FILES}
	${HEADER_FILES}
	${BINDING_FILES}
)

# Adding MSCControl.lib as it is required by the link additional dependencies of visual studio
target_link_libraries(SmarAct PUBLIC ${CMAKE_SOURCE_DIR}/Cpp/include/3rdParty/MCSControl.lib)

install(TARGETS SmarAct
  COMPONENT python
  LIBRARY DESTINATION "${PYTHON_LIBRARY_DIR}"
)
