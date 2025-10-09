(to10.1-deps-install)=

# Dependencies and installation

In most cases, your existing PyTango devices and clients will continue to
work as before, however there are important changes. In the other sections of
the migration guide, you can find the incompatibilities and the necessary migration steps.

## Dependencies

PyTango v10.1.0 requires Python 3.10 or higher.

PyTango v10.1.0 moved from cppTango 10.0.x to at least 10.1.0.  It
will not run with earlier versions.

PyTango is compiled with Numpy 2.x , but can work with both 1.x and 2.x versions at runtime.

## Installation

Similar to the 10.0.x series, the binary wheels on [PyPI](https://pypi.python.org/pypi/pytango) and
[Conda-forge](https://anaconda.org/conda-forge/pytango) make installation very simple on many
platforms.  No need for compilation.  See the [installation guide](#installation-guide).
