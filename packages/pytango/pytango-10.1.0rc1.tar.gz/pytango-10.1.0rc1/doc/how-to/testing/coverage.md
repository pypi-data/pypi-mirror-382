```{eval-rst}
.. currentmodule:: tango
```

```{highlight} python
:linenothreshold: 4
```

(test-coverage)=

# Code coverage for Tango devices

## Test coverage

A common tool for measuring code coverage is [Coverage.py](https://coverage.readthedocs.io).  From their docs:

> *Coverage.py is a tool for measuring code coverage of Python programs. It monitors your program, noting which parts of the code have been executed, then analyzes the source to identify code that could have been executed but was not.*

This is a very useful technique improve the quality of source code - both implementation and tests.

## How to run Coverage.py for a PyTango high-level device

The recommended approach is to use [pytest](https://pypi.org/project/pytest), with the [pytest-forked](https://pypi.org/project/pytest-forked) and [pytest-cov](https://pypi.org/project/pytest-cov) plugins.  See the [issues](#testing-approaches-issues) for notes on why the pytest-forked plugin, or subprocesses in general are necessary.  The pytest-cov plugin specifically supports tests run in subprocesses.

For example:

```
pytest --forked --cov --cov-branch tests/my_tests.py
```

Prior to pytest-cov 7.0.0, the above method provided higher (more accurate) coverage reporting than using
Coverage.py directly, like:

```
coverage run --branch -m pytest --forked tests/my_tests.py
```

Since pytest-cov 7.0.0 (which in turn requires Coverage.py >= 7.10.6), the mechanism for handling subprocesses
changed.  Now, Coverage.py's [run-time patching](https://coverage.readthedocs.io/en/latest/config.html#run-patch)
has to be enabled. Add the following patch configuration to  your `pyproject.toml` file:

```toml
[tool.coverage.run]
patch = ["subprocess", "fork", "_exit"]
```

This works well with pytest-cov.  However, if you use Coverage.py directly, then there is an extra step of combining
the various `.coverage*` files that are created before generating a report.

```shell
coverage combine
coverage report
```

:::{note}
If checking coverage using the built-in feature of an IDE like PyCharm, it may start tests with `coverage` first, so the same problems with tests in a forked subprocess apply.
Either enable the run-time patches, or try disabling the forked plugin and running a single test at a time.
:::

## PyTango run-time patching to support Coverage.py

:::{versionadded} 9.4.2
:::

Coverage.py works (see caveat noted below) by using Python's [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function to record the execution of every line of code.
If you are interested, you can read more about [how it works](https://coverage.readthedocs.io/en/stable/howitworks.html).  Unfortunately,
this mechanism doesn't automatically work for the callbacks from the cppTango layer.  E.g., when a command is executed or an attribute is read, the Python method in your Tango device is generally not called in a thread that Python is aware of.  If you were to call `threading.current_thread()` in these callbacks you would see `DummyThread` with a name like `Dummy-2`.  The threads are created by cppTango (using omniORB), not with Python's threading module.

In order to get coverage to work, PyTango does the following:

> 1. Detect if Coverage.py is currently running (when importing `tango/server.py`).
> 2. If a Coverage.py session is active, and the feature isn't disabled (see environment variable below), then patch all the server methods that would get callbacks from the cppTango layer.  This includes `init_device`, `always_executed_hook`, command methods, attribute read/write methods, is allowed methods, etc.
> 3. The patch calls `sys.setrace(threading._trace_hook)` to install the Coverage.py handler before calling your method.  This allows these methods to be analysed for code coverage.

You can opt out of the patching, by setting the `PYTANGO_DISABLE_COVERAGE_TRACE_PATCHING=1` environment variable.  The value it is set to doesn't matter.  The presence of the variable disables the patching.

:::{note}
This patching is not enabled if Coverage.py is using the "sysmon" core
(using [`sys.monitoring`](https://docs.python.org/3/library/sys.monitoring.html)), a newer feature than `sys.settrace`.
This is the default in Coverage.py since 7.9.1, if running on at least Python 3.14.
:::

:::{note}
This patching is only implemented for high-level API devices, in other words, those inheriting from {class}`~tango.server.Device`.  Low-level API devices, inheriting from  {class}`~tango.device_server.LatestDeviceImpl` (or earlier), do not benefit from this patching.
:::
