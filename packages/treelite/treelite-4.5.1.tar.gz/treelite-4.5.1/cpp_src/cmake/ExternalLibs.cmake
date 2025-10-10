include(FetchContent)

# RapidJSON (header-only library)
add_library(rapidjson INTERFACE)
target_compile_definitions(rapidjson INTERFACE -DRAPIDJSON_HAS_STDSTRING=1)
find_package(RapidJSON)
if(RapidJSON_FOUND)
  if(DEFINED RAPIDJSON_INCLUDE_DIRS)
    # Compatibility with 1.1.0 stable (circa 2016)
    set(RapidJSON_include_dir "${RAPIDJSON_INCLUDE_DIRS}")
  else()
    # Latest RapidJSON (1.1.0.post*)
    set(RapidJSON_include_dir "${RapidJSON_INCLUDE_DIRS}")
  endif()
  target_include_directories(rapidjson INTERFACE ${RapidJSON_include_dir})
  message(STATUS "Found RapidJSON: ${RapidJSON_include_dir}")
else()
  message(STATUS "Did not find RapidJSON in the system root. Fetching RapidJSON now...")
  FetchContent_Declare(
    RapidJSON
    GIT_REPOSITORY      https://github.com/Tencent/rapidjson
    GIT_TAG             ab1842a2dae061284c0a62dca1cc6d5e7e37e346
  )
  FetchContent_Populate(RapidJSON)
  message(STATUS "RapidJSON was downloaded at ${rapidjson_SOURCE_DIR}.")
  target_include_directories(rapidjson INTERFACE $<BUILD_INTERFACE:${rapidjson_SOURCE_DIR}/include>)
endif()
add_library(RapidJSON::rapidjson ALIAS rapidjson)

# nlohmann/json (header-only library), to parse UBJSON
find_package(nlohmann_json 3.11.3)
if(NOT nlohmann_json_FOUND)
  message(STATUS "Did not find nlohmann/json in the system root. Fetching nlohmann/json now...")
  FetchContent_Declare(
    nlohmann_json
    URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
    URL_HASH SHA256=d6c65aca6b1ed68e7a182f4757257b107ae403032760ed6ef121c9d55e81757d
  )
  FetchContent_MakeAvailable(nlohmann_json)
  message(STATUS "nlohmann/json was downloaded at ${nlohmann_json_SOURCE_DIR}.")
endif()

# mdspan (header-only library)
message(STATUS "Fetching mdspan...")
set(MDSPAN_CXX_STANDARD 17 CACHE STRING "")
FetchContent_Declare(
  mdspan
  GIT_REPOSITORY https://github.com/kokkos/mdspan.git
  GIT_TAG        mdspan-0.6.0
)
FetchContent_GetProperties(mdspan)
if(NOT mdspan_POPULATED)
  FetchContent_Populate(mdspan)
  add_subdirectory(${mdspan_SOURCE_DIR} ${mdspan_BINARY_DIR} EXCLUDE_FROM_ALL)
  message(STATUS "mdspan was downloaded at ${mdspan_SOURCE_DIR}.")
endif()
if(MSVC)  # workaround for MSVC 19.x: https://github.com/kokkos/mdspan/issues/276
  target_compile_options(mdspan INTERFACE "/permissive-")
endif()

# Google C++ tests
if(BUILD_CPP_TEST)
  find_package(GTest 1.14.0)
  if(NOT GTest_FOUND)
    message(STATUS "Did not find Google Test in the system root. Fetching Google Test now...")
    FetchContent_Declare(
      googletest
      URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.tar.gz
    )
    set(gtest_force_shared_crt ${DMLC_FORCE_SHARED_CRT} CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)

    add_library(GTest::gtest ALIAS gtest)
    add_library(GTest::gmock ALIAS gmock)
    target_compile_definitions(gtest PRIVATE ${ENABLE_GNU_EXTENSION_FLAGS})
    target_compile_definitions(gmock PRIVATE ${ENABLE_GNU_EXTENSION_FLAGS})
    foreach(target gtest gmock)
      target_compile_features(${target} PUBLIC cxx_std_14)
      if(MSVC)
        set_target_properties(${target} PROPERTIES
          MSVC_RUNTIME_LIBRARY "${Treelite_MSVC_RUNTIME_LIBRARY}")
      endif()
    endforeach()
    if(IS_DIRECTORY "${googletest_SOURCE_DIR}")
      # Do not install gtest
      set_property(DIRECTORY ${googletest_SOURCE_DIR} PROPERTY EXCLUDE_FROM_ALL YES)
    endif()
  endif()
endif()

# fmtlib
if(BUILD_CPP_TEST)
  find_package(fmt 10.1)
  if(fmt_FOUND)
    get_target_property(fmt_loc fmt::fmt INTERFACE_INCLUDE_DIRECTORIES)
    message(STATUS "Found fmtlib at ${fmt_loc}")
    set(FMTLIB_FROM_SYSTEM_ROOT TRUE)
  else()
    message(STATUS "Did not find fmtlib in the system root. Fetching fmtlib now...")
    set(FMT_INSTALL OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(
        fmtlib
        GIT_REPOSITORY  https://github.com/fmtlib/fmt.git
        GIT_TAG         10.1.1
    )
    FetchContent_MakeAvailable(fmtlib)
    set_target_properties(fmt PROPERTIES EXCLUDE_FROM_ALL TRUE)
    set(FMTLIB_FROM_SYSTEM_ROOT FALSE)
  endif()
endif()
