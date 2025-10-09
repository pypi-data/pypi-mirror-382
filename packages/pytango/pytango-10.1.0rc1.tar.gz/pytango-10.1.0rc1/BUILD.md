# Building pytango

This document is intended for maintainers, developers and distribution/package builders.

A number of practical use-cases for building pytango or parts of it are described here.

## Keeping Up-to-date

This repository uses git submodules.

- Ensure that you use `--recurse-submodules` when cloning:

    `git clone --recurse-submodules ...`

- If you didn't clone with `--recurse-submodules`, run

    `git submodule update --init`

  to initialise and fetch submodules data.

- Ensure that updates to git submodules are pulled:

    `git pull --recurse-submodules`

## Developers platforms

We all have our favorite brand of laptop, desktop, server and distro... Embrace the diversity - it forces us to think outside of our own particular box!

In random order:

### Pixi

Pixi is a package manager and workflow tool built on the foundation of the conda ecosystem.
Its goal is to provide developers with a clean and simple command-line interface to manage their project.
No more long and different instructions per platforms.
Pixi hides the complexity of installing dependencies and allows to run simple tasks whatever the operating system (Linux, Windows and macOS).

Pixi can manage multiple environments.
Environments are created under `.pixi/envs` to keep projects clean and isolated from each other.
It is safe to delete that directory. `pixi` will automatically creates it when needed.

All environments and tasks are defined in the `pixi.toml` file.
When you run a command that uses an environment, pixi will check if the environment is in sync with the `pixi.lock` file.
If it is not, pixi will solve the environment and update it.

You can create/update an environement manually by running `pixi install -e <env name>` but this is usually not required
as any command using an env will create it automatically.
The `pixi info` command will list all defined envs and tasks.

Pytango uses pixi to manage several environments:

- `default`: the default env with the latest python version and all requirements to build and test pytango
- `py3x`: same as default but with a pinned version of Python
- `doc`: env to generate the documentation
- `cpptango`: env to compile cpptango from source

To build and install `pytango` from the source directory:

```shell
git clone --recurse-submodules https://gitlab.com/tango-controls/pytango.git
cd pytango
pixi run install
```

This will automatically create the `default` env with all needed requirements and install pytango in editable mode, with debug symbols, whatever your OS.
Note that on macOS, an extra command is needed to generate the debug symbols: `pixi run generate-debug-symbols`. That will run the `dsymutil` command on `_tango.so`.

To use python 3.11 instead, use `pixi run -e py311 install`.

To build pytango against a specific branch from cpptango, you can run:

```shell
CPPTANGO_BRANCH=<mybranch> pixi run install-cpptango-and-tangotest
pixi run -e cpptango install
```

The first command will clone cpptango under the `.tmpbuild` directory and compile it.
If you don't specify the `CPPTANGO_BRANCH` variable, `main` is used by default.

To build a different version of cpptango, you should delete manually the `.tmpbuild` directory
or run `pixi run clean-cpptango-and-tangotest`.

`TangoTest` needs to be installed in the same environment as `pytango` because some tests load the TangoTest library.
As a conda package isn't available for cpptango source builds, `TangoTest` will also be built from source.
Like for cpptango, you can override the version defined in the `pixi.toml` by setting the `TANGO_TEST_VERSION` variable.

You can uninstall pytango with `pixi run uninstall`.
`pixi run clean` will also delete the `build` directory for the current environment.
And `pixi run clean-all` will delete all directories (`build`, `.tmpdir` and `dist`).

If you want to run some commands in an env without typing `pixi run`, you can use `pixi shell` (with `-e` to specify a specific env). It will open a shell with the environment activated.

To create reproducible environments, pixi uses a [lock file](https://pixi.sh/latest/features/lockfile/) (named `pixi.lock`).
It descibes the packages of the defined environments for all platforms.
This is how pixi can ensure that an installed environment is aligned with the project configuration. That file shouldn't be modified manually.
If you change any dependency in `pixi.toml`, pixi will update the lock file automatically when running any command as `pixi install`, `pixi run`, `pixi shell`, `pixi list`...

From time to time, to update dependencies that aren't pinned to the latest available version,
we can force pixi to re-generate the full file by deleting it:

```shell
rm pixi.lock
pixi run install
git commit -a -m "update pixi.lock"
```

### Conda

Conda can be used to install the build requirements on all platforms (Linux, MacOS or Windows).
The following assumes you are familiar with conda and it's already configured to use the `conda-forge` channel.

On macOS, you need to have the Xcode Command Line Tools installed.
To compile on Windows you first need to install the Build Tools for Visual Studio 2019 (or a more recent version).

The minumum requirements for all platforms are: `cmake cxx-compiler cpptango cppzmq python=3.11 pybind11>=3.0.1`.
On Linux and macOS, you also need `pkg-config` and can add `ninja` or `make`. With `ninja` you get *much* faster
compilation, since it uses multiple CPU cores to do the work in parallel.

Create the conda environment that will be used to compile and install `pytango`.

On Windows:

```shell
conda create -y -n pytango cmake cxx-compiler cpptango cppzmq python=3.11 pybind11>=3.0.1
```

On Linux and macOS:

```shell
conda create -y -n pytango make cmake cxx-compiler pkg-config ninja cpptango cppzmq python=3.11 pybind11>=3.0.1
```

You can also install at the same time the runtime, telemetry and test requirements with conda (they will be installed via pip otherwise):

```shell
conda create -y -n pytango make cmake cxx-compiler pkg-config ninja cpptango cppzmq python=3.11 pybind11>=3.0.1 gevent numpy packaging psutil typing_extensions pytest pytest-forked pytest-cov pytest-asyncio tango-test opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http docstring_parser
```

To build and install `pytango` from the source directory:

```shell
conda activate pytango
git clone --recurse-submodules https://gitlab.com/tango-controls/pytango.git
cd pytango
pip install .
```

To install in editable mode, you should use `--no-build-isolation`, meaning that you have to install the build requirements manually (`scikit-build-core`, `numpy`, `pybind11-stubgen`, `ruff`),
and using a fixed build directory speeds up recompilation if the extension code is changed:

```shell
conda activate pytango
conda install scikit-build-core numpy pybind11-stubgen ruff
git clone --recurse-submodules https://gitlab.com/tango-controls/pytango.git
cd pytango
pip install --no-build-isolation --config-settings=build-dir="build/{wheel_tag}" -e ".[tests]"
```

### macOS

I recommend switching from the default 'zsh' Terminal to using 'bash' by default. It is perhaps not strictly necessary as zsh is mostly backwards compatible - but it does occasionally cause some hard-to understand issues.

These instructions should work for both Intel (x86_64) and Apple (arm64) Silicon. Tested primarily on Monterey (M1).

Install [Homebrew](https://brew.sh/) if you do not already have it! You practically can't develop software on a Mac without it (and if you can then you're amazing and don't need these instructions)

The order here doesn't really matter. But first some tooling:

```shell
brew install coreutils cppcheck git lcov pkg-config python@3.11
```

Then some Tango/PyTango library dependencies:

```shell
brew install pybind11>=3.0.1 cppzmq jpeg-turbo omniorb zeromq
```

### Linux

Sorry, we don't provide instructions to build natively from source on Linux.
Using Pixi or Conda on Linux is so much easier.

You could try working from our old Ubuntu-based
[`Dockerfile`](https://gitlab.com/tango-controls/pytango/-/blob/v9.5.1/.devcontainer/Dockerfile?ref_type=tags),
from version 9.5.1.

Alternatively, the various Docker images used for [cppTango's CI](https://gitlab.com/tango-controls/docker/ci/cpptango)
may be useful.

### Windows

Other than python (which can be obtained from the Windows Store), the
dependency you need is cppTango.

- cppTango:
  - The easiest way to get cppTango is as part of the Windows Tango Source
    Distribution.  A Windows installer is available from
    [here](https://gitlab.com/tango-controls/TangoSourceDistribution/-/releases).
  - If you just want cppTango binaries you can download a zip archive from [here](https://gitlab.com/tango-controls/cppTango/-/releases)
    (if in doubt you want the `shared_release` version).  Once you have
    extracted the archive set the `TANGO_ROOT` environment variable, e.g. with
    `$env:TANGO_ROOT=<path\to\extracted\cppTango>` in powershell.

## New build system: how to build the wheel

Pytango can be built into a distribution package using the build system provided. The build system is based
on a few development tools, mainly:

* cmake - for building the c++ code and pulling in dependency configurations
* python build - the (new) standard build interface in python world
* scikit-build-core - provides glue to seamlessly invoke cmake builds from a python build
* pybind11 - used for the Python extension code

Assuming the library dependencies are already installed on your host (see [above](#pytango-library-dependencies)), you should create a python virtualenv for the build. This virtualenv can be very small because scikit-build-core actually creates its own virtualenv in the background (in /tmp) where the pytango build requirements are pulled in.

The following is a quick summary of how to build and check the pytango wheel. Assuming workstation environment is appropriately configred with pre-installed dependencies.

In brief, the steps are essentially:

1. Clone the pytango repo
2. Setup a virtual environment
3. Build the wheel using build and scikit-build-core
4. Generate the wheel with batteries (i.e. pull dependency libraries into a wheel)
5. Install the wheel
6. Test the wheel

Steps 1-3:  configure your environment and build the basic wheel (using scikit-build-core and cmake under the hood)

```shell
git clone --recurse-submodules git@gitlab.com:tango-controls/pytango.git
cd pytango
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip build
# Setting the Tango_ROOT variable is only required for a non-standard system install of cppTango
Tango_ROOT=/path/to/installed/tango.9.4 python3 -m build
# Check what has been built:
ls dist/
# Further check what is in the wheel if you're really curious:
unzip dist/*.whl
```

Step 4: pull the dependency libraries into a (new) wheel. This step is platform-dependent.
On Linux:

```shell
# on Linux only
pip install auditwheel
# LD_LIBRARY_PATH only required if Tango is installed in a non-standard location
LD_LIBRARY_PATH=/path/to/installed/tango.9.4/lib/ auditwheel repair dist/pytango*.whl
ls wheelhouse/
```

On MacOS:

```shell
# on MacOS only
pip install delocate
# DYLD_LIBRARY_PATH only required if Tango is installed in a non-standard location
$ DYLD_LIBRARY_PATH=/path/to/installed/tango.9.4/lib/ delocate-wheel -w wheelhouse/ -v dist/pytango*.whl
ls wheelhouse/
```

On Windows:

```powershell
# on Windows only (powershell)
pip install delvewheel
# --add-path only required if the DLLS are not already on in your $env:PATH
delvewheel repair $(Get-ChildItem -Path dist -Filter pytango*.whl | Select -Expand FullName) --add-path=C:\path\to\tango\dlls
ls wheelhouse\
```

Step 5-6: Installing and checking the wheel package.

```shell
# install the wheel with batteries
python -m pip install --prefer-binary wheelhouse/pytango*.whl
# Tests need to run somewhere not in the root of the pytango repo since the source code is located in a folder named `tango` and conflicts with the module name.
mkdir tmp && cd tmp/
python -c "import tango; print(tango.utils.info())"
```

## Advanced Build Configuration

The following information is intended for maintainers of pytango that may need to dive deeper into the depths of the build system.

### cmake configuration options

cmake can be used with all of its standard configuration options for different types of builds, etc.

Specific to this project, the following cmake cache variables can be used to hint at where to find dependencies, these can also defined and read from the environment although the cache (i.e. cmake `-D` option) will take precedence):

* **Tango_ROOT** - Set this to the path where cppTango is installed IF not in a system path.
* **PYTHON_ROOT** - Use this if you have multiple python installations. Set to the root path where the particular version of python is installed.

Other environment variables can also be used to control aspects of the build:

* **CMAKE_ARGS** - use this to set flags/options that are used by scikit-build-core when invoking cmake.
* **CMAKE_GENERATOR** - for example chose between "Unix Makefiles" (default) and "Ninja".

### Building with debug symbols

In order to get debug symbols, we need to set the build type to `Debug` via scikit-build-core
configuration option for `cmake.build-type`.  We also disable build isolation, and use a static build directory,
so that recompilation is quick, and so that the .o files are available for creating the debug symbols
on macOS.  We also do an editable install which is useful for developement, and add the `-v` option to `pip` so
that we can see details of the compilation.  Verify that the `-g` option is passed to the compiler - without it
there won't be any debug symbols.

```shell
pip install --no-build-isolation --config-settings=cmake.build-type="Debug" --config-settings=build-dir="build/{wheel_tag}_{build_type}" -v -e ".[tests]"
```

On macOS, an extra step is required to generate debug symbols.  Run this command, with the correct path to your newly compiled
`_tango.so` file:

```shell
dsyumtil /path/to/python/site-packages/tango/_tango.so
```

### The cmake presets

The `CMakePresets.json` file contains a number of preset configurations so that developers and maintainers do not have to remember or otherwise document which compiler flags are needed to build pytango. A preset definition can be passed to cmake with the `--preset=<PRESET_NAME>` but because cmake is called by scikit-build when building the python module, the argument need to be passed like this:

```shell
CMAKE_ARGS="--preset=ci-Linux" python3 -m build
```

Note that some of the preset targets (like `ci-Linux`) requires some additional software packages like `clang-tidy` and `cppcheck` as they are intended for maintainers to inspect the code quality.

We also offer presets for third party developers doing packaging. Right now we have configure presets
`third-party-packaging-Linux` and `third-party-packaging-MacOSX` available.

### Custom developers presets

User-defined presets can be stored in [CMakeUserPresets.json](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html). This is a file that a developer can use to setup their local development environment and configuration options. This will inevitably be workstation-dependent and must **not** be committed to source control.

A recommended example to get started with (replace the `Tango_ROOT` entry):

```json
{
  "version": 2,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 18,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "dev-common",
      "hidden": true,
      "inherits": ["dev-mode", "clang-tidy", "cppcheck"]
    },
    {
      "name": "dev-unix",
      "binaryDir": "${sourceDir}/cmakebuild/dev-unix",
      "inherits": ["dev-common", "ci-unix"],
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "dev",
      "binaryDir": "${sourceDir}/cmakebuild/dev",
      "inherits": "dev-unix",
      "cacheVariables": {
        "Tango_ROOT": "/path/to/installed/tango.9.4"   # Replace this path for your local installation
      }
    }
  ],
  "buildPresets": [
    {
      "name": "dev",
      "configurePreset": "dev",
      "configuration": "Debug",
      "jobs": 8
    }
  ]
}
```

Then you can simply use your own `dev` preset to build pytango, for example as an editable install for development:

```shell
CMAKE_ARGS="--preset=dev" python -m pip install -e ".[tests]"
```

**PLEASE NOTE** that you cannot reference presets from your own `CMakeUserPresets.json` when building a wheel with `python -m build` as this file is not packaged with the PyTango source distribution and thus not available in the temporary virtualenv that scikit-build-core creates. User presets can **only** be used in a local development environment.

## Building the CPP source code

Please note that the instructions in this section are for developers/maintainers of the C++
extension code. Python developers/users/packagers do **not** need to invoke cmake directly
in order to build pytango. See the next section for python build instructions.

The `ext/` dir contains the source code for the pytango bindings to the cppTango C++ library.
These python bindings are generated using pybind11 and built using cmake.

### PyTango library dependencies

The C++ code has dependencies on:

* Tango (cppTango) & its dependencies...
* Python
* pybind11
* NumPy

### PyTango Build System Dependencies

In addition, the build system requires a development environment with the following tools:

* cmake (>=3.18 - the newer the better)
* python (>= 3.10 - the newer the better)
* clang-format
* clang-tidy
* ninja
* pkg-config

(the latter 4 are not *strictly* required but the build system for developers and maintainers is configured by default to expect these so that we can easily monitor code quality)

### Example build

The following example shows how to build _just_ the C++ code into a shared object called `_pytango.so`.
The example uses a python virtualenv in order to pull together an up-to-date build environment which developers are encouraged to use.

Pre-amble: setup the environment.
First check that you have a recent cmake (>= 3.16) installed:

```shell
user@computer home $ cd pytango
user@computer pytango $ cmake --version
cmake version 3.25.1

CMake suite maintained and supported by Kitware (kitware.com/cmake).
```

If you don't have cmake already then you can install it in a python virtualenv (see below). NOTE: only `pip install cmake`
If you don't have cmake in your environment. Otherwise, they can conflict and cause difficult-to-track errors.

We create a python virtualenv in order to conveniently pull in some recent versions of useful developer tools:

```shell
cd pytango/   # if you're not already here...
user@computer pytango $ python3.11 -m venv venv
user@computer pytango $ source venv/bin/activate
pip install clang-tidy clang-format numpy
pip list
Package      Version
------------ --------
clang-format 15.0.7
clang-tidy   15.0.2.1
ninja        1.11.1
numpy        1.24.1
pip          22.3.1
setuptools   65.6.3

pip install cmake   # ONLY IF CMAKE IS NOT ALREADY AVAILABLE
```

If you **do** have the `CMakeUserPresets.json` file in the root of the project, then configure, build the `_pytango.so` library in "Debug" mode in the `cmakebuild/dev/` directory and (optionally) install it:

```shell
mkdir install  # optional: if you want to test installed lib locally

cmake --preset=dev -DCMAKE_INSTALL_PREFIX=$(pwd)/install  # configuring - the install prefix is optional
cmake --build --preset=dev   # building
cmake --build --preset=dev --target install  # optionally install the library

ls install/pytango/
_pytango.9.4.0.so _pytango.9.so     _pytango.so

```

If you do **not** have the `CMakeUserPresets.json` in the root of the project (i.e. if you're in a hurry or on a CI platform) then configure, build and install is a little more manual but you can fall back on the available `ci-<platform>` presets where `<platform>` can be one of the following:

* ci-macOS
* ci-Linux
* ci-Windows

Assuming that you do have the virtualenv defined as above (or all tools _somehow_ available), you can build a CI configuration which will build `_pytango.so` in "Release" mode in the `cmakebuild/` directory:

```shell
cmake --preset=ci-macOS -DTango_ROOT=/path/to/installed/tango.9.4
cmake --build --preset=dev

```

## Building with bleeding-edge dependencies from source code (IDL, cppTango, TangoTest, omniORB)

Please note that the instructions in this section are for developers/maintainers of the C++
extension code.  This is for PyTango developers/maintainers that want to test against a specific
version of cppTango.  E.g., testing against an unreleased version.  In that case there may not be
a conda-forge package available for your platform of choice.

### Create conda environment

In the conda environments below, we include the channel `conda-forge/label/tango-idl_dev`, so that
we can use the latest version Tango IDL (it may be an alpha version, before a final release is made).

#### Linux / macOS (Intel):
Include omniorb, as the conda package has omniidl
```shell
conda create -n pytango-dev-src -c conda-forge/label/tango-idl_dev cmake make cxx-compiler libtool pkg-config gnuconfig autoconf omniorb cppzmq zeromq tango-idl jpeg pybind11 numpy ninja python=3.12 scikit-build-core pybind11-stubgen ruff gevent packaging psutil typing_extensions pytest pytest-forked pytest-cov pytest-asyncio docstring_parser
conda activate pytango-dev-src
```

#### macOS (Apple Silicon):

Exclude omniorb, as omniidl isn't included in osx-arm64 package. We need to build from source
```shell
conda create -n pytango-dev-src -c conda-forge/label/tango-idl_dev cmake make cxx-compiler libtool pkg-config gnuconfig autoconf cppzmq zeromq tango-idl jpeg pybind11 numpy ninja python=3.12 scikit-build-core pybind11-stubgen ruff gevent packaging psutil typing_extensions pytest pytest-forked pytest-cov pytest-asyncio docstring_parser
conda activate pytango-dev-src
```

Build and install ominORB from source, if not available from conda-forge:
```shell
# (in pytango-dev-src env)
cd /path/to/your/src
mkdir omniORB
cd omniORB
download omniORB-4.3.1.tar.bz2 from https://sourceforge.net/projects/omniorb/files/omniORB/omniORB-4.3.1/
tar jxvf omniORB-4.3.1.tar.bz2
cd omniORB-4.3.1
cp $CONDA_PREFIX/share/gnuconfig/config.* ./bin/scripts
mkdir build
cd build
# on Apple Silicon, disable long double
../configure --prefix="$CONDA_PREFIX" --disable-longdouble
make -j$CPU_COUNT
make install
```

### Build and install cppTango

For a debug build, you can use `-DCMAKE_BUILD_TYPE=Debug`.  On non-Windows platforms you can modify
the cppTango `configure/CMakeLists.txt` file completely disable optimisation, and add more debug info.
Find the `add_compile_options` line with `-Og -g`.  That part can be changed to `-O0 -g3`

For a release build, you can use `-DCMAKE_BUILD_TYPE=Release`.

```shell
# (in pytango-dev-src env)
cd /path/to/your/src
git clone --recurse-submodules git@gitlab.com:tango-controls/cppTango.git
cd cpptango
mkdir build
cd build
cmake ${CMAKE_ARGS} \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_VERBOSE_MAKEFILE=ON \
      -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" \
      -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
      -DBUILD_TESTING=OFF \
      -DCMAKE_CXX_STANDARD=17 \
      -DTANGO_USE_TELEMETRY=ON \
      ..
make -j$CPU_COUNT
make install
```

If you get the error `Could not find a usable omniidl`, then you should build and install omniORB from source,
using the instructions above.

### Build and install TangoTest

If you want to run the PyTango unit tests, you will need a version of TangoTest on the path.  One way is
to build it from source, using the same cppTango library compiled and installed in the previous step.

```shell
# (in pytango-dev-src env)
cd /path/to/your/src
git clone --recurse-submodules https://gitlab.com/tango-controls/TangoTest.git
cd TangoTest
mkdir build
cd build
cmake --install-prefix="$CONDA_PREFIX" ..
make -j$CPU_COUNT
make install
```

### Build and install PyTango

Follow the steps from earlier in this document.  E.g.,

```shell
# (in pytango-dev-src env)
cd pytango
pip install --no-build-isolation --config-settings=build-dir="build/{wheel_tag}" -e ".[tests]" -v
```

### Getting C++ coverage data locally

```shell
# create venv and install dependencies
pip install --no-build-isolation                                        \
            --config-settings=cmake.args="-DPYTANGO_ENABLE_COVERAGE=ON" \
            --config-settings=cmake.build-type="Debug"                  \
            --config-settings=build-dir="cmakebuild"                    \
            -v  -e ".[tests]"
pytest --cov . --cov-branch --write_cpp_coverage tests
gcovr --gcov-ignore-parse-errors=negative_hits.warn_once_per_file \
      --txt                                                       \
      --decisions                                                 \
      --exclude-throw-branches                                    \
      --exclude-unreachable-branches                              \
      --html-details htmlcov/
```

The C++ coverage data can then be inspected on the terminal or at `htmlcov/coverage_details.html`.
