```{eval-rst}
.. currentmodule:: tango
```

(telemetry-howto)=

# OpenTelemetry

## Background

Since version 10.0.0 PyTango provides support for distributed tracing and logging via the [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/) framework.
You can read all about the concepts on their website.

You will need a collector to receive the traces and/or logs from your application.  This could either be one running
locally, or on a remote server.  For configuration, the important thing is the collector's endpoint URL and protocol.

E.g., if you run the [Signoz standalone demo](https://signoz.io/docs/install/docker/), there will be a collector
running locally for gRPC and HTTP traffic.  Signoz will also provide a website for viewing the telemetry data.

Alternatively, ask your IT infrastructure team if they already have an OpenTelemetry-compatible backend running, what
the configuration details are for traces and logs, and how to view the data.

:::{warning}
Emitting telemetry from a large number of devices servers and clients can generate a high load on
the backend receiving this data.  There is also small impact on the Tango servers and clients that
use this feature.  Be careful when enabling this feature, and monitor the performance impact.
See the [benchmarks](https://gitlab.com/tango-controls/TangoTickets/-/issues/109).
:::

## How to check if your PyTango installation supports telemetry

As a first step, you need at least version 10.0.0, and both PyTango and cppTango must be
compiled with telemetry support (i.e., the cppTango CMake compiler option `TANGO_USE_TELEMETRY` was enabled):

```console
$ python -c "import tango; print(tango.__version__)"
10.0.0

$ python -c "import tango; print(tango.constants.TELEMETRY_SUPPORTED)"
True
```

See the [PyTango news](#pytango-news) page for which versions of PyTango are packaged
with telemetry support compiled in.

The global enable for OpenTelemetry in Tango is provided by the environment variable `TANGO_TELEMETRY_ENABLE`.
It must be set to `on`, to enable telemetry.

Next, you need the OpenTelemetry Python dependencies installed.  You can see if these are
installed by simply importing the PyTango library with the environment variable enabled.

```console
$ TANGO_TELEMETRY_ENABLE=on python -c "import tango"
```

If there are no warnings, great!  Otherwise you may see a warning like:

```console
$ TANGO_TELEMETRY_ENABLE=on python -c "import tango"
/path/to/python/lib/python3.10/site-packages/tango/utils.py:2427: PyTangoUserWarning:
OpenTelemetry packages not available:
...
```

Install the packages you need.

## How to run a device server that emits telemetry

There are a number of environment variables related to telemetry.  You can read more about them
on this [issue](https://gitlab.com/tango-controls/tango-doc/-/issues/403) (pending a documentation update).

Assuming you have a traces collector using the HTTPS protocol
listening at URL `https://traces.my-institute.org:4319/v1/traces`,
and a logs collector, also using HTTPS, at URL `https://logs.my-institute.org:443/otlp/v1/logs`,
you can set your environment up as follows:

```console
$ export TANGO_TELEMETRY_ENABLE=on
$ export TANGO_TELEMETRY_TRACES_EXPORTER=http
$ export TANGO_TELEMETRY_TRACES_ENDPOINT=https://traces.my-institute.org:4319/v1/traces
$ export TANGO_TELEMETRY_LOGS_EXPORTER=http
$ export TANGO_TELEMETRY_LOGS_ENDPOINT=https://logs.my-institute.org:443/otlp/v1/logs
```

And then launch your application, as normal.

```console
$ python MySuperDS.py instance
```

Another example is using a local collector, with the gRPC protocol:

```console
$ export TANGO_TELEMETRY_ENABLE=on
$ export TANGO_TELEMETRY_TRACES_EXPORTER=grpc
$ export TANGO_TELEMETRY_TRACES_ENDPOINT=grpc://localhost:4317
$ export TANGO_TELEMETRY_LOGS_EXPORTER=grpc
$ export TANGO_TELEMETRY_LOGS_ENDPOINT=grpc://localhost:4317
```

For Tango, when using the gRPC protocol, the URLs must start with `grpc://`, even though your backend might
suggest an `http://` endpoint for the gRPC traffic.

If you want to emit traces, but disable logging via the telemetry backend, this can be done by setting
the exporter to `none`.  This may be useful if your logs are handled by a different system, or your
telemetry backend doesn't support logs.  This can be done as follows:

```console
$ export TANGO_TELEMETRY_LOGS_EXPORTER=none
```

:::{note}
The environment variables can be set in a configuration file, similar
to TANGO_HOST.
See the [reference documentation](https://tango-controls.readthedocs.io/en/latest/Reference/reference.html#environment-variables).
:::

## How to run a client that emits telemetry

The environment variables mentioned above also apply to clients.  Although clients won't emit logs
to the Tango Logging System.  Simply using the client classes, {class}`~tango.DeviceProxy`,
{class}`~tango.AttributeProxy`, {class}`~tango.Group`, and {class}`~tango.Database`, in such an
environment will emit telemetry.

The tracer instance ({class}`opentelemetry.trace.Tracer`) used for client requests depends on the context.
If it is within a device method for an attribute, command, device initialisation or shutdown, then
the device's tracer is used.  For all other cases the client tracer (singleton) is used.

By default, the OpenTelemetry service name associated with client traces from PyTango is
`pytango.client`.  This is very generic, so it is useful to customise this for your own application.
This can be done by setting the environment variable `PYTANGO_TELEMETRY_CLIENT_SERVICE_NAME` to
the string you prefer.  This must be done before the client is used for the first time.

It could be set programmatically, if the actual environment should be ignored:

```python
import os
import tango

if __name__ == "__main__":
    os.environ["PYTANGO_TELEMETRY_CLIENT_SERVICE_NAME"] = "my.client"
    dp = tango.DeviceProxy("sys/tg_test/1")
    dp.ping()
```

## How to add process information to the telemetry traces

The OpenTelemetry Python library has many
[environmental variables](https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html)
for configuration.
One of them (at least at version 1.25.0) allows additional information about the process to be added
to each trace.  This is done by setting the environment variable `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS=process`.

Note that cppTango uses the C++ OpenTelemetry library, which has different behaviour and configuration.

## How to add custom information to device traces

Devices can be customised in two different ways.  Firstly, common information can be added
to all traces.  Secondly, specific information can be added in custom spans when performing tasks
within the device.

### Adding common information to all traces

To add generic resource information, the creation of tracer provider,
{meth}`~tango.server.Device.create_telemetry_tracer_provider`, can be overridden.
This method is called when the device is being initialised, but before `init_device`.

```python
from opentelemetry.trace import TracerProvider
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT
from tango.utils import get_telemetry_tracer_provider_factory


class Example(Device):
    def create_telemetry_tracer_provider(
        self, class_name, device_name
    ) -> TracerProvider:
        tracer_provider_factory = get_telemetry_tracer_provider_factory()
        extra_resource_attributes = {DEPLOYMENT_ENVIRONMENT: "production"}
        return tracer_provider_factory(
            class_name, device_name, extra_resource_attributes
        )
```

Even more customisation is possible by overriding the device's {meth}`~tango.server.Device.create_telemetry_tracer`
method.  This method is also called when the device is being initialised, but after the tracer provider has been
created.

For more extreme cases, the factory used for all device and client tracers can be changed using
{func}`~tango.utils.set_telemetry_tracer_provider_factory`.

### Adding specific information to a span

Each device has its own instance of an {class}`opentelemetry.trace.Tracer`.  This tracer associates the
device's spans with the device's name, and its Tango device class.  The tracer instance can be
accessed at runtime using {meth}`~tango.server.Device.get_telemetry_tracer`.

For example, a partial implementation of a device is shown below with a command handler that creates a custom
span. This span automatically inherits the trace context of the caller.  When creating the span, it adds
the configuration string as an attribute.  Note that only a few simple types are allowed as attribute values
(see {class}`opentelemetry.utils.types.Attributes`).  The example also emits an event during the span.

```python
import json
from tango.server import Device, command


class Example(Device):

   @command
   def Configure(self, configuration_json: str) -> None:
       device_tracer = self.get_telemetry_tracer()
       with device_tracer.start_as_current_span(
           "manager.configure", attributes={"configuration": configuration_json}
       ) as span:
           span.add_event("configuration requested")
           configuration = json.loads(configuration_json)
           self._comms_library.configure(configuration)
```

It is not necessary to create a new span within a command handler or attribute read/write method, as
PyTango has already created a span automatically. This span could be accessed as follows:

```python
import json
from opentelemetry import trace as trace_api
from tango.server import Device, command


class Example(Device):

    @command
    def Configure(self, configuration_json: str) -> None:
        span = trace_api.get_current_span()
        span.set_attribute("configuration", configuration_json)
        span.add_event("configuration requested")
        configuration = json.loads(configuration_json)
        self._comms_library.configure(configuration)
```

## How to manually instrument your own application

Device servers and clients are automatically instrumented, so that they emit spans for
the basic operations.  However, your custom devices and applications that build on Tango can
benefit from additional context.  Manual instrumentation is well described in the
[OpenTelemetry instrumentation docs](https://opentelemetry.io/docs/languages/python/instrumentation/).

You can create your own custom tracer for your application.  It is convenient to use the factory function from
PyTango, so that you make use of the same environment variables that Tango is using to configure the tracer
end point.

```python
from opentelemetry import trace as trace_api
from tango.utils import get_telemetry_tracer_provider_factory

tracer_provider_factory = get_telemetry_tracer_provider_factory()
tracer_provider = tracer_provider_factory("my.app")
tracer = trace_api.get_tracer(
    instrumenting_module_name="my.app.reader",
    instrumenting_library_version=my_app.__version__,
    tracer_provider=tracer_provider,
)
```

Then you can create spans in any interesting functions.  Consider a web application
that is providing a way to read Tango device attribute values.  It may be useful to
add details about the requesting client to the span.

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/read_attr_value/{device_name}/{attr_name}")
def read_attr_value(device_name: str, attr_name: str, request: Request):
    with tracer.start_as_current_span(
           "my-web-proxy.read_attr_value",
           attributes={"client.address": request.client.host}
       ):
           proxy = tango.DeviceProxy(device_name)
           value = proxy.read_attribute(attr_name).value
           return {"value": value}
```

:::{note}
Creating a span around a very long running task is not recommended.  The
span is only emitted on completion.  Users viewing traces related to such
a span will not get a complete picture until it completes.  Also, having
a huge number of child spans (100s to 1000s) will be problematic
to view in typical web UIs.
:::

The Tango logs that go to OpenTelemetry are emitted by cppTango.  PyTango doesn't expose
a way to use the logging directly for client-only applications.  Devices already have a standard way
to emit logs.  If you want your application's logs to be emitted from Python, this is still an experimental
feature in OpenTelemetry Python (as at v1.26.0).
See the [logs examples](https://github.com/open-telemetry/opentelemetry-python/tree/v1.26.0/docs/examples/logs).

(telemetry-howto-hide-error-messages)=

## How to hide error messages when traces cannot be sent

The traces are sent to the backend in the background.  This might fail if the host is unreachable or too busy.
If that happens, the error messages from the OpenTelemtry SDK are printed to stdout.  For example:

```
Exception while exporting Span batch.
Traceback (most recent call last):
  ...
[Error] File: /Users/runner/miniforge3/conda-bld/opentelemetry-sdk_1733208709442/work/exporters/otlp/src/otlp_http_exporter.cc:145 [OTLP TRACE HTTP Exporter] ERROR: Export 6 trace span(s) error: 1
```

For an end-user these messages might be confusing, or a nuisance.  It is possible to hide them by changing the
OpenTelemetry SDK's log level.  PyTango provides an environment variable, `PYTANGO_TELEMETRY_SDK_LOG_LEVEL`,
to do this.  Set the value to `fatal` before starting your application to hide the error logs.

The standard Python logging levels are all options: `critical`, `fatal`, `error`, `warning`, `info`, `debug`, `notset`.

The name of the [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python) logger used for
this may change in future, so there is a second environment variable, `PYTANGO_TELEMETRY_SDK_LOGGER_NAMES`, which
can be set to a comma-seperated list of logger names.  Defaults are used if the environment variable is empty or
not set.

(As at version 1.35.0, opentelemetry-python
[does not support](https://github.com/open-telemetry/opentelemetry-python/issues/1059) its own `OTEL_LOG_LEVEL`
environment variable).

## How to reduce the number of traces being stored

Storing all traces from all Tango devices in your facility is probably not feasible.

One option is to only enable telemetry after a problem has occurred, and further
debugging is planned.  Unfortunately, it means that rare errors typically won't be captured.
Currently (as at v10.0.0), the device server or client process has to be restarted with the
correct environment variables to enable telemetry.  This is restrictive.
In future, there may be a DeviceProxy API to change this at run time, similar to how the
logging severity and targets can be changed.

Another option is to have all devices emitting telemetry, but have the collector apply some filtering
to reduce the number of traces that get stored.
This is the concept of [sampling](https://opentelemetry.io/docs/concepts/sampling/).
You may consider a probabilistic sampler, or a [tail sampler](https://opentelemetry.io/blog/2022/tail-sampling/),
or many of the other contributed samplers.

## Further examples

The
[prototyping.py](https://gitlab.com/tango-controls/pytango/-/blob/develop/examples/telemetry/prototyping.py)
file in the source repository has some further examples, including creating a custom tracer, passing the
trace context to a different thread, enabling and disabling telemetry at runtime.  Note that while the
interface exists for enabling and disabling, it doesn't work correctly in PyTango 10.0.0.
