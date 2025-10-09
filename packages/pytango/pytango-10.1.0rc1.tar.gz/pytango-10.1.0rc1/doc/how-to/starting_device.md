```{eval-rst}
.. currentmodule:: tango
```

```{highlight} python
:linenothreshold: 4
```

(advanced-starting-device)=

# Starting/creating/deleting devices

## Multiple device classes (Python and C++) in a server

Within the same python interpreter, it is possible to mix several Tango classes.
Let's say two of your colleagues programmed two separate Tango classes in two
separated python files: A {class}`PLC` class in a {file}`PLC.py`:

```
# PLC.py

from tango.server import Device

class PLC(Device):

    # bla, bla my PLC code

if __name__ == "__main__":
    PLC.run_server()
```

... and a {class}`IRMirror` in a {file}`IRMirror.py`:

```
# IRMirror.py

from tango.server import Device

class IRMirror(Device):

    # bla, bla my IRMirror code

if __name__ == "__main__":
    IRMirror.run_server()
```

You want to create a Tango server called `PLCMirror` that is able to contain
devices from both PLC and IRMirror classes. All you have to do is write
a {file}`PLCMirror.py` containing the code:

```
# PLCMirror.py

from tango.server import run
from PLC import PLC
from IRMirror import IRMirror

run([PLC, IRMirror])
```

It is also possible to add C++ Tango class in a Python device server as soon as:
: 1. The Tango class is in a shared library
  2. It exist a C function to create the Tango class
  3. The C++ Tango class is linked against the same `libtango.so` object as PyTango
     (i.e., **cannot be used with binary wheels from PyPI**, but can with conda-forge or a custom build).

For a Tango class called MyTgClass, the shared library has to be called
MyTgClass.so and has to be in a directory listed in the LD_LIBRARY_PATH
environment variable. The C function creating the Tango class has to be called
\_create_MyTgClass_class() and has to take one parameter of type "char \*" which
is the Tango class name. Here is an example of the main function of the same
device server than before but with one C++ Tango class called SerialLine:

```
import tango
import sys

if __name__ == '__main__':
    util = tango.Util(sys.argv)
    util.add_class('SerialLine', 'SerialLine', language="c++")
    util.add_class(PLCClass, PLC, 'PLC')
    util.add_class(IRMirrorClass, IRMirror, 'IRMirror')

    U = tango.Util.instance()
    U.server_init()
    U.server_run()
```

```{eval-rst}

:Line 6: The C++ class is registered in the device server
:Line 7 and 8: The two Python classes are registered in the device server
```

## Create/Delete devices dynamically

*This feature is only possible since PyTango 7.1.2*

Starting from PyTango 7.1.2 it is possible to create devices in a device server
"en caliente". This means that you can create a command in your "management device"
of a device server that creates devices of (possibly) several other tango classes.
There are two ways to create a new device which are described below.

Tango imposes a limitation: the tango class(es) of the device(s) that is(are)
to be created must have been registered before the server starts.
If you use the high level API, the tango class(es) must be listed in the call
to {func}`~tango.server.run`. If you use the lower level server API, it must
be done using individual calls to {meth}`~tango.Util.add_class`.

### Dynamic device from a known tango class name

If you know the tango class name but you don't have access to the {class}`tango.DeviceClass`
(or you are too lazy to search how to get it ;-) the way to do it is call
{meth}`~tango.Util.create_device` / {meth}`~tango.Util.delete_device`.
Here is an example of implementing a tango command on one of your devices that
creates a device of some arbitrary class (the example assumes the tango commands
'CreateDevice' and 'DeleteDevice' receive a parameter of type DevVarStringArray
with two strings. No error processing was done on the code for simplicity sake):

```
from tango import Util
from tango.server import Device, command

class MyDevice(Device):

    @command(dtype_in=[str])
    def CreateDevice(self, pars):
        klass_name, dev_name = pars
        util = Util.instance()
        util.create_device(klass_name, dev_name, alias=None, cb=None)

    @command(dtype_in=[str])
    def DeleteDevice(self, pars):
        klass_name, dev_name = pars
        util = Util.instance()
        util.delete_device(klass_name, dev_name)
```

An optional callback can be registered that will be executed after the device is
registed in the tango database but before the actual device object is created
and its init_device method is called. It can be used, for example, to initialize
some device properties.

### Dynamic device from a known tango class

If you already have access to the {class}`~tango.DeviceClass` object that
corresponds to the tango class of the device to be created you can call directly
the {meth}`~tango.DeviceClass.create_device` / {meth}`~tango.DeviceClass.delete_device`.
For example, if you wish to create a clone of your device, you can create a
tango command called *Clone*:

```
class MyDevice(tango.Device):

    def fill_new_device_properties(self, dev_name):
        prop_names = db.get_device_property_list(self.get_name(), "*")
        prop_values = db.get_device_property(self.get_name(), prop_names.value_string)
        db.put_device_property(dev_name, prop_values)

        # do the same for attributes...
        ...

    def Clone(self, dev_name):
        klass = self.get_device_class()
        klass.create_device(dev_name, alias=None, cb=self.fill_new_device_properties)

    def DeleteSibling(self, dev_name):
        klass = self.get_device_class()
        klass.delete_device(dev_name)
```

Note that the cb parameter is optional. In the example it is given for
demonstration purposes only.
