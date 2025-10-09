(to10.1-pybind11)=

# Migration from Boost.Python to Pybind11

PyTango 10.1 was moved from [Boost.Python](https://www.boost.org/doc/libs/release/libs/python/doc/html/index.html) to [PyBind11](https://pybind11.readthedocs.io) for the C++ extension layer. The vast majority of code using PyTango will work as before, however these are some API changes, which are described here.

(to10.1-pybind11_rationale)=

## Rationale
First of all, why did we do it? Boost.Python was the first successful library which offered the possibility to bind two almost completely opposite languages in one project: dynamically-typed, interpreted with fully hidden from user memory management Python, and strictly typed, compiled, with direct memory control C++. However, even though Boost.Python is still around, there are several successors, which took the best from Boost.Python, but made it easier, better and more modern. In PyTango, we decided to move our project to pybind11, the **de facto standard** for C++/Python bindings, and there were several reasons:

### 1. Simplicity & Cleaner Code
Pybind11 provides a modern, intuitive API for binding C++ to Python with minimal boilerplate code. Unlike Boost.Python, which requires extensive macro usage and setup, Pybind11 enables developers to write clean and maintainable code. We also used the opportunity simplify, remove duplication and improve the code layout.

### 2. Header-Only Library (No Linking Hassles) with Reduced Dependencies
Pybind11 is a **header-only** library, meaning it does not require additional linking steps. Using Boost.Python means bringing in the entire Boost library, which is large and mostly unused. It was especially complicated to build for Windows.

### 3. Better C++11/14/17/20 Support
Pybind11 is designed with **modern C++ standards in mind**, making it easier to work with **smart pointers, lambdas, move semantics, and other advanced C++ features**.

### 4. Better Python Version Compatibility
Boost.Python often lags in supporting **newer Python versions** and core dependencies, leading to maintenance challenges. E.g., the official Boost release to support NumPy 2.0 was about 6 months late. We also had to re-build the library for each new version of Python, on each supported platform.

### 5. Better Documentation
To be honest, PyBind11 documentation cannot be really called perfect, but compared to Boost.Python it is **much** better.

### 6. Easier Debugging & Maintenance
Pybind11 is easier to debug compared to Boost.Python. Just look to the typical frame stack of Boost function call vs. PyBind11.

### 7. Bonus
As a result of some rigorous testing, a number of old bugs were discovered and fixed. We also improved our test coverage along the way.

(to10.1-pybind11_api)=

# API changes

And now what changed from PyTango user side:

## Version constant

Obviously, `BOOST_VERSION` constant and `Compile` class member was replaced with `PYBIND11_VERSION`

(to10.1-pybind11_pipes)=

## Pipes removed

The pipes bindings were not re-written, since pipes in general are scheduled to be removed from Tango, and we decided not to spend time to their adaptation.
Due to this, the following methods/classes were removed:

1. `tango.pipe` module with `PipeConfig` class.
2. `tango.pipe_data` module with `PipeData` class.
3. `Pipe`, `PipeEventData`, `PipeWriteType`, `PipeInfoList`, `PipeInfo`, `DevicePipe`, `UserDefaultPipeProp`, `CmdArgType.DevPipeBlob`, `EventType.PIPE_EVENT` classes.
4. `DeviceClass`: `pipe_list` member, and `get_pipe_list`, `get_pipe_by_name` methods.
5. `DeviceImpl`: `push_pipe_event` method.
5  high-level API `Device`: `pipe` class from `tango.server` used to define pipe as class member or by method decorator.
6. `DeviceProxy`: high-level DeviceProxy does not list pipes as class members, high-level write and read to/from pipes is not possible.
7. `DeviceProxy`: `get_pipe_config`, `set_pipe_config`, `read_pipe`, `write_pipe`, `get_pipe_list` methods.

(to10.1-pybind11_enums)=

## Enums

Pybind11 has a different mechanism to export enums (pybind11 creates enums that are native Python's enums,
while Boost does something very different by creating a singleton).  PyTango wraps the cppTango enums as
enums derived from Python {class}`~enum.IntEnum`.

The `__repr__()` of Enums has changed: with Boost if you did `repr(DevState.ON)` you got `"tango._tango.DevState.ON"`,
while now you will get `"<DevState.ON: 0>"`.
So if you do string analysis of Enum representation in you code, please adapt it. The `__str__()` method for
Enums has not changed: `str(DevState.ON)` is still `"ON"`.

## Type coercion for commands with boolean return type

A command that returns a boolean, `dtype_out=bool`, will no longer convert a `None` value into `False`. The caller
will get a {class}`~tango.DevFailed` exception. Either return a value of the correct type, or change the return type
to `None` (i.e., `DevVoid`).

```python
from tango.server import Device, command


class MyDevice(Device):

    @command(dtype_out=bool)
    def bad_boolean_return_command(self):
        pass  # don't do this and don't return None

    @command(dtype_out=bool)
    def good_boolean_return_command(self):
        return False

    @command()
    def good_void_command(self):
        pass

    @command(dtype_out=None)
    def another_good_void_command(self):
        pass
```

(to10.1-pybind11_dimx-dimy-removal)=

## Attribute and WAttribute: dim_x and dim_y

The {meth}`tango.Attribute.set_value`, {meth}`tango.Attribute.set_value_date_quality`, and
{meth}`tango.WAttribute.set_write_value` methods no longer support `dim_x` and `dim_y` parameters (long deprecated).

## Pushing events: dim_x and dim_y

The various methods for pushing events no longer support the `dim_x` and `dim_y` arguments. The dimensions are
determined automatically from the data. Methods affected:

| {class}`tango.server.Device`                    | {class}`tango.LatestDeviceImpl`                    |
|-------------------------------------------------|----------------------------------------------------|
| {meth}`~tango.server.Device.push_alarm_event`   | {meth}`~tango.LatestDeviceImpl.push_alarm_event`   |
| {meth}`~tango.server.Device.push_archive_event` | {meth}`~tango.LatestDeviceImpl.push_archive_event` |
| {meth}`~tango.server.Device.push_change_event`  | {meth}`~tango.LatestDeviceImpl.push_change_event`  |
| {meth}`~tango.server.Device.push_event`         | {meth}`~tango.LatestDeviceImpl.push_event`         |

## Keyword args for set_change_event, etc.

The various methods for declaring that a device pushes its own events, e.g., `set_change_event`, can now
be used with keyword arguments. This can make code more readable. Usage is optional.

```python
from tango.server import Device

class MyDevice(Device):
    def init_device(self):
        # instead of:
        self.set_change_event("State", True, False)
        # rather use:
        self.set_change_event("State", implemented=True, detect=False)
```

This kind of change applies to:

| {class}`tango.server.Device`                      | {class}`tango.LatestDeviceImpl`                      |
|---------------------------------------------------|------------------------------------------------------|
| {meth}`~tango.server.Device.set_alarm_event`      | {meth}`~tango.LatestDeviceImpl.set_alarm_event`      |
| {meth}`~tango.server.Device.set_archive_event`    | {meth}`~tango.LatestDeviceImpl.set_archive_event`    |
| {meth}`~tango.server.Device.set_change_event`     | {meth}`~tango.LatestDeviceImpl.set_change_event`     |
| {meth}`~tango.server.Device.set_data_ready_event` | {meth}`~tango.LatestDeviceImpl.set_data_ready_event` |


| {class}`tango.Attribute`                   | {class}`tango.Attr`                   |
|--------------------------------------------|---------------------------------------|
| {meth}`~tango.Attribute.set_alarm_event`   | {meth}`~tango.Attr.set_alarm_event`   |
| {meth}`~tango.Attribute.set_archive_event` | {meth}`~tango.Attr.set_archive_event` |
| {meth}`~tango.Attribute.set_change_event`  | {meth}`~tango.Attr.set_change_event`  |

## Asynch attribute read/command inout

The callback result from {meth}`~tango.DeviceProxy.command_inout_asynch` is still a {class}`~tango.CmdDoneEvent` object.
However, the `argout` field behaves differently in case the command failed (exception on server side, or
timeout on client side). Accessing `argout` will now raise a {class}`~tango.DevFailed` exception, instead
of returning `None`. Check the `err` field before trying to access `argout`.

```python
if not result.err:
    print(result.argout)
```

The callback result from {meth}`~tango.DeviceProxy.read_attribute_asynch` and {meth}`~tango.DeviceProxy.read_attributes_asynch`
is still a {class}`~tango.AttrReadEvent` object. However, if there was a timeout on the client side, the
`argout` field is an empty list, `[]`, instead of `None`, for consistency with a successful read.
The `err` field is unchanged, and will be `True` in case of a timeout.

## Std vectors

1. Vectors such as `StdStringVector`, `StdLongVector`, `StdDoubleVector` are now implicitly
convertible to Python lists, so there is no need to convert methods arguments to them.
Similarly, methods return values changed to Python `list[str]`, `list[int]` and `list[float]`, respectively

2. `StdGroupAttrReplyVector`, `StdGroupCmdReplyVector`, `StdGroupReplyVector` aren't exported any more (due to bad implementation on cpptango side).
Instead, user receives `list[GroupAttrReply]`, `list[GroupCmdReply]`, `list[GroupReply]`, respectively

3. `AttrList` and `AttributeList` were removed. They do not have analogues in cppTango and were pure PyTango structures.
Instead, user receives `tuple[Attr]`, `tuple[Attribute]`, respectively. Note that these structures do not have python-to-cpp convertors, as it is not possible to implement correctly.

## Docstring

Due to implementation details, almost all **docstrings** for classes, methods and enums in pybind11 **aren't mutable**,
so if you need to change it in your code - now you must create your own class, method, enum inheriting/calling parent
method and put your docstring there

## Attribute configuration structs interface frozen

Many structs related to attributes and attribute configuration used generate a `PytangoUserWarning` if you
assigned to a field that didn't exist in the structure.

E.g., `tango.ChangeEventProp().invalid_field = "123"` would generate a warning.

Now, the interfaces of these structs are frozen, so attempting to write to a non-existent field will raise an
`AttributeError`.

The list of affected structs is:

- {class}`~tango.ArchiveEventProp`
- {class}`~tango.AttributeAlarm`
- {class}`~tango.AttributeConfig`
- {class}`~tango.AttributeConfig_2`
- {class}`~tango.AttributeConfig_3`
- {class}`~tango.AttributeConfig_5`
- {class}`~tango.ChangeEventProp`
- {class}`~tango.EventProperties`
- {class}`~tango.MultiAttrProp`
- {class}`~tango.PeriodicEventProp`

## Modules removed

The following top-level modules can no longer be imported. They were for defining docstrings, and didn't have classes or
functions for public use: `tango.api_util`, `tango.callback`, `tango.device_data`, `tango.exception`.

---

**And this should be all notable API changes!**
