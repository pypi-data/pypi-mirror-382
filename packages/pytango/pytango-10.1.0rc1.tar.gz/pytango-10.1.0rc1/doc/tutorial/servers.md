```{eval-rst}
.. currentmodule:: tango
```

(server-new-api)=

# Writing TANGO servers in Python

## Quick start

Since PyTango 8.1 it has become much easier to program a Tango device server.
PyTango provides some helpers that allow developers to simplify the programming
of a Tango device server.

Before reading this chapter you should be aware of the TANGO basic concepts.
This chapter does not explain what a Tango device or a device server is.
This is explained in detail in the
[Tango control system manual](http://www.tango-controls.org/documentation/kernel/)

You may also read the [high level server API](#pytango-hlapi) for the complete reference API.

Before creating a server you need to decide:

1. The Tango Class name of your device (example: `Clock`). In our
   example we will use the same name as the python class name.
2. The list of attributes of the device, their data type, access (read-only vs
   read-write), data_format (scalar, 1D, 2D)
3. The list of commands, their parameters and their result

Here is a simple example on how to write a *Clock* device server using the
high level API

```{code-block} python
:linenos: true

 import time
 from tango.server import Device, device_property, attribute, command


 class Clock(Device):

     model = device_property(dtype=str)

     @attribute
     def time(self):
         return time.time()

     @command(dtype_in=str, dtype_out=str)
     def strftime(self, format):
         return time.strftime(format)

 if __name__ == "__main__":
     Clock.run_server()
```

**line 2**

: import the necessary symbols

**line 5**

: tango device class definition. A Tango device must inherit from
  {class}`tango.server.Device`

**line 7**

: definition of the *model* property. Check the
  {class}`~tango.server.device_property` for the complete list of options

**line 9-11**

: definition of the *time* attribute. By default, attributes are double, scalar,
  read-only. Check the {class}`~tango.server.attribute` for the complete
  list of attribute options.

**line 13-15**

: the method *strftime* is exported as a Tango command. In receives a string
  as argument and it returns a string. If a method is to be exported as a
  Tango command, it must be decorated as such with the
  {func}`~tango.server.command` decorator

**line 18**

: start the Tango run loop.  This method automatically determines the Python
  class name and exports it as a Tango class.  For more complicated cases,
  check {func}`~tango.server.run` for the complete list of options

Before running this brand new server we need to register it in the Tango system.
You can do it with Jive (`Jive->Edit->Create server`):

```{image} ../_static/jive_clock.png
```

... or in a python script:

```
import tango

dev_info = tango.DbDevInfo()
dev_info.server = "Clock/test"
dev_info._class = "Clock"
dev_info.name = "test/Clock/1"

db = tango.Database()
db.add_device(dev_info)
```

## Start server from command line

To start server from the command line execute the following command:

```console
$ python Clock.py test
Ready to accept request
```

:::{note}
In this example, the name of the server and the name of the tango
class are the same: `Clock`. This pattern is enforced by the
{meth}`~tango.server.Device.run_server` method. However, it is possible
to run several tango classes in the same server. In this case, the server
name would typically be the name of server file. See the
{func}`~tango.server.run` function for further information.
:::

To run server without database use option `-nodb`.

```console
$ python <server_file>.py <instance_name> -nodb -port 10000
Ready to accept request
```

Note, that to start server in this mode you should provide a port with either `--port`, or `--ORBendPoint` option

Additionally, you can use the following options:

:::{note}
all long-options can be provided in non-POSIX format: `-port` or `--port`, etc...
:::

```console
-h, -?, --help : show usage help

-v, --verbose: set the trace level. Can be user in count way: -vvvv set level to 4 or --verbose --verbose set to 2

-vN: directly set the trace level to N, e.g., -v3 - set level to 3

--file <file_name>: start a device server using an ASCII file instead of the Tango database

--host <host_name>: force the host from which server accept requests

--port <port>: force the port on which the device server listens

--nodb: run server without DB

--dlist <dev1,dev2,etc>: the device name list. This option is supported only with the -nodb option

--ORBendPoint giop:tcp:<host>:<port>: Specifying the host from which server accept requests and port on which the device server listens.
```

:::{note}
any ORB option can be provided if it starts with --ORB\<option>
:::

Additionally, in Windows the following option can be used:

```console
-i: install the service

-s: install the service and choose the automatic startup mode

-u: uninstall the service

--dbg: run in console mode to debug service. The service must have been installed prior to use it.
```

## Advanced attributes configuration

There is a more detailed clock device server in the examples/Clock folder.

Here is a more complete example on how to write a *PowerSupply* device server
using the high level API. The example contains:

1. a *host* device property
2. a *port* class property
3. the standard initialisation method called *init_device*
4. a read/write double scalar expert attribute *current*
5. a read-only double scalar attribute called *voltage*
6. a read-only double image attribute called *noise*
7. a read/write float scalar attribute *range*, defined with pythonic-style decorators, which can be always read, but conditionally written
8. a read/write float scalar attribute *compliance*, defined with alternative decorators
9. an *output_on_off* command

```{code-block} python
:linenos: true

from time import time
from numpy.random import random_sample

from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType
from tango.server import Device, attribute, command
from tango.server import class_property, device_property


class PowerSupply(Device):
    _my_current = 2.3456
    _my_range = 0.0
    _my_compliance = 0.0
    _output_on = False

    host = device_property(dtype=str)
    port = class_property(dtype=int, default_value=9788)

    def init_device(self):
        super().init_device()
        self.info_stream(f"Power supply connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.set_status("Power supply is ON")

    current = attribute(
        label="Current",
        dtype=float,
        display_level=DispLevel.EXPERT,
        access=AttrWriteType.READ_WRITE,
        unit="A",
        format="8.4f",
        min_value=0.0,
        max_value=8.5,
        min_alarm=0.1,
        max_alarm=8.4,
        min_warning=0.5,
        max_warning=8.0,
        fget="get_current",
        fset="set_current",
        doc="the power supply current",
    )

    noise = attribute(
        label="Noise",
        dtype=((float,),),
        max_dim_x=1024,
        max_dim_y=1024,
        fget="get_noise",
    )

    @attribute
    def voltage(self):
        return 10.0

    def get_current(self):
        return self._my_current

    def set_current(self, current):
        print("Current set to %f" % current)
        self._my_current = current

    def get_noise(self):
        return random_sample((1024, 1024))

    range = attribute(label="Range", dtype=float)

    @range.setter
    def range(self, new_range):
        self._my_range = new_range

    @range.getter
    def current_range(self):
        return self._my_range, time(), AttrQuality.ATTR_WARNING

    @range.is_allowed
    def can_range_be_changed(self, req_type):
        if req_type == AttReqType.WRITE_REQ:
            return not self._output_on
        return True

    compliance = attribute(label="Compliance", dtype=float)

    @compliance.read
    def compliance(self):
        return self._my_compliance

    @compliance.write
    def new_compliance(self, new_compliance):
        self._my_compliance = new_compliance

    @command(dtype_in=bool, dtype_out=bool)
    def output_on_off(self, on_off):
        self._output_on = on_off
        return self._output_on


if __name__ == "__main__":
    PowerSupply.run_server()
```

(dynamic-attributes-howto)=

## Create attributes dynamically

It is also possible to create dynamic attributes within a Python device server.
There are several ways to create dynamic attributes. One of the ways, is to
create all the devices within a loop, then to create the dynamic attributes and
finally to make all the devices available for the external world. In a C++ device
server, this is typically done within the \<Device>Class::device_factory() method.
In Python device server, this method is generic and the user does not have one.
Nevertheless, this generic device_factory provides the user with a way to create
dynamic attributes.

Using the high-level API, you can re-define a method called
{meth}`~tango.server.Device.initialize_dynamic_attributes`
on each \<Device>. This method will be called automatically by the device_factory for
each device. Within this method you create all the dynamic attributes.

If you are still using the low-level API with a \<Device>Class instead of just a \<Device>,
then you can use the generic device_factory's call to the
{meth}`~tango.DeviceClass.dyn_attr` method.
It is simply necessary to re-define this method within your \<Device>Class and to create
the dynamic attributes within this method.

Internally, the high-level API re-defines {meth}`~tango.DeviceClass.dyn_attr` to call
{meth}`~tango.server.Device.initialize_dynamic_attributes` for each device.

:::{note}
The `dyn_attr()` (and `initialize_dynamic_attributes()` for high-level API) methods
are only called **once** when the device server starts, since the Python device_factory
method is only called once. Within the device_factory method, `init_device()` is
called for all devices and only after that is `dyn_attr()` called for all devices.
If the `Init` command is executed on a device it will not call the `dyn_attr()` method
again (and will not call `initialize_dynamic_attributes()` either).
:::

There is another point to be noted regarding dynamic attributes within a Python
device server. The Tango Python device server core checks that for each
static attribute there exists methods named \<attribute_name>\_read and/or
\<attribute_name>\_write and/or is\_\<attribute_name>\_allowed. Using dynamic
attributes, it is not possible to define these methods because attribute names
and number are known only at run-time.
To address this issue, you need to provide references to these methods when
calling {meth}`~tango.server.Device.add_attribute`.

The recommended approach with the high-level API is to reference these methods when
instantiating a {class}`tango.server.attribute` object using the fget, fset and/or
fisallowed kwargs (see example below).  Where fget is the method which has to be
executed when the attribute is read, fset is the method to be executed
when the attribute is written and fisallowed is the method to be executed
to implement the attribute state machine.  This {class}`tango.server.attribute` object
is then passed to the {meth}`~tango.server.Device.add_attribute` method.

:::{note}
If the fget (fread), fset (fwrite) and fisallowed are given as str(name) they must be methods
that exist on your Device class. If you want to use plain functions, or functions belonging to a
different class, you should pass a callable.
:::

Which arguments you have to provide depends on the type of the attribute.  For example,
a WRITE attribute does not need a read method.

:::{note}
Starting from PyTango 9.4.0 the read methods for dynamic attributes
can also be implemented with the high-level API.  Prior to that, only the low-level
API was available.
:::

For the read function it is possible to use one of the following signatures:

```
def low_level_read(self, attr):
    attr.set_value(self.attr_value)

def high_level_read(self, attr):
    return self.attr_value
```

For the write function there is only one signature:

```
def low_level_write(self, attr):
    self.attr_value = attr.get_write_value()
```

Here is an example of a device which creates a dynamic attribute on startup:

```
from tango import AttrWriteType
from tango.server import Device, attribute

class MyDevice(Device):

    def initialize_dynamic_attributes(self):
        self._values = {"dyn_attr": 0}
        attr = attribute(
            name="dyn_attr",
            dtype=int,
            access=AttrWriteType.READ_WRITE,
            fget=self.generic_read,
            fset=self.generic_write,
            fisallowed=self.generic_is_allowed,
        )
        self.add_attribute(attr)

    def generic_read(self, attr):
        attr_name = attr.get_name()
        value = self._values[attr_name]
        return value

    def generic_write(self, attr):
        attr_name = attr.get_name()
        value = attr.get_write_value()
        self._values[attr_name] = value

    def generic_is_allowed(self, request_type):
        # note: we don't know which attribute is being read!
        # request_type will be either AttReqType.READ_REQ or AttReqType.WRITE_REQ
        return True
```

Another way to create dynamic attributes is to do it some time after the device has
started.  For example, using a command.  In this case, we just call the
{meth}`~tango.server.Device.add_attribute` method when necessary.

Here is an example of a device which has a TANGO command called
*CreateFloatAttribute*. When called, this command creates a new scalar floating
point attribute with the specified name:

```
from tango import AttrWriteType
from tango.server import Device, attribute, command

class MyDevice(Device):

    def init_device(self):
        super(MyDevice, self).init_device()
        self._values = {}

    @command(dtype_in=str)
    def CreateFloatAttribute(self, attr_name):
        if attr_name not in self._values:
            self._values[attr_name] = 0.0
            attr = attribute(
                name=attr_name,
                dtype=float,
                access=AttrWriteType.READ_WRITE,
                fget=self.generic_read,
                fset=self.generic_write,
            )
            self.add_attribute(attr)
            self.info_stream("Added dynamic attribute %r", attr_name)
        else:
            raise ValueError(f"Already have an attribute called {repr(attr_name)}")

    def generic_read(self, attr):
        attr_name = attr.get_name()
        self.info_stream("Reading attribute %s", attr_name)
        value = self._values[attr.get_name()]
        attr.set_value(value)

    def generic_write(self, attr):
        attr_name = attr.get_name()
        value = attr.get_write_value()
        self.info_stream("Writing attribute %s - value %s", attr_name, value)
        self._values[attr.get_name()] = value
```

An approach more in line with the low-level API is also possible, but not recommended for
new devices. The Device_3Impl::add_attribute() method has the following
signature:

> `add_attribute(self, attr, r_meth=None, w_meth=None, is_allo_meth=None)`

attr is an instance of the {class}`tango.Attr` class, r_meth is the method which has to be
executed when the attribute is read, w_meth is the method to be executed
when the attribute is written and is_allo_meth is the method to be executed
to implement the attribute state machine.

Old example:

```
from tango import Attr, AttrWriteType
from tango.server import Device, command

class MyOldDevice(Device):

    @command(dtype_in=str)
    def CreateFloatAttribute(self, attr_name):
        attr = Attr(attr_name, tango.DevDouble, AttrWriteType.READ_WRITE)
        self.add_attribute(attr, self.read_General, self.write_General)

    def read_General(self, attr):
        self.info_stream("Reading attribute %s", attr.get_name())
        attr.set_value(99.99)

    def write_General(self, attr):
        self.info_stream("Writing attribute %s - value %s", attr.get_name(), attr.get_write_value())
```

(decorators)=

## Attributes and commands with decorated functions

PyTango offers support of decorated methods for attributes methods (read, write and is_allowed) as well as for commands (command and is_allowed method)
Nevertheless, there are a few peculiarities:

1. for **attributes**, all additional decorators must be applied below the `@attribute` decorator:

```python
# valid attribute declaration
@attribute
@my_perfect_decorator
def correct_attribute(self) -> str:
    return "This works"

# invalid attribute declaration!!!
@my_perfect_decorator
@attribute
def bad_attribute(self) -> str:
    return "But this does not"
```

2. for sync, futures and gevent green mode **commands**, the sequence of decorators is not as strict:

```python
# valid command declaration
@command
@my_perfect_decorator
def recommended_command(self) -> str:
    return "This works"

# also valid command declaration
@my_perfect_decorator
@command
def alternative_command(self) -> str:
    return "This works, but has some limitations"
```

:::{note}
There is a small difference: for all decorators applied *below* `@command` (as shown in first example above)
it will be possible to put breakpoints in their code, and they will be included in
[test coverage](#test-coverage) reports.
This is not the case for any decorators applied *above* `@command` (thus the limitations for
the second example above).
:::

3. for asyncio green mode **commands**, the sequence of decorators is similar to other green modes, but all
   decorators applied *below* `@command` must be async while all decorators applied *above* `@command` must
   be sync:

```python
# valid async command declaration
@my_perfect_sync_decorator
@command
@my_perfect_async_decorator
async def good_command(self) -> str:
    return "This works"

# this won't work
@my_perfect_sync_decorator
@command
@my_perfect_sync_decorator
async def bad_command(self) -> str:
    return "But this does not"

# this won't work either
@my_perfect_async_decorator
@command
@my_perfect_async_decorator
async def another_bad_command(self) -> str:
    return "This does not either"

# and this won't work
@my_perfect_async_decorator
@command
@my_perfect_sync_decorator
async def also_a_bad_command(self) -> str:
    return "Nor does this work"
```

(type-hint)=

## Use Python type hints when declaring a device

Starting from PyTango 9.5.0 the data type of properties, attributes and commands
in high-level API device servers can be declared using Python type hints.

This is the same simple *PowerSupply* device server, but using type hints in various ways:

```{code-block} python
:linenos: true

 from time import time
 from numpy.random import random_sample

 from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType
 from tango.server import Device, attribute, command
 from tango.server import class_property, device_property


 class PowerSupply(Device):
     _my_current = 2.3456
     _my_range = 0
     _my_compliance = 0.0
     _output_on = False

     host: str = device_property()
     port: int = class_property(default_value=9788)

     def init_device(self):
         super().init_device()
         self.info_stream(f"Power supply connection details: {self.host}:{self.port}")
         self.set_state(DevState.ON)
         self.set_status("Power supply is ON")

     current: float = attribute(
         label="Current",
         display_level=DispLevel.EXPERT,
         access=AttrWriteType.READ_WRITE,
         unit="A",
         format="8.4f",
         min_value=0.0,
         max_value=8.5,
         min_alarm=0.1,
         max_alarm=8.4,
         min_warning=0.5,
         max_warning=8.0,
         fget="get_current",
         fset="set_current",
         doc="the power supply current",
     )

     noise: list[list[float]] = attribute(
         label="Noise", max_dim_x=1024, max_dim_y=1024, fget="get_noise"
     )

     @attribute
     def voltage(self) -> float:
         return 10.0

     def get_current(self):
         return self._my_current

     def set_current(self, current):
         print("Current set to %f" % current)
         self._my_current = current

     def get_noise(self):
         return random_sample((1024, 1024))

     range = attribute(label="Range")

     @range.getter
     def current_range(self) -> tuple[float, float, AttrQuality]:
         return self._my_range, time(), AttrQuality.ATTR_WARNING

     @range.setter
     def range(self, new_range: float):
         self._my_range = new_range

     @range.is_allowed
     def can_range_be_changed(self, req_type):
         if req_type == AttReqType.WRITE_REQ:
             return not self._output_on
         return True

     compliance = attribute(label="Compliance")

     @compliance.read
     def compliance(self) -> float:
         return self._my_compliance

     @compliance.write
     def new_compliance(self, new_compliance: float):
         self._my_compliance = new_compliance

     @command
     def output_on_off(self, on_off: bool) -> bool:
         self._output_on = on_off
         return self._output_on


 if __name__ == "__main__":
     PowerSupply.run_server()
```

:::{note}
To defining DevEncoded attribute you can use type hints *tuple\[str, bytes\]* and *tuple\[str, bytearray\]*
(or *tuple\[str, bytes, float, AttrQuality\]* and *tuple\[str, bytearray, float, AttrQuality\]*).

Type hints *tuple\[str, str\]* (or *tuple\[str, str, float, AttrQuality\]*) will be recognized as SPECTRUM DevString attribute with max_dim_x=2

If you want to create DevEncoded attribute with *(str, str)* return you have to use dtype kwarg
:::

:::{note}
To defining DevVarLongStringArray and DevVarDoubleStringArray commands you can use type hints *tuple\[tuple\[int\], tuple\[str\]\]* and *tuple\[tuple\[float\], tuple\[str\]\]*
(or *tuple\[tuple\[int\], tuple\[str\], float, AttrQuality\]* and *tuple\[tuple\[float\], tuple\[str\], float, AttrQuality\]*), respectively. You can use also list\[\] declarations in all combinations.
Since commands does not have dimension parameter, length of the tuple\[\] is ignored (see description of commands below)
:::

:::{note}
There are some peculiarities with type hints if you are using "from \_\_future\_\_ import annotations":
In that case, Python doesn't try to resolve the names of the types inside the type hints.
Instead, it stores them as strings. PyTango will try to resolve it later; however, this functionality is not guaranteed.
:::


**Properties**

To define device property you can use:

```python
host: str = device_property()
```

If you want to create list property you can use *tuple\[\]*, *list\[\]* or *numpy.typing.NDArray\[\]* annotation:

```python
channels: tuple[int] = device_property()
```

or

```python
channels: list[int] = device_property()
```

or

```python
channels: numpy.typing.NDArray[np.int_] = device_property()
```

**Attributes**
For the attributes you can use one of the following patterns:

```python
voltage: float = attribute()
```

or

```python
voltage = attribute()

def read_voltage(self) -> float:
    return 10.0
```

or

```python
voltage = attribute(fget="query_voltage")

def query_voltage(self) -> float:
    return 10.0
```

or

```python
@attribute
def voltage(self) -> float:
    return 10.0
```

For writable (AttrWriteType.READ_WRITE and AttrWriteType.WRITE) attributes you can also define the type in write functions.

:::{note}
Defining the type hint of a READ_WRITE attribute *only* in the write function is not recommended as it can lead to inconsistent code.
:::

```python
data_to_save = attribute(access=AttrWriteType.WRITE)

# since WRITE attribute can have only write method,
# its type can be defined here
def write_data_to_save(self, data: float)
    self._hardware.save(value)
```

:::{note}
If you provide a type hint in several places (e.g., dtype kwarg and read function): there is no check, that types are the same and attribute type will be taken according to the following priority:

1. dtype kwarg
2. attribute assignment
3. read function
4. write function
:::

E.g., if you create the following attribute:

```python
voltage: int = attribute(dtype=float)

def read_voltage(self) -> str:
    return 10
```

the attribute type will be float

**SPECTRUM and IMAGE attributes**

As for the case of properties, the SPECTRUM and IMAGE attributes can be defined by *tuple\[\]*, *list\[\]* or *numpy.typing.NDArray\[\]* annotation.

:::{note}
Since there isn't yet official support for *numpy.typing.NDArray\[\]* shape definitions (as at 12 October 2023: <https://github.com/numpy/numpy/issues/16544>) you **must** provide a *dformat* kwarg as well as *max_dim_x* (and, if necessary, *max_dim_y*):
:::

```python
@attribute(dformat=AttrDataFormat.SPECTRUM, max_dim_x=3)
def get_time(self) -> numpy.typing.NDArray[np.int_]:
    return hours, minutes, seconds
```

In case of *tuple\[\]*, *list\[\]* you can automatically specify attribute dimension:

```python
@attribute
def get_time(self) -> tuple[int, int, int]:
    return hours, minutes, seconds
```

or you can use max_dim_x(max_dim_y) kwarg with just one element in tuple/list:

```python
@attribute(max_dim_x=3)
def get_time(self) -> list[int]: # can be also tuple[int]
    return hours, minutes, seconds
```

:::{note}
If you provide both max_dim_x(max_dim_y) kwarg and use *tuple\[\]* annotation, kwarg will have priority
:::

:::{note}
Mixing element types within a spectrum(image) attribute definition is not supported by Tango and will raise a RuntimeError.
:::

e.g., attribute

```python
@attribute(max_dim_x=3)
def get_time(self) -> tuple[float, str]:
    return hours, minutes, seconds
```

will result in RuntimeError

Dimension of SPECTRUM attributes can be also taken from annotation:

```python
@attribute()
def not_matrix(self) -> tuple[tuple[bool, bool], tuple[bool, bool]]:
    return [[False, True],[True, False]]
```

:::{note}
max_y will be len of outer tuple (or list), max_x - len of the inner. Note, that all inner tuples(lists) must be the same length
:::

e.g.,

```python
tuple[tuple[bool, bool], tuple[bool, bool], tuple[bool, bool]]
```

will result in max_y=3, max_x=2

while

```python
tuple[tuple[bool, bool], tuple[bool], tuple[bool]]
```

will result in RuntimeError

**Commands**

Declaration of commands is the same as declaration of attributes with decorators:

```python
@command
def set_and_check_voltage(self, voltage_to_set: float) -> float:
    device.set_voltage(voltage_to_set)
    return device.get_voltage()
```

:::{note}
If you provide both type hints and dtype kwargs, the kwargs take priority:
:::

e.g.,

```python
@command(dtype_in=float, dtype_out=float)
def set_and_check_voltage(self, voltage_to_set: str) -> str:
    device.set_voltage(voltage_to_set)
    return device.get_voltage()
```

will be a command that accepts float and returns float.

As in case of attributes, the SPECTRUM commands can be declared with *tuple\[\]* or *list\[\]* annotation:

```python
@command
def set_and_check_voltages(self, voltages_set: tuple[float, float]) -> tuple[float, float]:
    device.set_voltage(channel1, voltages_set[0])
    device.set_voltage(channel2, voltages_set[1])
    return device.get_voltage(channel=1), device.get_voltage(channel=2)
```

:::{note}
Since commands do not have dimension parameters, length of tuple/list does not matter.  If the type hints indicates 2 floats in the input, PyTango does not check that the input for each call received arrived with length 2.
:::

**Dynamic attributes with type hint**

:::{note}
Starting from PyTango 9.5.0 dynamic attribute type can be defined by type hints in the read/write methods.
:::

Usage of type hints is described in {ref}`type-hint` .
The only difference in case of dynamic attributes is, that there is no option to use type hint in attribute at assignment

e.g., the following code won't work:

```python
def initialize_dynamic_attributes(self):
    voltage: float = attribute() # CANNOT BE AN OPTION FOR DYNAMIC ATTRIBUTES!!!!!!!!
    self.add_attribute(attr)
```

(version-info)=

## Add detailed version information to a device

Since PyTango v10.0.0, devices can add custom version information, using
the {meth}`~tango.server.Device.add_version_info` method.  A copy of the version information
dict can be read within the device using the {meth}`~tango.server.Device.get_version_info` method.
Clients can get the information using the standard {meth}`~tango.DeviceProxy.info` method.

```python
from tango.server import Device

__version__ = "1.0.0"


class Demo(Device):

    def init_device(self):
        super().init_device()
        self.add_version_info("MyDemo.Name", "Demo version info")
        self.add_version_info("MyDemo.Source", __file__)
        self.add_version_info("MyDemo.Version", __version__)

if __name__ == "__main__":
    Demo.run_server()
```

Put the above code in a file called `ver_info_demo.py`.  Then run it locally without a Tango database
in your PyTango environment using the {mod}`tango.test_context` module
(which uses {class}`~tango.test_context.DeviceTestContext`):

```console
$ python -m tango.test_context ver_info_demo.Demo --host 127.0.0.1
Can't create notifd event supplier. Notifd event not available
Ready to accept request
Demo started on port 8888 with properties {}
Device access: tango://127.0.0.1:8888/test/nodb/demo#dbase=no
Server access: tango://127.0.0.1:8888/dserver/Demo/demo#dbase=no
```

Then you can access the information as a client.  Note the {meth}`~tango.DeviceProxy.info` method
returns a {class}`~tango.DeviceInfo` object with some additional information:

```
>>> from tango import DeviceProxy

>>> dp = DeviceProxy("tango://127.0.0.1:8888/test/nodb/demo#dbase=no")
>>> info = dp.info()
>>> print(info)
DeviceInfo[
    dev_class = "Demo"
    dev_type = "Demo"
    doc_url = "Doc URL = http://www.tango-controls.org"
    server_host = "myhost.domain"
    server_id = "Demo/Demo"
    server_version = 6
    version_info = {
        "Build.PyTango.NumPy": "2.2.3",
        "Build.PyTango.Pybind11": "3.0.1",
        "Build.PyTango.Python": "3.13.2",
        "Build.PyTango.cppTango": "10.0.2",
        "MyDemo.Name": "Demo version info",
        "MyDemo.Source": "/path/to/ver_info_demo.py",
        "MyDemo.Version": "1.0.0",
        "NumPy": "2.2.3",
        "PyTango": "10.1.0.dev1",
        "Python": "3.13.2",
        "cppTango": "10.0.2",
        "cppTango.git_revision": "unknown",
        "cppzmq": "41000",
        "idl": "6.0.2",
        "omniORB": "4.3.2",
        "opentelemetry-cpp": "1.18.0",
        "zmq": "40305"
    }
]
>>> print(info.version_info["MyDemo.Version"])
1.0.0
```
