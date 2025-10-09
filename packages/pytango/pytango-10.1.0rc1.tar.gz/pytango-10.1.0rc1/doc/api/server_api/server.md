```{eval-rst}
.. currentmodule:: tango.server
```

(pytango-hlapi)=

# High level server API

```{eval-rst}
.. automodule:: tango.server
```

```{eval-rst}
.. hlist::

   * :class:`~tango.server.Device`
   * :class:`~tango.server.attribute`
   * :class:`~tango.server.command`
   * :class:`~tango.server.device_property`
   * :class:`~tango.server.class_property`
   * :func:`~tango.server.run`
   * :func:`~tango.server.server_run`
```

This module provides a high level device server API. It implements
[TEP1](#pytango-TEP1). It exposes an easier API for developing a Tango
device server.

Here is a simple example on how to write a *Clock* device server using the
high level API:

```
import time
from tango.server import run
from tango.server import Device
from tango.server import attribute, command


class Clock(Device):

    time = attribute()

    def read_time(self):
        return time.time()

    @command(dtype_in=str, dtype_out=str)
    def strftime(self, format):
        return time.strftime(format)


if __name__ == "__main__":
    run((Clock,))
```

Here is a more complete  example on how to write a *PowerSupply* device server
using the high level API. The example contains:

1. device description (via docstring), which user can get later as DeviceProxy.description()
2. default state DevState.ON and default status "Device is current supply mode"
3. a read-only double scalar attribute called *voltage*
4. a read/write double scalar expert attribute *current*
5. a read-only double image attribute called *noise*
6. a *ramp* command
7. a *host* device property
8. a *port* class property

```{code-block} python
:linenos: true

from time import time
from numpy.random import random_sample

from tango import AttrQuality, AttrWriteType, DevState, DispLevel
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

class PowerSupply(Device):
    """PyTango example of PowerSuppy device."""

    # alternative way to add device description (see note below)
    DEVICE_CLASS_DESCRIPTION = "PyTango example of PowerSuppy device."

    DEVICE_CLASS_INITIAL_STATUS = "Device is in current supply mode"
    DEVICE_CLASS_INITIAL_STATE  = DevState.ON

    voltage = attribute()

    current = attribute(label="Current", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ_WRITE,
                        unit="A", format="8.4f",
                        min_value=0.0, max_value=8.5,
                        min_alarm=0.1, max_alarm=8.4,
                        min_warning=0.5, max_warning=8.0,
                        fget="get_current", fset="set_current",
                        doc="the power supply current")

    noise = attribute(label="Noise", dtype=((float,),),
                      max_dim_x=1024, max_dim_y=1024,
                      fget="get_noise")

    host = device_property(dtype=str)
    port = class_property(dtype=int, default_value=9788)

    def read_voltage(self):
        self.info_stream(f"Get voltage({self.host}, {self.port})")
        return 10.0

    def get_current(self):
        return 2.3456, time(), AttrQuality.ATTR_CHANGING

    def set_current(self, current):
        self.info_stream(f"Current set to {current}")

    def get_noise(self):
        return random_sample((1024, 1024))

    @command(dtype_in=float)
    def ramp(self, value):
        self.info_stream(f"Ramp up requested: {value} seconds")

if __name__ == "__main__":
    PowerSupply.run_server()
```

*Pretty cool, uh?*

:::{note}
the device description can be added either by class docstring or by DEVICE_CLASS_DESCRIPTION class member, the latter has priority over the docstring.
The important difference is that DEVICE_CLASS_DESCRIPTION will be inherited by child classes, while the docstring will not be.
:::

(pytango-hlapi-datatypes)=

```{rubric} Data types
```

When declaring attributes, properties or commands, one of the most important
details is the data type. It is given by the keyword argument *dtype*.
In order to provide a more *pythonic* interface, this argument is not restricted
to the {obj}`~tango.CmdArgType` options.

For example, to define a *SCALAR* {obj}`~tango.CmdArgType.DevLong`
attribute you have several possibilities:

1. {obj}`int`
2. 'int'
3. 'int64'
4. {obj}`tango.CmdArgType.DevLong64`
5. 'DevLong64'
6. {obj}`numpy.int64`

To define a *SPECTRUM* attribute simply wrap the scalar data type in any
python sequence:

- using a *tuple*: `` (:obj:`int`,) `` or
- using a *list*: `` [:obj:`int`] `` or
- any other sequence type

To define an *IMAGE* attribute simply wrap the scalar data type in any
python sequence of sequences:

- using a *tuple*: `` ((:obj:`int`,),) `` or
- using a *list*: `` [[:obj:`int`]] `` or
- any other sequence type

Below is the complete table of equivalences.

| dtype argument              | converts to tango type    |
| --------------------------- | ------------------------- |
| `None`                      | `DevVoid`                 |
| `'None'`                    | `DevVoid`                 |
| `DevVoid`                   | `DevVoid`                 |
| `'DevVoid'`                 | `DevVoid`                 |
| `DevState`                  | `DevState`                |
| `'DevState'`                | `DevState`                |
| {py:obj}`bool`              | `DevBoolean`              |
| `'bool'`                    | `DevBoolean`              |
| `'boolean'`                 | `DevBoolean`              |
| `DevBoolean`                | `DevBoolean`              |
| `'DevBoolean'`              | `DevBoolean`              |
| {py:obj}`numpy.bool_`       | `DevBoolean`              |
| `'char'`                    | `DevUChar`                |
| `'chr'`                     | `DevUChar`                |
| `'byte'`                    | `DevUChar`                |
| `chr`                       | `DevUChar`                |
| `DevUChar`                  | `DevUChar`                |
| `'DevUChar'`                | `DevUChar`                |
| {py:obj}`numpy.uint8`       | `DevUChar`                |
| `'int16'`                   | `DevShort`                |
| `DevShort`                  | `DevShort`                |
| `'DevShort'`                | `DevShort`                |
| {py:obj}`numpy.int16`       | `DevShort`                |
| `'uint16'`                  | `DevUShort`               |
| `DevUShort`                 | `DevUShort`               |
| `'DevUShort'`               | `DevUShort`               |
| {py:obj}`numpy.uint16`      | `DevUShort`               |
| `'int32'`                   | `DevLong`                 |
| `DevLong`                   | `DevLong`                 |
| `'DevLong'`                 | `DevLong`                 |
| {py:obj}`numpy.int32`       | `DevLong`                 |
| `'uint32'`                  | `DevULong`                |
| `DevULong`                  | `DevULong`                |
| `'DevULong'`                | `DevULong`                |
| {py:obj}`numpy.uint32`      | `DevULong`                |
| {py:obj}`int`               | `DevLong64`               |
| `'int'`                     | `DevLong64`               |
| `'int64'`                   | `DevLong64`               |
| `DevLong64`                 | `DevLong64`               |
| `'DevLong64'`               | `DevLong64`               |
| {py:obj}`numpy.int64`       | `DevLong64`               |
| `'uint'`                    | `DevULong64`              |
| `'uint64'`                  | `DevULong64`              |
| `DevULong64`                | `DevULong64`              |
| `'DevULong64'`              | `DevULong64`              |
| {py:obj}`numpy.uint64`      | `DevULong64`              |
| `'float32'`                 | `DevFloat`                |
| `DevFloat`                  | `DevFloat`                |
| `'DevFloat'`                | `DevFloat`                |
| {py:obj}`numpy.float32`     | `DevFloat`                |
| {py:obj}`float`             | `DevDouble`               |
| `'double'`                  | `DevDouble`               |
| `'float'`                   | `DevDouble`               |
| `'float64'`                 | `DevDouble`               |
| `DevDouble`                 | `DevDouble`               |
| `'DevDouble'`               | `DevDouble`               |
| {py:obj}`numpy.float64`     | `DevDouble`               |
| {py:obj}`str`               | `DevString`               |
| `'str'`                     | `DevString`               |
| `'string'`                  | `DevString`               |
| `'text'`                    | `DevString`               |
| `DevString`                 | `DevString`               |
| `'DevString'`               | `DevString`               |
| {py:obj}`bytearray`         | `DevEncoded`              |
| `'bytearray'`               | `DevEncoded`              |
| `'bytes'`                   | `DevEncoded`              |
| `DevEncoded`                | `DevEncoded`              |
| `'DevEncoded'`              | `DevEncoded`              |
| `DevVarBooleanArray`        | `DevVarBooleanArray`      |
| `'DevVarBooleanArray'`      | `DevVarBooleanArray`      |
| `DevVarCharArray`           | `DevVarCharArray`         |
| `'DevVarCharArray'`         | `DevVarCharArray`         |
| `DevVarShortArray`          | `DevVarShortArray`        |
| `'DevVarShortArray'`        | `DevVarShortArray`        |
| `DevVarLongArray`           | `DevVarLongArray`         |
| `'DevVarLongArray'`         | `DevVarLongArray`         |
| `DevVarLong64Array`         | `DevVarLong64Array`       |
| `'DevVarLong64Array'`       | `DevVarLong64Array`       |
| `DevVarULong64Array`        | `DevVarULong64Array`      |
| `'DevVarULong64Array'`      | `DevVarULong64Array`      |
| `DevVarFloatArray`          | `DevVarFloatArray`        |
| `'DevVarFloatArray'`        | `DevVarFloatArray`        |
| `DevVarDoubleArray`         | `DevVarDoubleArray`       |
| `'DevVarDoubleArray'`       | `DevVarDoubleArray`       |
| `DevVarUShortArray`         | `DevVarUShortArray`       |
| `'DevVarUShortArray'`       | `DevVarUShortArray`       |
| `DevVarULongArray`          | `DevVarULongArray`        |
| `'DevVarULongArray'`        | `DevVarULongArray`        |
| `DevVarStringArray`         | `DevVarStringArray`       |
| `'DevVarStringArray'`       | `DevVarStringArray`       |
| `DevVarLongStringArray`     | `DevVarLongStringArray`   |
| `'DevVarLongStringArray'`   | `DevVarLongStringArray`   |
| `DevVarDoubleStringArray`   | `DevVarDoubleStringArray` |
| `'DevVarDoubleStringArray'` | `DevVarDoubleStringArray` |

```{eval-rst}
.. autoclass:: Device
   :show-inheritance:
   :inherited-members:
   :members:
```

```{eval-rst}
.. autoclass:: attribute
```

```{eval-rst}
.. autofunction:: command
```

```{eval-rst}
.. autoclass:: device_property
```

```{eval-rst}
.. autoclass:: class_property
```

```{eval-rst}
.. autofunction:: run
```

```{eval-rst}
.. autofunction:: server_run
```
