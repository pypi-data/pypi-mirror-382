```{eval-rst}
.. currentmodule:: tango
```

(logging)=

# Server logging in Python

This chapter instructs you on how to use the tango logging API (log4tango) to
create tango log messages on your device server.

The logging system explained here is the Tango Logging Service (TLS). For
detailed information on how this logging system works please check:

> - [Usage](https://tango-controls.readthedocs.io/en/latest/Explanation/device-server-model.html#the-tango-logging-service)
> - [Property reference](https://tango-controls.readthedocs.io/en/latest/Reference/reference.html#the-device-logging)

The easiest way to start seeing log messages on your device server console is
by starting it with the verbose option. Example:

```
python PyDsExp.py PyDs1 -v4
```

This activates the console tango logging target and filters messages with
importance level DEBUG or more.
The links above provided detailed information on how to configure log levels
and log targets. In this document we will focus on how to write log messages on
your device server.

## Basic logging

The most basic way to write a log message on your device is to use the
{class}`~tango.server.Device` logging related methods:

> - {meth}`~tango.server.Device.debug_stream`
> - {meth}`~tango.server.Device.info_stream`
> - {meth}`~tango.server.Device.warn_stream`
> - {meth}`~tango.server.Device.error_stream`
> - {meth}`~tango.server.Device.fatal_stream`

Example:

```
def read_voltage(self):
    self.info_stream("read voltage attribute")
    # ...
    return voltage_value
```

This will print a message like:

```
1282206864 [-1215867200] INFO test/power_supply/1 read voltage attribute
```

every time a client asks to read the *voltage* attribute value.

The logging methods support argument list feature (since PyTango 8.1). Example:

```
def read_voltage(self):
    self.info_stream("read_voltage(%s, %d)", self.host, self.port)
    # ...
    return voltage_value
```

## Logging with print statement

*This feature is only possible since PyTango 7.1.3*

It is possible to use the print statement to log messages into the tango logging
system. This is achieved by using the python's print extend form sometimes
refered to as *print chevron*.

Same example as above, but now using *print chevron*:

```
def read_voltage(self, the_att):
    print >>self.log_info, "read voltage attribute"
    # ...
    return voltage_value
```

Or plain print:

```
def read_Long_attr(self, the_att):
    print("read voltage attribute", file=self.log_info)
    # ...
    return voltage_value
```

## Logging with decorators

*This feature is only possible since PyTango 7.1.3*

PyTango provides a set of decorators that place automatic log messages when
you enter and when you leave a python method. For example:

```
@tango.DebugIt()
def read_Long_attr(self, the_att):
    the_att.set_value(self.attr_long)
```

will generate a pair of log messages each time a client asks for the 'Long_attr'
value. Your output would look something like:

```
1282208997 [-1215965504] DEBUG test/pydsexp/1 -> read_Long_attr()
1282208997 [-1215965504] DEBUG test/pydsexp/1 <- read_Long_attr()
```

Decorators exist for all tango log levels:
: - {class}`tango.DebugIt`
  - {class}`tango.InfoIt`
  - {class}`tango.WarnIt`
  - {class}`tango.ErrorIt`
  - {class}`tango.FatalIt`

The decorators receive three optional arguments:
: - show_args - shows method arguments in log message (defaults to False)
  - show_kwargs shows keyword method arguments in log message (defaults to False)
  - show_ret - shows return value in log message (defaults to False)

Example:

```
@tango.DebugIt(show_args=True, show_ret=True)
def IOLong(self, in_data):
    return in_data * 2
```

will output something like:

```
1282221947 [-1261438096] DEBUG test/pydsexp/1 -> IOLong(23)
1282221947 [-1261438096] DEBUG test/pydsexp/1 46 <- IOLong()
```
