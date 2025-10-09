# Tango CMake Modules

A set of common CMake modules for use in Tango projects.

# Usage

1. Add this repository as a git submodule:

    ```bash
    git submodule add https://gitlab.com/tango-controls/TangoCMakeModules
    ```

2. Use the modules in your CMakeLists.txt:

    ```cmake
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/TangoCMakeModules")

    find_package(Tango REQUIRED)
    ```

3. Add the following to your README.md to remind developers that we are using
   git submodules:

    ```markdown
    ## Keeping Up-to-date

    This repository uses git submodules.

    - Ensure that you use `--recurse-submodules` when cloning:

        `git clone --recurse-submodules ...`

    - If you didn't clone with `--recurse-submodules`, run

        `git submodule update --init`

      to initialise and fetch submodules data.

    - Ensure that updates to git submodules are pulled:

        `git pull --recurse-submodules`
    ```

4. Add the following to `.gitlab-ci.yml` so that the CI knows to clone the
   repository recursively and to generate archives with the submodule included:


    ```yaml
    variables:
        GIT_SUBMODULE_STRATEGY: recursive

    include:
    - project: 'tango-controls/gitlab-ci-templates'
        file: 'ArchiveWithSubmodules.gitlab-ci.yml'
    ```
