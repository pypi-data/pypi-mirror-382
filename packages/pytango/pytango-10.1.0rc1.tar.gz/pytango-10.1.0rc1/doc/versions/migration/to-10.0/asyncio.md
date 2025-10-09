(to10.0-asyncio)=

# Changes to Asyncio green mode servers

(to10.0-asyncio-deprecation)=

## Deprecation of synchronous methods in Asyncio servers

Historically, the implementation of [green modes](#green-modes-overview) utilized the basic
synchronous PyTango code and tried to convert to asynchronous code (coroutines) on the fly. The main advantage
of such an implementation was simpler code maintenance: all changes we make automatically applied to all green modes.

However, with [Asyncio](https://docs.python.org/3/library/asyncio.html) mode there is a major problem:
to convert all original synchronous methods we used Python's `asyncio.coroutine` function,
which was the first iteration to make coroutines by {mod}`asyncio`. Unfortunately, it  was deprecated in Python 3.8
and finally removed from Python 3.11.

As the temporary solution we copied the `asyncio.coroutine` code to PyTango.
But then the cleaning process of the {mod}`asyncio` library continued and for Python 3.12 we
had to copy `run_coroutine_threadsafe` and modify it to be able to work with such legacy generator-based coroutines.

Since there is no guarantee that our copied methods will be compatible
with new versions of {mod}`asyncio` we decided to change how the
[Asyncio](https://docs.python.org/3/library/asyncio.html) green mode of PyTango is implemented.

:::{note}
Starting from PyTango 10.0.0 all Asyncio servers should be written with coroutine functions.
:::

In other words, use `async def` when defining methods for attribute access (read/write/is allowed),
for command access (command/is allowed), and for the "special" methods:

> - `init_device`
> - `delete_device`
> - `dev_state`
> - `dev_status`
> - `read_attr_hardware`
> - `always_executed_hook`

The base {class}`tango.server.Device` class was also modified to use `async def`, so instead of
doing `super().<method name>()` calls you **must** do `await super().<method name>()`.

For example, change code like this:

```
class MyDevice(Device):
    green_mode = tango.GreenMode.Asyncio

    def init_device(self):
        super().init_device()
        self._attr = 1.5

    @attribute
    def slow_attr(self) -> float:
        time.sleep(0.5)
        return self._attr
```

To code like this:

```
class MyDevice(Device):
    green_mode = tango.GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self._attr = 1.5

    @attribute
    async def slow_attr(self) -> float:
        await asyncio.sleep(0.5)
        return self._attr
```

In PyTango 10.0.0 we still preserve option to run legacy servers, with synchronous user functions,
but every time server is started you will receive a {class}`DeprecationWarning`.

(to10.0-asyncio-dyn-attrs)=

## New methods for adding and removing dynamic attributes

There are now coroutine functions for adding and removing attributes. Specifically,
{meth}`~tango.server.Device.async_add_attribute` and {meth}`~tango.server.Device.async_remove_attribute`.
Use these instead of the synchronous versions, as they can prevent deadlocks in certain cases
when clients are accessing the device during attribute creation/removal.

For example, change code like this:

```
class MyDevice(Device):
    green_mode = tango.GreenMode.Asyncio
    attr_value = None

    @command
    async def add_dyn_attr(self):
        attr = attribute(
            name="dyn_attr",
            dtype=int,
            access=AttrWriteType.READ_WRITE,
            fget=self.read_dyn_attr,
            fset=self.write_dyn_attr,
        )
        self.add_attribute(attr)  # bad **********

    @command
    async def remove_dyn_attr(self):
        self.remove_attribute("dyn_attr")  # bad **********

    async def write_dyn_attr(self, attr):
        self.attr_value = attr.get_write_value()

    async def read_dyn_attr(self, attr):
        return self.attr_value
```

To code like this:

```
class MyDevice(Device):
    green_mode = tango.GreenMode.Asyncio
    attr_value = None

    @command
    async def add_dyn_attr(self):
        attr = attribute(
            name="dyn_attr",
            dtype=int,
            access=AttrWriteType.READ_WRITE,
            fget=self.read_dyn_attr,
            fset=self.write_dyn_attr,
        )
        await self.async_add_attribute(attr)  # good **********


    @command
    async def remove_dyn_attr(self):
        await self.async_remove_attribute("dyn_attr")  # good **********


    async def write_dyn_attr(self, attr):
        self.attr_value = attr.get_write_value()

    async def read_dyn_attr(self, attr):
        return self.attr_value
```

One exception to this rule, is when you are overriding the standard method,
{meth}`~tango.server.Device.initialize_dynamic_attributes`.  That method is
synchronous, so we cannot use the async versions.  Since it is only run at device
creation, we avoid the deadlock as clients cannot yet access the attributes.

Code like this does not need to change:

```
class MyDevice(Device):
    green_mode = tango.GreenMode.Asyncio
    attr_value = None

    def initialize_dynamic_attributes(self):
        attr = attribute(
            name="dyn_attr",
            dtype=int,
            access=AttrWriteType.READ_WRITE,
            fget=self.read_dyn_attr,
            fset=self.write_dyn_attr,
        )
        self.add_attribute(attr)  # OK, in this method

    async def write_dyn_attr(self, attr):
        self.attr_value = attr.get_write_value()

    async def read_dyn_attr(self, attr):
        return self.attr_value
```
