```{eval-rst}
.. currentmodule:: tango
```

# API util

```{eval-rst}
.. autoclass:: ApiUtil
    :members:
```

# Information classes

See also [Event configuration information]

## Attribute

```{eval-rst}
.. autoclass:: AttributeAlarmInfo
    :members:
```

```{eval-rst}
.. autoclass:: AttributeDimension
    :members:
```

```{eval-rst}
.. autoclass:: AttributeInfo
    :members:
```

```{eval-rst}
.. autoclass:: AttributeInfoEx
    :members:
```

see also {class}`AttributeInfo`

```{eval-rst}
.. autoclass:: DeviceAttributeConfig
    :members:
```

## Command

```{eval-rst}
.. autoclass:: DevCommandInfo
   :members:
```

```{eval-rst}
.. autoclass:: CommandInfo
   :members:
```

## Other

```{eval-rst}
.. autoclass:: DeviceInfo
    :members:
```

```{eval-rst}
.. autoclass:: LockerInfo
    :members:
```

```{eval-rst}
.. autoclass:: PollDevice
    :members:

```

# Storage classes

## Attribute: DeviceAttribute

```{eval-rst}
.. autoclass:: DeviceAttribute
    :members:

```

## Command: DeviceData

Device data is the type used internally by Tango to deal with command parameters
and return values. You don't usually need to deal with it, as command_inout
will automatically convert the parameters from any other type and the result
value to another type.

You can still use them, using command_inout_raw to get the result in a DeviceData.

You also may deal with it when reading command history.

```{eval-rst}
.. autoclass:: DeviceData
    :members:

```

# Callback related classes

If you subscribe a callback in a DeviceProxy, it will be run with a parameter.
This parameter depends will be of one of the following classes depending on
the callback type.

```{eval-rst}
.. autoclass:: AttrReadEvent
    :members:
```

```{eval-rst}
.. autoclass:: AttrWrittenEvent
    :members:
```

```{eval-rst}
.. autoclass:: CmdDoneEvent
    :members:

```

# Event related classes

## Event configuration information

```{eval-rst}
.. autoclass:: AttributeEventInfo
    :members:
```

```{eval-rst}
.. autoclass:: ArchiveEventInfo
    :members:
```

```{eval-rst}
.. autoclass:: ChangeEventInfo
    :members:
```

```{eval-rst}
.. autoclass:: PeriodicEventInfo
    :members:
```

## Event subscription structures

```{eval-rst}
.. autoclass:: EventSubMode
    :members:
```

(event-arrived-structures)=

## Event arrived structures

```{eval-rst}
.. autoclass:: EventData
    :members:
```

```{eval-rst}
.. autoclass:: AttrConfEventData
    :members:
```

```{eval-rst}
.. autoclass:: DataReadyEventData
    :members:

```

```{eval-rst}
.. autoclass:: DevIntrChangeEventData
    :members:

```

```{eval-rst}
.. autoclass:: EventReason
    :members:
```

# History classes

```{eval-rst}
.. autoclass:: DeviceAttributeHistory
    :show-inheritance:
    :members:
```

See {class}`DeviceAttribute`.

```{eval-rst}
.. autoclass:: DeviceDataHistory
    :show-inheritance:
    :members:
```

See {class}`DeviceData`.
