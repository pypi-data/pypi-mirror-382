```{eval-rst}
.. currentmodule:: tango
```

(green-modes-overview)=

# Green mode

```{toctree}
:maxdepth: 1
:hidden: true

green_modes/green_modes_client
green_modes/green_modes_server
```

PyTango supports cooperative green Tango objects. Since version 8.1 two *green*
modes have been added: {obj}`~tango.GreenMode.Futures` and
{obj}`~tango.GreenMode.Gevent`. In version 9.2.0 another one has been
added: {obj}`~tango.GreenMode.Asyncio`.

:::{note}
The preferred mode to use for new projects is {obj}`~tango.GreenMode.Asyncio`.
Support for this mode will take priority over the others.
:::

The {obj}`~tango.GreenMode.Futures` uses the standard python module
{mod}`concurrent.futures`.
The {obj}`~tango.GreenMode.Gevent` mode uses the well known [gevent](https://www.gevent.org) library.
The newest, {obj}`~tango.GreenMode.Asyncio` mode, uses [asyncio](https://docs.python.org/3/library/asyncio.html) - a Python
library for asynchronous programming (it's featured as a part of a standard
Python distribution since version 3.5 of Python; it's available on PyPI for
older ones).

You can set the PyTango green mode at a global level. Set the environment
variable {envvar}`PYTANGO_GREEN_MODE` to either *futures*, *gevent* or *asyncio*
(case-insensitive). If this environment variable is not defined the PyTango
global green mode defaults to *Synchronous*.
