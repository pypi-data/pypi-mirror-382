(to10.0-quality-event)=

# Removal of QUALITY_EVENT

Since the {class}`~tango.EventType.QUALITY_EVENT` was not actually used by cppTango core for a long time, there was
a [corresponding clean-up of leftover code in cppTango](https://gitlab.com/tango-controls/cppTango/-/issues/1260).

Following this, in PyTango v10.0.0 the event type {class}`~tango.EventType.QUALITY_EVENT` and
the `quality_event_subscribed` method from {class}`~tango.Attribute` were removed.

Remove any references to these from your code.
