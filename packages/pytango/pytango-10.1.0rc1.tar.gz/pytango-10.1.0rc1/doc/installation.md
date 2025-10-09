```{highlight} python
:linenothreshold: 10
```

(installation-guide)=

# Installation

## Minimum setup

To explore PyTango you should have a running Tango system. If you are working in
a facility/institute that uses Tango, this has probably already been prepared
for you. You need to ask your facility/institute Tango contact for the
{envvar}`TANGO_HOST` variable where Tango system is running.

If you are working on an isolated machine you may want to create your own Tango
system (see [How to try Tango](https://tango-controls.readthedocs.io/en/latest/tutorials-and-howtos/how-tos/how-to-try-tango.html)).
This is not a pre-requisite for installing PyTango, but will be useful when you want to start testing.

## Installation of PyTango

First you should try the easy installation way:  pre-compiled packages.
But if that doesn't work, or you need to compile from source, see the next section.

### PyPI (Linux, Windows, MacOS)

You can install the latest version from [PyPI](https://pypi.python.org/pypi/pytango).

PyTango has binary wheels for common platforms, so no compilation or dependencies required.

Install PyTango with pip:

```console
$ python -m pip install pytango
```

If this step downloads a `.tar.gz` file instead of a `.whl` file, then we don't have a binary package
for your platform.  Try Conda.

If you are going to utilize the gevent green mode of PyTango it is recommended to have a recent version of gevent.
You can force gevent installation with the "gevent" keyword:

```console
$ python -m pip install pytango[gevent]
```

### Conda (Linux, Windows, MacOS)

You can install the latest version from [Conda-forge](https://anaconda.org/conda-forge/pytango).

If you don't already have conda, try the [Miniforge3](https://github.com/conda-forge/miniforge#miniforge3)
installer (an alternative installer to [Miniconda](https://docs.conda.io/en/latest/miniconda.html)).

To install PyTango in a new conda environment (you can choose a different version of Python):

```console
$ conda create --channel conda-forge --name pytango-env python=3.11 pytango
$ conda activate pytango-env
```

Other useful packages on conda-forge include:  `tango-test`, `jive` and `tango-database`.

### Linux

PyTango is available on linux as an official debian/ubuntu package (however, this may not be the latest release):

For Python 3:

```console
$ sudo apt-get install python3-tango
```

### Windows

First, make sure [Python](https://www.python.org) is installed.  Then follow the same instructions as for
[PyPI](https://pypi.python.org/pypi/pytango) above.
There are binary wheels for some Windows platforms available.

(build-from-source)=

## Building and installing from source

This is the more complicated option, as you need to have all the correct dependencies and build tools
installed.  It is possible to build in Conda environments on Linux, macOS and Windows.  It is also possible
to build natively on those operating system.  Conda is the recommended option for simplicity.  For details see the file
[BUILD.md](https://gitlab.com/tango-controls/pytango/-/blob/develop/BUILD.md) in the root of the
source repository.

## Basic installation check

To test the installation, import `tango` and check `tango.Release.version`:

```console
$ cd  # move to a folder that doesn't contain the source code, if you built it
$ python -c "import tango; print(tango.Release.version)"
10.0.0
```

Next steps: Check out the {ref}`tutorial`.
