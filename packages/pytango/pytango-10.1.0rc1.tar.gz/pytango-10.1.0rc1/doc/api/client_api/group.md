# Group

```{eval-rst}
.. currentmodule:: tango

```

% GroupElement is the base class of Group, but is not the base of
% anything else. So, I don't include it in the documentation but just
% add its functions into Group by using :inherited-members:

## Group class

```{eval-rst}
.. autoclass:: tango.Group
    :show-inheritance:
    :inherited-members:
    :members:

```

## GroupReply classes

Group member functions do not return the same as their DeviceProxy counterparts,
but objects that contain them. This is:

> - *write attribute* family returns tango.GroupReplyList
> - *read attribute* family returns tango.GroupAttrReplyList
> - *command inout* family returns tango.GroupCmdReplyList

The Group\*ReplyList objects are just list-like objects containing
{class}`~tango.GroupReply`, {class}`~tango.GroupAttrReply` and
{class}`~GroupCmdReply` elements that will be described now.

Note also that GroupReply is the base of GroupCmdReply and GroupAttrReply.

```{eval-rst}
.. autoclass:: tango.GroupReply
    :members:
```

```{eval-rst}
.. autoclass:: tango.GroupAttrReply
    :show-inheritance:
    :members:
```

```{eval-rst}
.. autoclass:: GroupCmdReply
    :show-inheritance:
    :members:
```
