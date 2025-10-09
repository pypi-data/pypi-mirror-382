(to9.5-short-name-test-access)=

# Short-name access to TestContext devices

## Description

When a device server is launched via the {class}`~tango.test_context.DeviceTestContext` or
{class}`~tango.test_context.MultiDeviceTestContext`, it is run without a Tango database.  This means that access to
any of its devices must be done via a fully-qualified
[Tango Resource Locator](https://tango-controls.readthedocs.io/projects/rfc/en/latest/16/TangoResourceLocator.html)
(FQTRL).  I.e., we need something like `tango://172.17.0.3:48493/test/device/1#dbase=no`, instead of just the
short name: `test/device/1`.  Requiring the FQTRL is inconvenient.

A simple example:

```
from tango import AttrWriteType, DeviceProxy
from tango.server import Device, attribute
from tango.test_context import MultiDeviceTestContext

class Device1(Device):
    _attr1 = 100

    @attribute(access=AttrWriteType.READ_WRITE)
    def attr1(self):
        return self._attr1

    def write_attr1(self, value):
        self._attr1 = value

def test_multi_short_name_device_proxy_access_without_tango_db():
    devices_info = ({"class": Device1, "devices": [{"name": "test/device1/1"}]},)

    with MultiDeviceTestContext(devices_info):
        proxy1 = tango.DeviceProxy("test/device1/1")
        assert proxy1.name() == "test/device1/1"
        assert proxy1.attr1 == 100
```

Previously, we would have had to use a call like `context.get_device_access("test/device1/1")` to get the
FQTRL, before instantiating a {class}`~tango.DeviceProxy`.

A more detailed [example](https://gitlab.com/tango-controls/pytango/-/blob/develop/examples/multidevicetestcontext/test_integration.py)
is available.

## Limitations

- Group patterns (`*` wildcard) are not supported.
- Group device names will be FQTRLs, rather than the short name that was originally supplied.
- Launching two TestContexts in the same process will not work correctly without FQTRLs. The TestContext that is
  started second will overwrite the global variable set by the first.

## Implementation details

From PyTango 9.5.0, the test device server's FQTRL is stored in in a global variable while the TextContext is active.
Then, in order to make device access with short names transparent, the {class}`~tango.DeviceProxy`,
{class}`~tango.AttributeProxy` and {class}`~tango.Group` classes have been modified to take this global variable
into account.  If it is set, and a short (i.e., unresolved) TRL is used for the proxy constructor or group add method,
then the name is rewritten to a fully qualified (resolved) TRL.  If this FQTRL is not accessible, the short name is
tried again (except for `Group`) - this allows real devices to be accessed via short TRLs, if necessary.

There should not be a noticeable performance degradation for this outside of test environments. It it just a single
variable lookup per proxy constructor or group add invocation.

This new TestContext functionality is enabled by default.  It can be disabled by setting the
`enable_test_context_tango_host_override` attribute to `False` before starting the TestContext.

Example:

```
def test_multi_short_name_access_fails_if_override_disabled():
    devices_info = ({"class": Device1, "devices": [{"name": "test/device1/a"}]},)

    context = MultiDeviceTestContext(devices_info)
    context.enable_test_context_tango_host_override = False
    context.start()
    try:
        with pytest.raises(DevFailed):
            _ = tango.DeviceProxy("test/device1/a")
    finally:
        context.stop()
```

## Port detection and pre_init_callback

As before, if the user doesn't specify a port number when instantiating the TestContext, omniORB will select
an ephemeral port automatically when the device server starts.  We need to determine this port number before
any device calls its `init_device` method, in case it want to create clients ({class}`~tango.DeviceProxy`, etc.)
at that early stage.

The solution to this is the addition of a `pre_init_callback` in the {func}`~tango.server.run` and
{meth}`~tango.server.Device.run_server` methods.  This is called after `Util.init()` (when omniORB has started
and bound to a TCP port for the GIOP traffic, and the event system has bound two ports for ZeroMQ traffic),
but before `Util.server_init()` (which initialises all classes in the device server).

During `pre_init_callback` the TestContext probes the process's open ports to determine the GIOP port number.
We didn't find a way to determine the port number without probing each port.
