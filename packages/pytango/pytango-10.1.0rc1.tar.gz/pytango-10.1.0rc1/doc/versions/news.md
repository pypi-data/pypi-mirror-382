(pytango-news)=

# What's new?

The sections below will give you the most relevant news from the PyTango releases.
For help moving to a new release, or for the complete list of changes, see the
following links:

```{toctree}
:maxdepth: 1

migration/index
```

## What's new in PyTango 10.1.0rc1?

Date: 2025-10-18

Type: major release

Here we provide highlights of the changes:

(You can find the full changelog in the [history of changes](#pytango-version-history) with the links to related MRs,
where the detailed descriptions of every change/new feature can be found.)

### Changed

- PyTango requires at least [cppTango][cppTangoUrl] 10.1.0. See the [migration guide](#to10.1-deps-install).
- The biggest change in this release is moving the C++ Python bindings from Boost.Python to Pybind11.  There are a
  few **breaking changes**.  See the [migration guide](#to10.1-pybind11).
- When subscribing to events, there are now more options, including **asynchronous** mode.  This new mode can significantly
  speed up subscription to a large number of attributes. See the [migration guide](#to10.1-subscribe-event).
- The string representation of nested structs has been improved so they print a little more nicely.
- References to event subscription callback methods are immediately cleared on unsubscription (instead of sticking
  around for at least a minute).
- Clients ({class}`~tango.DeviceProxy`, {class}`~tango.AttributeProxy`, {class}`~tango.Group`) and servers now release
  the Python GIL in most cases when waiting on cppTango, allowing better concurrency, and avoiding some deadlocks.
  **Note**: The {class}`~tango.Database` client wasn't updated, and still holds the GIL for most calls.
- Better types hints for the extension code (in stub files), and the stub files are now included in the conda-forge
  osx-arm64 packages.
- Many improvements to the documentation, including for {class}`~tango.server.attribute`.
- Support [Coverage.py](https://coverage.readthedocs.io) runs using [`sys.monitoring`](https://peps.python.org/pep-0669/)
  (aka the "sysmon" core).
- Removed limitation of NumPy version < 2.3 at build time.
- For the Python-based DatabaseDS server (developer tool), some of the "default" values in the database have been
  improved to fix a problem with getting device info for the DB device. However, it will only take effect when
  creating a new database from scratch. If you don't want to do that you can also fix them by running
  a command like this:
  - `sqlite3 tango_database.db "UPDATE device SET pid='0' WHERE pid = 'nada';"`

### Added

- Python 3.14 support.
- When defining attributes, you can indicate that they push events in place, removing the need for extra
  calls to `set_change_event`, etc.  See the [migration guide](#to10.1-other-attribute-event-definition).
- Command handler docstrings can now populate the `in_type_desc` and `out_type_desc` fields automatically.
  There is support for ReST, Google, Numpydoc-style and Epydoc docstrings.
  See the [migration guide](#to10.1-other-command-docstrings).
- The client identity is now available in devices when handling command or attribute read/write calls.  However,
  only for synchronous green mode device servers.  See {meth}`tango.server.Device.get_client_ident`. If OpenTelemetry
  is enabled, the client details will be included in relevant spans (for all green modes).
- Non-synchronous green mode clients now keep OpenTelemetry context for all traced calls.
- Two test utility functions: {func}`tango.test_utils.wait_for_proxy` and
  {func}`tango.test_utils.wait_for_nodb_proxy_via_pid`.

### Fixed

- Dynamic commands with no argument (regression in 10.0.0).
- `pre_init_callback` and `post_init_callback` used with a sequence (regression in 10.0.0).
- Type hints with decorated commands - order no longer matters.
- Type hints are parsed when `from __future__ import annotations` is used.
- Crash when exception raised in `delete_device`.
- `AttributeProxy`'s slow initialization (remove unnecessary listing of all commands and attributes).

### Removed

- Support for Python 3.9.
- Support for Tango pipes.
- The `dim_x` and `dim_y` parameters for setting attribute values and pushing events.
  See the [migration guide](#to10.1-pybind11_dimx-dimy-removal). The size is automatically determined from
  the data.

### Packaging

- PyTango packages are compiled with support for OpenTelemetry in Linux and macOS, but not Windows:

| Compilation option  | Linux | Windows | MacOS |
| ------------------- | ----- | ------- | ----- |
| TANGO_USE_TELEMETRY | on    | off     | on    |

- Some of the dependencies packaged with the binary wheels on PyPI have changed. The bundled versions are:

| Dependency             | Linux       | Windows | MacOS      |
| ---------------------- |-------------|---------|------------|
| cpptango               | 10.1.1      | 10.1.1  | 10.1.1     |
| omniorb / omniorb-libs | 4.3.3       | 4.3.0   | 4.3.3      |
| libzmq / zeromq        | 4.3.5       | 4.0.5-2 | 4.3.5      |
| cppzmq                 | 4.11.0      | 4.7.1   | 4.10.0     |
| libjpeg-turbo          | 3.1.2       | 2.0.3   | 3.1.0      |
| abseil                 | 20250814.1  | -       | 20250512.1 |
| protobuf               | v32.1       | -       | v31.1      |
| c-ares                 | v1.34.5     | -       | 1.34.5     |
| re2                    | 2025-08-12  | -       | 2025.08.12 |
| OpenSSL                | 3.6.0       | -       | 3.5.4      |
| curl                   | curl-8_16_0 | -       | 8.14.1     |
| gRPC                   | v1.75.1     | -       | 1.73.1     |
| opentelemetry-cpp      | v1.23.0     | -       | 1.21.0     |

______________________________________________________________________


## What's new in PyTango 10.0.3?

Date: 2025-07-25

Type: patch release

Here we provide short highlights of the changes.
You can find the full changelog in [revisions history](#pytango-version-history).

### Changed

- Silenced pydev debugger warnings about frozen modules at import time.
- NumPy version pinned < 2.3 at build time.  Newer versions can be used at runtime.
- Updated logo for documentation.
- OpenTelemetry SDK log level can be set via an [environment variable](#telemetry-howto-hide-error-messages).

### Fixed

- Fixed regression in {meth}`tango.DeviceProxy.read_attributes_reply` (noticed in Taurus).
- Fixed segfault when client application using OpenTelemetry with OpenSSL exits quickly (under a few seconds).
- Various issues in the Python DatabaseDS implementation.

### Packaging

- PyTango packages are compiled with support for OpenTelemetry in Linux and macOS, but not Windows:

| Compilation option  | Linux | Windows | MacOS |
| ------------------- | ----- | ------- | ----- |
| TANGO_USE_TELEMETRY | on    | off     | on    |

- Some of the dependencies packaged with the binary wheels on PyPI have changed. The bundled versions are:

| Dependency             | Linux       | Windows | MacOS      |
| ---------------------- |-------------|---------|------------|
| cpptango               | 10.0.2      | 10.0.2  | 10.0.2     |
| omniorb / omniorb-libs | 4.3.3       | 4.3.0   | 4.3.3      |
| libzmq / zeromq        | 4.3.5       | 4.0.5-2 | 4.3.5      |
| cppzmq                 | 4.11.0      | 4.7.1   | 4.10.0     |
| libjpeg-turbo          | 3.1.1       | 2.0.3   | 3.1.0      |
| boost                  | 1.87.0      | 1.86.0  | 1.87.0     |
| abseil                 | 20250512.1  | -       | 20250512.1 |
| protobuf               | v31.1       | -       | v31.1      |
| c-ares                 | v1.34.5     | -       | 1.34.5     |
| re2                    | 2025-07-22  | -       | 2025.07.22 |
| OpenSSL                | 3.5.1       | -       | 3.5.1      |
| curl                   | curl-8_15_0 | -       | 8.14.1     |
| gRPC                   | v1.73.1     | -       | 1.73.1     |
| opentelemetry-cpp      | v1.22.0     | -       | 1.21.0     |

______________________________________________________________________

## What's new in PyTango 10.0.2?

Date: 2025-03-07

Type: minor release

**Note:** There was no 10.0.1 release (the number was skipped).

You can find the full changelog in [revisions history](#pytango-version-history) with the links to related MRs,
where the detailed descriptions of every change/new feature can be found.

Here we provide short highlights of the changes:

### Changed

- Documentation updated with a new theme, and changed from reStructuredText syntax to
  [MyST](https://myst-parser.readthedocs.io) markdown.
- Deprecated pipes for clients and servers.  Removal scheduled for v10.1.0.
- Deprecated the old experimental Tango object API which was broken.  Removal scheduled for v11.0.0.

### Added

- Python 3.13 binary wheels on PyPI.
- {meth}`tango.Group.command_inout` and related methods now accept simple data types, like float and int,
  instead of the inconvenient {class}`~tango.DeviceData`.

### Fixed

- Occasional deadlock when a {class}`~tango.Group` object that used events is destroyed.
- {meth}`tango.AttributeProxy.write_asynch` was broken.
- Logging decorators like {class}`~tango.DebugIt` work with `show_kwargs=True`.
- Occasional segfault when an{class}`~tango.AttrConfEventData` object are destroyed.
- Segfault when pytest failure report tries to print device name.
- Various issues in the Python DatabaseDS implementation

### Packaging

- PyTango packages are compiled with support for OpenTelemetry in Linux and macOS, but not Windows:

| Compilation option  | Linux | Windows | MacOS |
| ------------------- | ----- | ------- | ----- |
| TANGO_USE_TELEMETRY | on    | off     | on    |

- Some of the dependencies packaged with the binary wheels on PyPI have changed. The bundled versions are:

| Dependency             | Linux       | Windows | MacOS      |
| ---------------------- |-------------|---------|------------|
| cpptango               | 10.0.2      | 10.0.2  | 10.0.2     |
| omniorb / omniorb-libs | 4.3.2       | 4.3.0   | 4.3.2      |
| libzmq / zeromq        | 4.3.5       | 4.0.5-2 | 4.3.5      |
| cppzmq                 | 4.10.0      | 4.7.1   | 4.10.0     |
| libjpeg-turbo          | 3.0.0       | 2.0.3   | 3.0.0      |
| boost                  | 1.87.0      | 1.86.0  | 1.87.0     |
| abseil                 | 20250127.0  | -       | 20240722.0 |
| protobuf               | v29.3       | -       | v28.3      |
| c-ares                 | v1.34.4     | -       | 1.34.4     |
| re2                    | 2024-07-02  | -       | 2024.07.02 |
| OpenSSL                | 3.4.0       | -       | 3.4.1      |
| curl                   | curl-8_12_0 | -       | 8.12.1     |
| gRPC                   | v1.70.1     | -       | 1.67.1     |
| opentelemetry-cpp      | v1.19.0     | -       | 1.18.0     |

______________________________________________________________________

## What's new in PyTango 10.0.0?

Date: 2024-10-01

Type: major release

An overview of the major new features are available in the [Tango v10 and IDLv6](https://indico.tango-controls.org/event/261/contributions/867/)
presentation materials from the Tango Collaboration meeting.

You can find the full changelog in [revisions history](#pytango-version-history) with the links to related MRs,
where the detailed descriptions of every change/new feature can be found.

Here we provide short highlights of the changes:

### Changed

- PyTango requires at least [cppTango][cppTangoUrl] 10.0.0. See the [migration guide](#to10.0-deps-install).
- High-level {class}`~tango.server.Device` and low-level {class}`~tango.LatestDeviceImpl` classes now use Device_6Impl, with Tango IDLv6 interface
- When using the [Asyncio](server-green-mode-asyncio) green mode, a {class}`DeprecationWarning` will be emitted during the
  {meth}`~tango.server.Device.init_device` call, if any or the methods in {class}`~tango.server.Device` are not
  coroutine functions (i.e., defined with `async def`).
  Note, support of synchronous methods in [Asyncio](server-green-mode-asyncio) servers will be removed in a future release.
  See the [migration guide](#to10.0-asyncio-deprecation).
- The Python GIL is released when adding/removing dynamic attributes calls into cppTango.
- Error messages occurring during device start-up are now redirected to stderr instead of stdout
- PyTango must be complied with the C++17 standard

### Added

- Numpy 2.0 support
- PyTango now supports [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/) for distributed tracing - see the [telemetry how-to guide](#telemetry-howto)
- Support for alarm events
- Extended device information (DevInfo6 implementation, from IDLv6) - see the [version info tutorial](#version-info)
- For [Asyncio](server-green-mode-asyncio) green mode servers, added two coroutine functions to be used when adding and
  removing dynamic attributes.  See the [migration guide](#to10.0-asyncio-dyn-attrs).
- Pydevd debugging (as well as coverage) now is extended to dynamic attributes and commands.
  If necessary, the feature can be disabled by setting the environment variable
  `PYTANGO_DISABLE_DEBUG_TRACE_PATCHING=1`.
- PyTango provides a stub file with typing information for improved autocompletion in your code editor
  (except conda packages for osx-arm64 and linux-aarch64)
- Events can be pushed with Python exception objects directly, no need to convert to {class}`~tango.DevFailed`
- Device description, status, state can be set at the device start-up. See class attributes
  {attr}`~tango.server.Device.DEVICE_CLASS_DESCRIPTION`, {attr}`~tango.server.Device.DEVICE_CLASS_INITIAL_STATUS`,
  and {attr}`~tango.server.Device.DEVICE_CLASS_INITIAL_STATE`.

### Fixed

- Segfault when Restart Command is used on a PyTango server (first reported 6 years ago!)
- Deadlock when pushing event from attribute read method (regression, introduced in 9.5.1)
- Memory leak when writing {class}`~tango.DevString` attribute with {class}`~tango.DeviceProxy` is fixed
- Segfault in `push_archive_event(attr_name)` with attr_name != state or status was fixed
- Various fixes of asyncio {class}`tango.asyncio.DeviceProxy` methods.  High-level reads, and getattr calls
  can (and must) be awaited.
- Fixes of \*\_asynch methods on {class}`~tango.DeviceProxy`.  I.e., when using Tango's asynchronous
  push/pull callback model for accessing attributes and commands.  This is not related to
  Python asyncio methods and coroutine functions.
- {class}`~tango.server.class_property` is now inherited by child device classes
- Various issues in the Python DatabaseDS implementation

### Removed

- Reverted the fix from 9.5.1 for resolving a crash in Asyncio devices when an attribute is read
  at the same time as an event is being pushed (original bug is not fixed).  It was reverted because
  it caused a deadlock in existing code that was pushing events from attribute read methods.
- Following cppTango, event type {class}`~tango.EventType.QUALITY_EVENT` was removed from the {class}`~tango.EventType`
  enum, as well as the `quality_event_subscribed` method from the {class}`~tango.Attribute` class.
  See the [migration guide](#to10.0-quality-event).

### Packaging

- PyTango packages are compiled with support for OpenTelemetry in Linux and macOS, but not Windows:

| Compilation option  | Linux | Windows | MacOS |
| ------------------- | ----- | ------- | ----- |
| TANGO_USE_TELEMETRY | on    | off     | on    |

- Some of the dependencies packaged with the binary wheels on PyPI have changed. The bundled versions are:

| Dependency             | Linux       | Windows | MacOS      |
| ---------------------- | ----------- | ------- | ---------- |
| cpptango               | 10.0.0      | 10.0.0  | 10.0.0     |
| omniorb / omniorb-libs | 4.3.2       | 4.3.0   | 4.3.2      |
| libzmq / zeromq        | 4.3.5       | 4.0.5-2 | 4.3.5      |
| cppzmq                 | 4.10.0      | 4.7.1   | 4.10.0     |
| libjpeg-turbo          | 3.0.0       | 2.0.3   | 3.0.0      |
| boost                  | 1.85.0      | 1.85.0  | 1.85.0     |
| abseil                 | 20240722.0  | -       | 20240722.0 |
| protobuf               | v28.2       | -       | v27.5      |
| c-ares                 | v1.33.1     | -       | 1.33.1     |
| re2                    | 2024-07-02  | -       | 2023.09.01 |
| OpenSSL                | 3.3.2       | -       | 3.3.2      |
| curl                   | curl-8_10_1 | -       | 8.10.1     |
| gRPC                   | v1.66.2     | -       | 1.65.5     |
| opentelemetry-cpp      | v1.16.1     | -       | 1.16.1     |

______________________________________________________________________

## What's new in PyTango 9.5.1?

Date: 2024-03-28 9.5.1

Type: minor release

### Changed

- Restricted NumPy to 1.x, since we do not have NumPy 2.0 support yet.
- Improved some error message related to invalid types passed to {class}`~tango.DeviceProxy`.
- Extended pydevd debugging and coverage to dynamic attributes and commands.

### Fixed

- High-level attribute reads using asyncio DeviceProxies can now be awaited.
- Asyncio green mode devices no longer crash when an attribute is read at the same time as an event is being pushed.
- Numpy 1.20.0 no longer causes an import error.
- High-level Device class inheritance now supports {class}`~tango.server.class_property`.

______________________________________________________________________

## What's new in PyTango 9.5.0?

Date: 2023-11-23

Type: major release

### Changed

- PyTango requires at least [cppTango][cppTangoUrl] 9.5.0. See the [migration guide](#to9.5-deps-installation).
- When using the asyncio green mode, a {class}`~tango.PyTangoUserWarning` will be emitted during the
  {meth}`~tango.server.Device.init_device` call, if the user's {class}`~tango.server.Device` methods are not
  coroutines (i.e., defined with `async def`).
- Use `127.0.0.1` as the default host for (Multi)DeviceTestContext instead of trying to find an external IP.
  This allows tests to work on systems that only have a loopback interface, and also reduces firewall warnings
  when running tests (at least on macOS).  If using it from the command line like,
  `python -m tango.test_context MyDS.MyDevice`, an external IP is still the default.
- All warnings generated by PyTango are now instances of {class}`~tango.PyTangoUserWarning`, which
  inherits from Python's {class}`UserWarning`.
- Some of the dependencies packaged with the binary wheels on PyPI have changed.  The bundled versions are:

| Dependency             | Linux  | Windows | MacOS  |
| ---------------------- | ------ | ------- | ------ |
| cpptango               | 9.5.0  | 9.5.0   | 9.5.0  |
| omniorb / omniorb-libs | 4.3.1  | 4.3.0   | 4.3.1  |
| libzmq / zeromq        | 4.3.5  | 4.0.5-2 | 4.3.5  |
| cppzmq                 | 4.10.0 | 4.7.1   | 4.10.0 |
| libjpeg-turbo          | 3.0.0  | 2.0.3   | 3.0.0  |
| tango-idl              | 5.1.1  | 5.1.2   | 5.1.2  |
| boost                  | 1.82.0 | 1.83.0  | 1.82.0 |

### Added

- Short-name access can be used for (Multi)DeviceTestContext devices.  See [migration guide](#to9.5-short-name-test-access)
- *Experimental feature:*  use Python type hints to declare Device more easily.
  Read more in the new section: {ref}`type-hint`.
- {meth}`~tango.WAttribute.set_write_value` now supports IMAGE attributes.
- Forwarded attributes are *partially* supported in the (Multi)DeviceTestContext.  We say *partially*, because
  a cppTango limitation (at least version 9.5.0) means root attributes on devices running in "nodb" mode
  (like those in launched by the TestContext) don't work. However, it does work if the test device accesses a root
  attribute on a Tango device running with a Tango database.
- Support for {class}`~tango.EncodedAttribute` in high-level API devices.
- Added `free_it` and `clean_db` arguments to {meth}`tango.server.Device.remove_attribute` and
  {meth}`tango.LatestDeviceImpl.remove_attribute` methods.
- Support Tango server debugging with PyCharm, PyDev and VS Code.  Breakpoints now work for command and attribute
  handler methods, as well as other standard {class}`~tango.server.Device` methods, when running through a debugger that
  is based on [pydevd](https://pypi.org/project/pydevd).  However, it doesn't currently work with dynamic attributes
  and commands.  If necessary, the feature can be disabled by setting the environment variable
  `PYTANGO_DISABLE_DEBUG_TRACE_PATCHING=1`.
- Added support for Python 3.12.

### Fixed

- Fixed various issues with {class}`~tango.DeviceProxy` with non-synchronous green mode devices launched with
  {class}`~tango.test_context.DeviceTestContext` and {class}`~tango.test_context.MultiDeviceTestContext`.
  This also fixes support for tests decorated with `@pytest.mark.asyncio`.

### Removed

- Breaking change to the API: the {class}`~tango.CmdArgType.DevInt` data type
  was removed, due to its removal from [cppTango][cppTangoUrl]. See the [migration guide](#to9.5-dev-int).
- Deprecated signature, {meth}`~tango.WAttribute.get_write_value(self, lst)`, was removed.

______________________________________________________________________

## What's new in PyTango 9.4.2?

Date: 2023-07-27

Type: minor release

### Changed

- New python and NumPy [version policy](#pytango-version-policy) is implemented.

### Added

- Correct code coverage of server's methods can be obtained
- server_init_hook was added to high-level and low-level API
- macOS wheels now are provided

### Fixed

- DevEncoded attributes and commands read methods are now segfault safe
- DevEncoded attributes and commands now decoded with utf-8
- DevEncoded attributes and commands can be extracted and written as str, bytes and bytesarray
- If string encoding with Latin-1 fails, UnicodeError will be raised instead of segfaulting
- When user gives empty spectrum properties to the DeviceTestContext,
  they will be patched with one space symbol " " for each element
- In case patching failed or any other problems with FileDatabase, instead of crash PyTango will raise an exception
  and print out generated file
- Regression when applying additional decorators on attribute accessor functions.  Method calls
  would have the wrong signature and fail.

### Removed

- Support for Python \< 3.9. See [version policy](#pytango-version-policy)

______________________________________________________________________

## What's new in PyTango 9.4.1?

Date: 2023-03-15

Type: major release (breaking changes compared to 9.4.0)

### Changed

- Removed additional function signatures for high-level attribute read/write/is_allowed
  methods that were added in 9.4.0 resulting in a regression.  For example, the high-level
  write method API for dynamic attributes of the form `write_method(self, attr, value)`
  has been removed, leaving only `write_method(self, attr)`.  Similarly, unbound functions
  that could be used without a reference to the device object, like `read_function()`, are no
  longer supported - only `read_function(device)`.
  See the [migration guide](#to9.4-non-bound-user-funcs).
- The dependencies packaged with the binary PyPI wheels are as follows:
  : - Linux:
      : - cpptango: 9.4.1
        - omniorb: 4.2.5  (changed since PyTango 9.4.0)
        - libzmq: v4.3.4
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.9
        - tango-idl: 5.1.1
        - boost: 1.80.0 (with patch for Python 3.11 support)
    - Windows:
      : - cpptango: 9.4.1
        - omniorb: 4.2.5
        - libzmq: v4.0.5-2
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.3
        - tango-idl: 5.1.2
        - boost: 1.73.0

### Fixed

- Regression for undecorated read attribute accessor functions in derived device classes.  E.g., if we
  have `class A(Device)` with attribute reading via method `A.read_my_attribute`, then
  reading `my_attribute` from `class B(A)` would fail.  More generally, repeated wrapping
  of methods related to attributes, commands and standard methods (like `init_device`) is now
  avoided.
- Regression when applying additional decorators on attribute accessor functions.  Method calls
  would have the wrong signature and fail.

______________________________________________________________________

## What's new in PyTango 9.4.0?

Date: 2023-02-15

Type: major release

:::{warning}
significant regressions - use newer release!
:::

### Changed

- PyTango requires at least [cppTango][cppTangoUrl] 9.4.1.  See the [migration guide](#to9.4-deps-install).
- Breaking change to the API when using empty spectrum and image attributes.  Clients reading an empty
  attribute will get an empty sequence (list/tuple/numpy array) instead of a {obj}`None` value.  Similarly,
  devices that have an empty sequence written will receive that in the write method instead of a {obj}`None`
  value.  See the migration guide on [empty attributes](#to9.4-empty-attrs) and
  [extract as](#to9.4-extract-as).
- Python dependencies:  [numpy](https://numpy.org) is no longer optional - it is required.
  Other new requirements are [packaging](https://pypi.org/project/packaging) and
  [psutil](https://pypi.org/project/psutil).
- Binary wheels for more platforms, including Linux, are available on [PyPI](https://pypi.python.org/pypi/pytango).  Fast installation without compiling and
  figuring out all the dependencies!
- The dependencies packaged with the binary PyPI wheels are as follows:
  : - Linux:
      : - cpptango: 9.4.1
        - omniorb: 4.2.4
        - libzmq: v4.3.4
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.9
        - tango-idl: 5.1.1
        - boost: 1.80.0 (with patch for Python 3.11 support)
    - Windows:
      : - cpptango: 9.4.1
        - omniorb: 4.2.5
        - libzmq: v4.0.5-2
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.3
        - tango-idl: 5.1.2
        - boost: 1.73.0
- When using the `--port` commandline option without `--host`, the `ORBendpoint` for `gio::tcp` passed
  to cppTango will use `"0.0.0.0"` as the host instead of an empty string.  This is to workaround a
  [regression with cppTango 9.4.1](https://gitlab.com/tango-controls/cppTango/-/issues/1055).
  Note that if the `--ORBendPoint` commandline option is specified directly, it will not be modified.
  This will lead to a crash if an empty host is used, e.g., `--ORBendPoint giop:tcp::1234`.

### Added

- User methods for attribute access (read/write/is allowed), and for commands (execute/is allowed)
  can be plain functions.  They don't need to be methods on the device class anymore.  There was some
  inconsistency with this previously, but now it is the same for static and dynamic attributes,
  and for commands.  Static and dynamic commands can also take an `fisallowed` keyword argument.
  See the [migration guide](#to9.4-non-bound-user-funcs).
- Device methods for reading and writing dynamic attributes can use the high-level API instead of getting
  and setting values inside {class}`~tango.Attr` objects.  See the [migration guide](#to9.4-hl-dynamic).
- High-level API support for accessing and creating DevEnum spectrum and image attributes.
  See the [migration guide](#to9.4-hl-dev-enum).
- Developers can optionally allow Python attributes to be added to a {class}`~tango.DeviceProxy` instance
  by calling {meth}`~tango.DeviceProxy.unfreeze_dynamic_interface`.  The default behaviour is still
  to raise an exception when accessing unknown attributes.
  See the [migration guide](#to9.4-optional-proxy-attrs).
- Attribute decorators have additional methods: {meth}`~tango.server.attribute.getter`,
  {meth}`~tango.server.attribute.read` and {meth}`~tango.server.attribute.is_allowed`.
  See the [migration guide](#to9.4-attr-decorators).
- Python 3.11 support.
- MacOS support.  This is easiest installing from [Conda-forge](https://anaconda.org/conda-forge/pytango).  Compiling locally is not recommended.
  See the [installation guide](#installation-guide).
- Integrated development environment (IDE) autocompletion for methods inherited from
  {class}`tango.server.Device` and {class}`tango.LatestDeviceImpl`.  Attributes from the full class
  hierarchy are now more easily accessible directly in your editor.

### Fixed

- Log stream calls that include literal `%` symbols but no args now work properly without
  raising an exception.  E.g., `self.debug_stream("I want to log a %s symbol")`.
  See the [migration guide](#to9.4-logging-percent-sym).
- Writing a {obj}`numpy.array` to a spectrum attribute of type {obj}`str` no longer crashes.
- Reading an enum attribute with {class}`~tango.AttrQuality.ATTR_INVALID` quality via the high-level API
  now returns {obj}`None` instead of crashing.  This behaviour is consistent with the other data types.

### Removed

- Support for Python 2.7 and Python 3.5.
- The option to install PyTango without [numpy](https://numpy.org).

[cppTangoUrl]: https://gitlab.com/tango-controls/cppTango
