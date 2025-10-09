#[=======================================================================[.rst:
FindMySQL
---------

Find MySQL library

Imported Targets
^^^^^^^^^^^^^^^^

This module provides the following imported targets, if found:

    ``MySQL::MySQL``
    The MySQL client library
    ``MySQL::exe``
    The MySQL client executable

Result Variables
^^^^^^^^^^^^^^^^

This will define the following variables:

    ``MySQL_FOUND``
    True if the system has the MySQL library.
    ``MySQL_exe_FOUND``
    True if the system has the MySQL library.
    ``MySQL_VERSION``
    The version of the MySQL library which was found, if known

Cache Variables
^^^^^^^^^^^^^^^

The following cache variables may also be set:

    ``MySQL_INCLUDE_DIR``
    The directory containing ``mysql.h``.
    ``MySQL_LIBRARY_RELEASE``
    The path to the release MySQL library.
    ``MySQL_LIBRARY_DEBUG``
    The path to the debug MySQL library.
    ``MySQL_LIBRARY``
    The path to the release MySQL library or the debug library
    if the release library is not found.
    ``MySQL_EXECUTABLE``
    The path to the mysql client program

#]=======================================================================]

if (NOT DEFINED PKG_CONFIG_FOUND)
    find_package(PkgConfig QUIET)
endif()

# Collect hints from pkg-config
if (PKG_CONFIG_FOUND)
    pkg_search_module(_MySQL_PKG mysql mariadb QUIET)
endif()

if (WIN32)
    set(_mysql_inc_paths
        "$ENV{ProgramFiles}/MySQL/*/include"
        "$ENV{ProgramFiles\(x86\)}/MySQL/*/include"
        "$ENV{ProgramFiles}/MariaDB/*/include"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/*/include"
        "$ENV{ProgramFiles}/MariaDB/include"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/include"
        )
endif()

find_path(MySQL_INCLUDE_DIR
    NAMES "mysql.h"
    PATHS
        ${_mysql_inc_paths}
        "${_MySQL_PKG_INCLUDE_DIRS}"
    PATH_SUFFIXES mysql mariadb
    )
unset(_mysql_inc_paths)

if (WIN32)
    set(_mysql_release_names libmariadb libmysql)
    set(_mysql_debug_names  libmariadbd libmysqld)
    set(_mysql_lib_paths
        "$ENV{ProgramFiles}/MySQL/*/lib"
        "$ENV{ProgramFiles\(x86\)}/MySQL/*/lib"
        "$ENV{ProgramFiles}/MariaDB/*/lib"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/*/lib"
        "$ENV{ProgramFiles}/MariaDB/lib"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/lib"
        )
else()
    set(_mysql_release_names  mariadb mysqlclient mysqlclient_r)
    set(_mysql_debug_names  mariadb mysqlclient mysqlclient_r)
endif()

find_library(MySQL_LIBRARY_RELEASE
    NAMES ${_mysql_release_names}
    NAMES_PER_DIR
    PATHS
        ""
        ${_mysql_lib_paths}
        ${_MySQL_PKG_LIBRARY_DIRS}
    )

find_library(MySQL_LIBRARY_DEBUG
    NAMES ${_mysql_debug_names}
    NAMES_PER_DIR
    PATHS
        ""
        ${_mysql_lib_paths}
        ${_MySQL_PKG_LIBRARY_DIRS}
    )

unset(_mysql_lib_paths)
unset(_mysql_release_names)
unset(_mysql_debug_names)

include(SelectLibraryConfigurations)
select_library_configurations(MySQL)

if (WIN32)
    set(_mysql_bin_paths
        "$ENV{ProgramFiles}/MySQL/*/bin"
        "$ENV{ProgramFiles\(x86\)}/MySQL/*/bin"
        "$ENV{ProgramFiles}/MariaDB/*/bin"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/*/bin"
        "$ENV{ProgramFiles}/MariaDB/bin"
        "$ENV{ProgramFiles\(x86\)}/MariaDB/bin"
        )
endif()

find_program(MySQL_EXECUTABLE
    NAMES mariadb mysql
    NAMES_PER_DIR
    PATHS
        ${_mysql_bin_paths}
    )

if (MySQL_EXECUTABLE)
    set(MySQL_exe_FOUND TRUE)
endif()

if (NOT MySQL_INCLUDE_DIR OR
    (CMAKE_CROSSCOMPILING AND NOT CMAKE_CROSSCOMPILING_EMULATOR))
    set(MySQL_VERSION MySQL_VERSION-NOTFOUND)
endif()

if(NOT DEFINED MySQL_VERSION)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/mysql_test_db_client.cpp [===[
#include <mysql.h>
#include <stdio.h>

int main(int argc, char** argv)
{
  printf("%s\n", mysql_get_client_info());

  return 0;
}
]===])

    try_run(
        DB_CLIENT_RUN
        DB_CLIENT_COMPILE
        ${CMAKE_CURRENT_BINARY_DIR}
        ${CMAKE_CURRENT_BINARY_DIR}/mysql_test_db_client.cpp
        COMPILE_DEFINITIONS "-I \"${MySQL_INCLUDE_DIR}\""
        LINK_LIBRARIES "${MySQL_LIBRARY}"
        COMPILE_OUTPUT_VARIABLE DB_CLIENT_COMPILE_OUTPUT
        RUN_OUTPUT_VARIABLE DB_CLIENT_VERSION)

    if (NOT DB_CLIENT_COMPILE)
      message(FATAL_ERROR "Failed to compile simple database client program:\n${DB_CLIENT_COMPILE_OUTPUT}")
    endif()

    if (NOT DB_CLIENT_RUN EQUAL 0)
      message(FATAL_ERROR "Failed to run simple database client program:\n${DB_CLIENT_VERSION}")
    endif()

    string(STRIP "${DB_CLIENT_VERSION}" DB_CLIENT_VERSION)
    set(MySQL_VERSION ${DB_CLIENT_VERSION} CACHE INTERNAL "database client library version")
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(MySQL
    FOUND_VAR MySQL_FOUND
    REQUIRED_VARS
        MySQL_LIBRARY
        MySQL_INCLUDE_DIR
    VERSION_VAR MySQL_VERSION
    HANDLE_COMPONENTS)

if (MySQL_FOUND)
    mark_as_advanced(MySQL_INCLUDE_DIR)
    mark_as_advanced(MySQL_LIBRARY_RELEASE)
    mark_as_advanced(MySQL_LIBRARY_DEBUG)
    mark_as_advanced(MySQL_LIBRARY)
endif()

if (MySQL_FOUND)
    if (NOT TARGET MySQL::MySQL)
        add_library(MySQL::MySQL UNKNOWN IMPORTED)
    endif()
    if (MySQL_LIBRARY_RELEASE)
        set_property(TARGET MySQL::MySQL APPEND PROPERTY
            IMPORTED_CONFIGURATIONS RELEASE
        )
        set_target_properties(MySQL::MySQL PROPERTIES
            IMPORTED_LOCATION_RELEASE "${MySQL_LIBRARY_RELEASE}"
        )
    endif()
    if (MySQL_LIBRARY_DEBUG)
        set_property(TARGET MySQL::MySQL APPEND PROPERTY
            IMPORTED_CONFIGURATIONS DEBUG
        )
        set_target_properties(MySQL::MySQL PROPERTIES
            IMPORTED_LOCATION_DEBUG "${MySQL_LIBRARY_DEBUG}"
        )
    endif()
    set_target_properties(MySQL::MySQL PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${MySQL_INCLUDE_DIR}"
        INTERFACE_DEFINITIONS "${_MySQL_PKG_CFLAGS_OTHER}"
        )
endif()

if (MySQL_exe_FOUND)
    mark_as_advanced(MySQL_EXECUTABLE)
endif()

if (MySQL_exe_FOUND AND NOT TARGET MySQL::exe)
    add_executable(MySQL::exe IMPORTED)
    set_property(TARGET MySQL::exe PROPERTY IMPORTED_LOCATION "${MySQL_EXECUTABLE}")
endif()

