```{eval-rst}
.. currentmodule:: tango
```

(tutorial-guide)=

# Tutorial

The following sections will guide you through the first steps on using PyTango.

```{toctree}
:maxdepth: 2

Clients <tutorial/clients>
Servers <tutorial/servers>
Database <tutorial/database>
Logging <tutorial/logging>
Asynchronous (green modes) <tutorial/green_modes>
ITango <tutorial/itango>
```

But before you begin there are some fundamental TANGO concepts you should be aware of.

## Fundamental TANGO concepts

Tango consists basically of a set of *devices* running somewhere on the network.

A device is identified by a unique case insensitive name in the format
*\<domain>/\<family>/\<member>*. Examples: `LAB-01/PowerSupply/01`,
`ID21/OpticsHutch/energy`.

Each device has a series of *attributes*, *properties* and *commands*.

An attribute is identified by a name in a device. It has a value that can
be read. Some attributes can also be changed (read-write attributes). Each
attribute has a well known, fixed data type.

A property is identified by a name in a device. Usually, devices properties are
used to provide a way to configure a device.

A command is also identified by a name. A command may or not receive a parameter
and may or not return a value when it is executed.

Any device has **at least** a *State* and *Status* attributes and *State*,
*Status* and *Init* commands. Reading the *State* or *Status* attributes has
the same effect as executing the *State* or *Status* commands.

Each device as an associated *TANGO Class*. Most of the times the TANGO class
has the same name as the object oriented programming class which implements it
but that is not mandatory.

TANGO devices *live* inside a operating system process called *TANGO Device Server*.
This server acts as a container of devices. A device server can host multiple
devices of multiple TANGO classes. Devices are, therefore, only accessible when
the corresponding TANGO Device Server is running.

A special TANGO device server called the *TANGO Database Server* will act as
a naming service between TANGO servers and clients. This server has a known
address where it can be reached. The machines that run TANGO Device Servers
and/or TANGO clients, should export an environment variable called
{envvar}`TANGO_HOST` that points to the TANGO Database server address. Example:
`TANGO_HOST=homer.lab.eu:10000`

## Check the default TANGO host

Before you start you might check your default TANGO host
It is defined using the environment variable {envvar}`TANGO_HOST` or in a `tangorc` file
(see [Tango environment variables](https://tango-controls.readthedocs.io/en/latest/Reference/reference.html#environment-variables)
for complete information)

To check simple do:

```
>>> import tango
>>> tango.ApiUtil.get_env_var("TANGO_HOST")
'homer.simpson.com:10000'
```

## Check TANGO version

PyTango is under continuous development, and some features are unavailable in earlier releases.
To be sure, specific features are available, you should check your installation.

There are two library versions you might be interested in checking:
The PyTango version:

```
>>> import tango
>>> tango.__version__
'9.5.0'
>>> tango.__version_info__
(9, 5, 0)
```

and the Tango C++ library version that PyTango was compiled with:

```
>>> import tango
>>> tango.constants.TgLibVers
'9.5.0'
```
