```{eval-rst}
.. currentmodule:: tango
```

(versions-news)=

# News and releases

In this section, we provide news and details about PyTango releases.

```{toctree}
:maxdepth: 2

versions/news
versions/revision
```

(pytango-version-policy)=

## Python and NumPy version policy

Python and NumPy version policy

: Supported versions are determined based on each PyTango release's anticipated release date, as follows:

  1. All minor versions of Python released 42 months prior to that date, and at minimum the two latest minor versions.
  2. All minor versions of NumPy released at that date that meet the requirements in [oldest-supported-numpy](https://pypi.org/project/oldest-supported-numpy/) for the corresponding Python version and platform.

As Python minor versions are released annually, this means that PyTango will drop support for the oldest minor Python version every year, and also gain support for a new minor version every year.

:::{note}
NumPy's [NEP 29](https://numpy.org/neps/nep-0029-deprecation_policy.html) policy requires that dependency versions are only changed on minor or major releases, however, as PyTango does not
follow semantic versioning we allow changing the dependencies on any release, including a patch release.
If PyTango ever changes to semantic versioning, then we can avoid such dependency updates on patch releases.
:::

For example, a 9.4.2 PyTango release would support:

| Python | Platform                                 | NumPy    |
| ------ | ---------------------------------------- | -------- |
| 3.9    | x86_64, win_amd64, win32, aarch64        | >=1.19.3 |
| 3.9    | arm64 (macOS)                            | >=1.21.0 |
| 3.10   | x86_64, win_amd64, win32, aarch64, arm64 | >=1.21.6 |
| 3.11   | x86_64, win_amd64, win32, aarch64, arm64 | >=1.23.2 |

A release after 5 April 2024 would require at least Python 3.10, and support Python 3.12.

The related discussion can be found <https://gitlab.com/tango-controls/pytango/-/issues/527>
