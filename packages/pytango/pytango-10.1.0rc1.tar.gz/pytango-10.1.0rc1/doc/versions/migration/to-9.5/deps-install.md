(to9.5-deps-installation)=

# Dependencies and installation

In most cases, your existing PyTango devices and clients will continue to
work as before, however there are important changes.  In the other sections of
the migration guide, you can find the incompatibilities and the necessary migration steps.

## Dependencies

PyTango v9.5.0 requires Python 3.9 or higher.

PyTango v9.5.0 moved from cppTango 9.4.x to at least 9.5.0.  It
will not run with earlier versions.  cppTango's dependencies have also changed,
most notably, omniORB 4.3.x is required, instead of 4.2.x.

### OmniORB 4.3 troubleshooting

If you get an error like:

```
omniORB: (0) 2023-10-23 13:18:11.872312: ORB_init failed: Bad parameter (2097152    # 2 MBytes.)
for ORB configuration option giopMaxMsgSize, reason: Invalid value, expect n >= 8192 or n == 0
```

This is probably because your system has the string `2097152    # 2 MBytes.` in a configuration file, and this
is incorrectly parsed by omniORB 4.3.  For example, if the Linux system package `libomniorb4-2` is installed
then configuration file `/etc/omniORB.cfg` has this problem.

You can edit the file and remove the comment from that line, changing it to `2097152`.  Alternatively, uninstall
the `libomniorb4-2` package if it isn't required on your system.  PyTango's binary Python wheels
include their own copy of omniORB, so they don't require the system package.  Similarly, the conda-forge packages
come with their own copy of omniORB.

## Installation

Similar to the 9.4.x series, the binary wheels on [PyPI](https://pypi.python.org/pypi/pytango) and
[Conda-forge](https://anaconda.org/conda-forge/pytango) make installation very simple on many
platforms.  No need for compilation.  See the [installation guide](#installation-guide).

If you are compiling from source, you may notice that the build system has changed completely.
We now use [scikit-build-core](https://scikit-build-core.readthedocs.io/), and use [CMake](https://cmake.org)
for the compilation on all platforms.  See [building from source](#build-from-source).
