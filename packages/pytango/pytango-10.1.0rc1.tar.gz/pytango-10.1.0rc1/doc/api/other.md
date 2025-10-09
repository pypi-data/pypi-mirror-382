```{eval-rst}
.. currentmodule:: tango
```

# Enumerations & other classes

## Enumerations

```{eval-rst}
.. autoclass:: tango.LockerLanguage
```

```{eval-rst}
.. autoclass:: tango.CmdArgType
```

```{eval-rst}
.. autoclass:: tango.MessBoxType
```

```{eval-rst}
.. autoclass:: tango.PollObjType
```

```{eval-rst}
.. autoclass:: tango.PollCmdCode
```

```{eval-rst}
.. autoclass:: tango..SerialModel
```

```{eval-rst}
.. autoclass:: tango.AttReqType
```

```{eval-rst}
.. autoclass:: tango.LockCmdCode
```

```{eval-rst}
.. autoclass:: tango.LogLevel
```

```{eval-rst}
.. autoclass:: tango.LogTarget
```

```{eval-rst}
.. autoclass:: tango.EventType
```

```{eval-rst}
.. autoclass:: tango.KeepAliveCmdCode
```

```{eval-rst}
.. autoclass:: tango.AccessControlType
```

```{eval-rst}
.. autoclass:: tango.asyn_req_type
```

```{eval-rst}
.. autoclass:: tango.cb_sub_model
```

```{eval-rst}
.. autoclass:: tango.AttrQuality
```

```{eval-rst}
.. autoclass:: tango.AttrWriteType
```

```{eval-rst}
.. autoclass:: tango.AttrDataFormat
```

```{eval-rst}
.. autoclass:: tango.DevSource
```

```{eval-rst}
.. autoclass:: tango.ErrSeverity
```

```{eval-rst}
.. autoclass:: tango.DevState
```

```{eval-rst}
.. autoclass:: tango.DispLevel
```

```{eval-rst}
.. autoclass:: tango.GreenMode

```

## Other classes

```{eval-rst}
.. autoclass:: tango.Release
    :members:
```

```{eval-rst}
.. autoclass:: tango.TimeVal
    :members:

    .. rubric:: Constructors

    .. py:method:: __init__(self)
        :no-index:

        Default constructor; all fields set to 0.

    .. py:method:: __init__(self, tv_sec: int, tv_usec: int, tv_nsec: int)
        :no-index:

        Create a TimeVal by specifying all three members.

    .. py:method:: __init__(self, time: float)
        :no-index:

        Create a TimeVal from time in seconds since epoch (e.g. time.time()).

    .. py:method:: __init__(self, time: datetime.datetime)
        :no-index:

        Create a TimeVal from time in datetime.datetime format (e.g. datetime.datetime.now()).
```

```{eval-rst}
.. autoclass:: tango.TimedAttrData
    :members:
```

```{eval-rst}
.. autoclass:: tango.TimedCmdData
    :members:
```
