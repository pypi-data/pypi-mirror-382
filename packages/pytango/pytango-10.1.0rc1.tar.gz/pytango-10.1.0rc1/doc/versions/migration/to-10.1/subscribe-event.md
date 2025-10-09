(to10.1-subscribe-event)=

# Changes to event subscription

(to10.1-subscribe-event-sub-mode)=

## New asynchronous subscription and `sub_mode` parameter

cppTango 10.1.0 added a new set of options for subscribing to events.  Historically, the
{meth}`tango.DeviceProxy.subscribe_event` and {meth}`tango.AttributeProxy.subscribe_event` calls were
synchronous, and included a read of the attribute being subscribed to.  In other words, the client had to
wait for both the subscription and the attribute read before continuing.  This could delay the client significantly
when subscribing to a large number of attributes, especially if any of those attributes were slow to read.  cppTango
has now decoupled the subscription and reading, providing a variety of new options.

The client's `subscribe_event` method has a new parameter, `sub_mode`, which is an enumeration of
{class}`~tango.EventSubMode`. The default value is `EventSubMode.SyncRead`, which is the standard behaviour
we had in previous versions of Tango.  If you want the client to be able to continue sooner after subscription,
the `EventSubMode.AsyncRead` is better, however, you have no guarantee when the callback with the initial value
will happen.  It should be "soon", if the device is running and the attribute exists.

## Event callback changes

The event data objects received on event callbacks (or when fetching them from the event queue) now have a new field,
`event_reason`,  of type {class}`~tango.EventReason`.  See the [event arrived structures](#event-arrived-structures).

This field may be of interest for the `EventSubMode.Async` subscription mode.  After initial subscription to an
attribute, we receive an event of type `EventData`, with `EventReason.SubSuccess`, but since we aren't doing a
read, there won't be a value in the `attr_value` field (it will be `None`).

(to10.1-subscribe-event-deprecation)=

## Deprecation of `filters` and `stateless` parameters

The `filters` parameter for {meth}`tango.DeviceProxy.subscribe_event` and {meth}`tango.AttributeProxy.subscribe_event`
is only useful with old Tango device servers with the notifd event system (rather than ZeroMQ). Support for this
is scheduled for removal in Tango 11.  In most clients that are still providing this parameter, they set it to an empty
list, `[]`, since it isn't applicable to the ZeroMQ event system.

The behaviour of `stateless=True` is now superseded by providing the `sub_mode=EventSubMode.Stateless` parameter
instead.

The plan is to remove both of these parameters from PyTango in future. The exact version hasn't been decided, but
the earliest is PyTango 11.0.0.  PyTango will emit deprecation warnings if you use these old parameters.

Change code like this:

```python
dp = DeviceProxy("sys/tg_test/1")
callback = tango.utils.EventCallback()

eid = dp.subscribe_event("double_scalar", EventType.CHANGE_EVENT, callback, [], True)
```

To code like this:

```python
...
eid = dp.subscribe_event("double_scalar", EventType.CHANGE_EVENT, callback, sub_mode=EventSubMode.Stateless)
```

Or, if you don't need the callback to be called immediately as part of the subscription, it is better
to use the new asynchronous-read subscription mode:

```python
...
eid = dp.subscribe_event("double_scalar", EventType.CHANGE_EVENT, callback, sub_mode=EventSubMode.AsyncRead)
```

If your old code is setting `stateless` to `False`, then the arguments can just be removed.

```python
...
eid = dp.subscribe_event("double_scalar", EventType.CHANGE_EVENT, callback, [], False)
```

Changes to:

```python
...
eid = dp.subscribe_event("double_scalar", EventType.CHANGE_EVENT, callback)
```
