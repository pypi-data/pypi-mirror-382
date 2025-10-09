```{eval-rst}
.. currentmodule:: tango
```

(clients)=

# Python clients to TANGO servers

In the examples here we connect to a device called *sys/tg_test/1* that runs in a
TANGO server called *TangoTest* with the instance name *test*.
This server comes with the TANGO installation. The TANGO installation
also registers the *test* instance. All you have to do is start the TangoTest
server on a console:

```
$ TangoTest test
Ready to accept request
```

:::{note}
if you receive a message saying that the server is already running,
it just means that somebody has already started the test server so you don't
need to do anything.
:::

:::{note}
PyTango used to come with an integrated [IPython](https://ipython.org) based console called
{ref}`itango`, now moved to a separate project. It provides helpers to simplify
console usage. You can use this console instead of the traditional python
console. Be aware, though, that many of the *tricks* you can do in an
{ref}`itango` console cannot be done in a python program.
:::

## Test the connection to the Device and get it's current state

One of the most basic examples is to get a reference to a device and
determine if it is running or not:

```
import tango

# create a device object
tango_test = tango.DeviceProxy("sys/tg_test/1")

# you can ping it
print(f"Ping: {tango_test.ping()}")

# every device has a state and status which can be checked with:
print(f"State: {tango_test.state()}")
print(f"Status: {tango_test.status()}")
```

If you execute:

```
Ping: 264
State: RUNNING
Status: The device is in RUNNING state.
```

## Read and write attributes

Basic read/write attribute operations:

```
from tango import DeviceProxy

# Get proxy on the tango_test1 device
print("Creating proxy to TangoTest device...")
tango_test = DeviceProxy("sys/tg_test/1")

# Read a scalar attribute. This will return a tango.DeviceAttribute
# Member 'value' contains the attribute value
scalar = tango_test.read_attribute("long_scalar")
print(f"Long_scalar value = {scalar.value}")

# Check the complete DeviceAttribute members:
print(f"\n{scalar}\n")

# Write a scalar attribute
scalar_value = 18
tango_test.write_attribute("long_scalar", scalar_value)
```

If you execute:

```
Creating proxy to TangoTest device...
Long_scalar value = 44

DeviceAttribute[
data_format = tango._tango.AttrDataFormat.SCALAR
      dim_x = 1
      dim_y = 0
 has_failed = False
   is_empty = False
       name = 'long_scalar'
    nb_read = 1
 nb_written = 1
    quality = tango._tango.AttrQuality.ATTR_VALID
r_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
       time = TimeVal(tv_nsec = 0, tv_sec = 1707833196, tv_usec = 456892)
       type = tango._tango.CmdArgType.DevLong
      value = 44
    w_dim_x = 1
    w_dim_y = 0
w_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
w_value = 0]
```

PyTango also provides more "pythonic" way - so called High API, to do the same:

```
from tango import DeviceProxy

# Get proxy on the tango_test1 device
print("Creating proxy to TangoTest device...")
tango_test = DeviceProxy("sys/tg_test/1")

# Read a scalar attribute value directly
scalar_value = tango_test.long_scalar
print(f"Long_scalar value = {scalar_value}")

# Write a scalar attribute
tango_test.long_scalar = scalar_value

# Check the complete DeviceAttribute members:
scalar_value = tango_test["long_scalar"]
print(f"\nLong_scalar attribute:\n{scalar_value}")
```

if you run:

```
Creating proxy to TangoTest device...
Long_scalar value = 8

Long_scalar attribute:
DeviceAttribute[
data_format = tango._tango.AttrDataFormat.SCALAR
      dim_x = 1
      dim_y = 0
 has_failed = False
   is_empty = False
       name = 'long_scalar'
    nb_read = 1
 nb_written = 1
    quality = tango._tango.AttrQuality.ATTR_VALID
r_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
       time = TimeVal(tv_nsec = 0, tv_sec = 1707833578, tv_usec = 542918)
       type = tango._tango.CmdArgType.DevLong
      value = 8
    w_dim_x = 1
    w_dim_y = 0
w_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
    w_value = 8]
```

The multidimensional attributes in Pytango by defaults are numpy arrays (SPECTRUM - 1D, IMAGE - 2D).
This results in a faster and more memory efficient PyTango:

```
from tango import DeviceProxy
tango_test = DeviceProxy("sys/tg_test/1")

print(f"double_spectrum: {tango_test.double_spectrum}")
print(f"double_spectrum type: {type(tango_test.double_spectrum)}")
```

Result:

```
double_spectrum: [0. 0. 0. .....  0. 0.]
double_spectrum type: <class 'numpy.ndarray'>
```

You can also use numpy to specify the values when
writing attributes, especially if you know the exact attribute type:

```
from tango import DeviceProxy
import numpy

tango_test = DeviceProxy("sys/tg_test/1")

tango_test.long_spectrum = numpy.arange(0, 100, dtype=numpy.int32)

data_2d_float = numpy.zeros((10, 20), dtype=numpy.float64)
tango_test.double_image = data_2d_float
```

However, if you want, you can force python's types:

```
from tango import DeviceProxy, ExtractAs
tango_test = DeviceProxy("sys/tg_test/1")

double_spectrum = tango_test.read_attribute("double_spectrum", extract_as=ExtractAs.List)

print(f"double_spectrum: {double_spectrum.value}")
print(f"double_spectrum type: {type(double_spectrum.value)}")
```

Result:

```
double_spectrum: [0.0, 0.0, 0.0, .... 0.0, 0.0]
double_spectrum type: <class 'list'>
```

## DeviceProxy's and AttributeProxy's hasattr method peculiarities:

The `hasattr` method of DeviceProxy and inheriting AttributeProxy classes could sometime raise an exception.
Python's `hasattr` uses `getattr()`, so it calls the DeviceProxy's custom `__getattr__` method. This is going to try and read the attribute from the remote Tango device.  You will get an exception if the device is not reachable, times out, or raises an exception when read.  E.g., an attribute with an "is allowed" check, could raise because it may not be read at the moment.

So this method is not a reliable way to check if a device has a certain Tango attribute. There are a few alternative options:
### 1. Custom function

Make your own function, that uses `get_attribute_list()`, and ignores the errors you do not care about.

### 2. Use Python's `dir()` built-in

This calls the custom `DeviceProxy.__dir__` method.

```py
python_or_tango_attr_exists = "your_attribute" in dir(your_device_proxy)
```

Note:
- Doesn't raise, even if device is not available
- Checks both commands and attributes, with a fresh call to `get_command_list()` and ` get_attribute_list()`.
- Also includes all methods on the DeviceProxy object, like `ping`, `name`, `subscribe_event`, etc.
- The `dir()` result includes the Tango attribute and commands in both original, and lower case.  If you have an attribute called `myAttr` or `myATTR`, you could always check for `"myattr" in dir(det8.proxy)`.

### 3. Use the `in` keyword

This calls the custom `DeviceProxy.__contains__` method.

```py
tango_attr_exists = "your_attribute" in your_device_proxy
```

Note:
  - Only check attributes, doing a fresh `get_attribute_list()`.
  - Does a case-insensitive check.  Something like `"YoUr_AttRiBuTe" in your_device_proxy` would also work.
  - Raises a `DevFailed` exception if the `get_attribute_list()` call fails.


## Execute commands

As you can see in the following example, when scalar types are used, the Tango
binding automagically manages the data types, and writing scripts is quite easy:

```
from tango import DeviceProxy
tango_test = DeviceProxy("sys/tg_test/1")

# First use the classical command_inout way to execute the DevString command
# (DevString in this case is a command of the Tango_Test device)

result = tango_test.command_inout("DevString", "First hello to device")
print(f"Result of execution of DevString command = {result}")

# the same can be achieved with a helper method
result = tango_test.DevString("Second Hello to device")
print(f"Result of execution of DevString command = {result}")

# Please note that argin argument type is automatically managed by python
result = tango_test.DevULong(12456)
print(f"Result of execution of DevULong command = {result}")
```

Result:

```
Result of execution of DevString command = First hello to device
Result of execution of DevString command = Second Hello to device
Result of execution of DevULong command = 12456
```

## Execute commands with more complex types

In this case you have to use put your arguments data in the correct python
structures:

```
from tango import DeviceProxy
tango_test = DeviceProxy("sys/tg_test/1")

# The input argument is a DevVarLongStringArray so create the argin
# variable containing an array of longs and an array of strings
argin = ([1,2,3], ["Hello", "TangoTest device"])
result = tango_test.DevVarLongStringArray(argin)
print(f"Result of execution of DevVarLongArray command = {result}")
```

Result:

```
Result of execution of DevVarLongArray command = [array([1, 2, 3], dtype=int32), ['Hello', 'TangoTest device']]
```

## Work with Groups

```{eval-rst}
.. todo::
   write this how to
```

## Handle errors

```{eval-rst}
.. todo::
   write this how to
```

This is just the tip of the iceberg. Check the {class}`~tango.DeviceProxy` for
the complete API.
