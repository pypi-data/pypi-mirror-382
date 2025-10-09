```{eval-rst}
.. currentmodule:: tango
```

(multiprocessing)=

# Multiprocessing/Multithreading

## Using clients with multiprocessing

Since version 9.3.0 PyTango provides {meth}`tango.ApiUtil.cleanup`
which resets CORBA connection.
This static function is needed when you want to use {mod}`tango` with
{mod}`multiprocessing` in your client code.

In the case when both your parent process and your child process create
{class}`~tango.DeviceProxy`, {class}`~tango.Database`, {class}`~tango.Group`,
or/and {class}`~tango.AttributeProxy`
your child process inherits the context from your parent process,
i.e. open file descriptors, the TANGO and the CORBA state.
Sharing the above objects between the processes may cause unpredictable
errors, e.g., *TRANSIENT_CallTimedout*, *unidentifiable C++ exception*.
Therefore, when you start a new process you must reset CORBA connection:

```python
import time
import tango

from multiprocessing import Process


class Worker(Process):

    def run(self):
        # reset CORBA connection
        tango.ApiUtil.cleanup()

        proxy = tango.DeviceProxy("sys/tg_test/1")

        stime = time.time()
        etime = stime
        while etime - stime < 1.:
            try:
                proxy.read_attribute("double_scalar")
            except Exception as e:
                print(str(e))
            etime = time.time()


def run_workers():
    workers = [Worker() for _ in range(6)]
    for wk in workers:
        wk.start()
    for wk in workers:
        wk.join()


db = tango.Database()
dp = tango.DeviceProxy("sys/tg_test/1")

if __name__ == '__main__':
   for i in range(4):
       run_workers()
```

After `cleanup()` all references to {class}`~tango.DeviceProxy`,
{class}`~tango.AttributeProxy`, {class}`~tango.Group` or {class}`~tango.Database` objects
in the current process become invalid
and these objects need to be reconstructed.

## Multithreading - clients and servers

When performing Tango I/O from user-created threads, there can be problems.
This is often more noticeable with event subscription/unsubscription, and
when pushing events, but it could affect any Tango I/O.

A client subscribing and unsubscribing to events via a user thread may see
a crash, a deadlock, or `Event channel is not responding anymore` errors.

A device server pushing events from a user-created thread (including asyncio
callbacks) might see `Not able to acquire serialization (dev, class or process) monitor`
errors, if it is using the default [green mode](#green-modes-overview) {obj}`tango.GreenMode.Synchronous`.

If the device server is using an asynchronous green mode, i.e., {obj}`tango.GreenMode.Gevent` or
{obj}`tango.GreenMode.Asyncio`, then Tango's [device server serialisation](https://tango-controls.readthedocs.io/en/latest/Explanation/threading.html#serialization-model-within-a-device-server)
is disabled - see the [green mode warning](#green-modes-no-sync-warning).  This means you are
likely to see a crash when pushing events from a user thread, especially if an attribute
is read around the same time.  The method described below **WILL NOT** help
for this.  There is no solution (at least with cppTango 9.5.0 and PyTango 9.5.0, and earlier).

As PyTango wraps the cppTango library, we need to consider how cppTango's threads work.
cppTango was originally developed at a time where C++ didn't have standard
threads. All the threads currently created in cppTango are "omni threads",
since this is what the omniORB library is using to create threads and since
this implementation is available for free with omniORB.

In C++, users used to create omni threads in the past so there was no issue.
Since C++11, C++ comes with an implementation of standard threads.
cppTango is currently (version 9.4.1) not directly thread safe when
a user is using C++11 standard threads or threads different than omni threads.
This lack of thread safety includes threads created from Python's
{mod}`threading` module.

In an ideal future cppTango should protect itself, regardless
of what type of threads are used.  In the meantime, we need a work-around.

The work-around when using threads which are not omni threads is to create an
object of the C++ class `omni_thread::ensure_self` in the user thread, just
after the thread creation, and to delete this object only when the thread
has finished its job. This `omni_thread::ensure_self` object provides a
dummy omniORB ID for the thread. This ID is used when accessing thread
locks within cppTango, so the ID must remain the same for the lifetime
of the thread.  Also note that this object MUST be released before the
thread has exited, otherwise omniORB will throw an exception.

A Pythonic way to implement this work-around for multithreaded
applications is available via the {class}`~tango.EnsureOmniThread` class.
It was added in PyTango version 9.3.2.  This class is best used as a
context handler to wrap the target method of the user thread.  An example
is shown below:

```
import tango
from threading import Thread
from time import sleep


def thread_task():
    with tango.EnsureOmniThread():
        eid = dp.subscribe_event(
            "double_scalar", tango.EventType.PERIODIC_EVENT, cb)
        while running:
            print(f"num events stored {len(cb.get_events())}")
            sleep(1)
        dp.unsubscribe_event(eid)


cb = tango.utils.EventCallback()  # print events to stdout
dp = tango.DeviceProxy("sys/tg_test/1")
dp.poll_attribute("double_scalar", 1000)
thread = Thread(target=thread_task)
running = True
thread.start()
sleep(5)
running = False
thread.join()
```

Another way to create threads in Python is the
{class}`concurrent.futures.ThreadPoolExecutor`. The problem with this is that
the API does not provide an easy way for the context handler to cover the
lifetime of the threads, which are created as daemons. There are several options here:

1. PyTango has its own {class}`~tango.utils.PyTangoThreadPoolExecutor` (`tango.utils`).
   It is based on the standard {class}`concurrent.futures.ThreadPoolExecutor`
   and does patching with {class}`~tango.EnsureOmniThread` of the each thread at the startup time.
2. A second option is to at least use the context handler for the functions that are submitted to the
   executor. I.e., `executor.submit(thread_task)`.  This is not guaranteed to work.
