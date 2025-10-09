# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
# Imports

import time
import sys
import gc
import inspect

from threading import Thread

import pytest
from io import StringIO

from tango import (
    EventType,
    DeviceProxy,
    DevEncoded,
    GreenMode,
    AttrQuality,
    DevFailed,
    EnsureOmniThread,
    is_omni_thread,
    EventSubMode,
    EventReason,
    EventData,
    ExtractAs,
)

from tango import Except
from tango.server import Device
from tango.server import command, attribute
from tango.test_utils import DeviceTestContext, assert_close
from tango.utils import EventCallback, PyTangoUserWarning


MAX_RETRIES = 200
DELAY_PER_RETRY = 0.05

event_results = []


async def async_callback(evt):
    event_callback(evt)


def event_callback(evt):
    if evt.err:
        event_results.append(evt.errors[0].desc)
        assert evt.attr_value is None
    elif hasattr(evt, "ctr"):
        event_results.append(evt.ctr)
    elif hasattr(evt, "attr_value"):
        event_results.append(evt.attr_value.value)
    else:
        event_results.append(evt)


# Test device
class EventDevice(Device):
    _requested_event_type = None
    _base = 0

    def init_device(self):
        self.set_change_event("attr", implemented=True, detect=False)
        # even if set_alarm_event is not necessary after we did set_change_event,
        # we call it to test that function works
        self.set_alarm_event("attr", implemented=True, detect=False)
        self.set_data_ready_event("attr", implemented=True)
        self.set_archive_event("attr", implemented=True, detect=False)

        self.set_change_event("dev_encoded_attr", implemented=True, detect=False)

    @attribute()
    def attr(self) -> int:
        # to avoid sending events at subscription
        if self._requested_event_type is not None:
            self._base += 10
            self._send_events("attr", self._requested_event_type)
        return 0

    @attr.write
    def attr(self, event_type):
        self._base += 10
        self._requested_event_type = event_type
        self._send_events("attr", event_type)

    @attribute(dtype=DevEncoded)
    def dev_encoded_attr(self):
        return "a", "b"

    @attribute(
        change_event_implemented=True,
    )
    def slow_attr(self) -> int:
        time.sleep(1)
        return 0

    @attribute(
        alarm_event_implemented=True,
        archive_event_implemented=True,
        change_event_implemented=True,
        data_ready_event_implemented=True,
    )
    def attr_decorator_with_kwords(self) -> int:
        return 0

    attr_class_with_kwords = attribute(
        alarm_event_implemented=True,
        archive_event_implemented=True,
        change_event_implemented=True,
        data_ready_event_implemented=True,
    )

    def read_attr_class_with_kwords(self) -> int:
        return 0

    @command
    def reset(self):
        self._requested_event_type = None
        self._base = 0

    def _send_events(self, attr_name: str, event_type: int):
        # to test fire_xxx_event methods we should have attr object and exception, converted to DevFailed:
        attr = self.get_device_attr().get_attr_by_name(attr_name)
        try:
            raise Exception(f"test exception {self._base + 1}")
        except Exception:
            test_exception = Except.to_dev_failed(*sys.exc_info())

        if event_type == EventType.USER_EVENT:
            self.push_event(attr_name, [], [], self._base + 1)
            self.push_event(
                attr_name, [], [], self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )
            self.push_event(
                attr_name, [], [], Exception(f"test exception {self._base}")
            )

        elif event_type == EventType.ARCHIVE_EVENT:
            self.push_archive_event(attr_name, self._base + 1)
            self.push_archive_event(
                attr_name, self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )
            self.push_archive_event(
                attr_name, Exception(f"test exception {self._base}")
            )

        elif event_type == EventType.CHANGE_EVENT:
            self.push_change_event(attr_name, self._base + 1)

            self.push_change_event(
                attr_name, self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )

            attr.set_value(self._base + 3)
            attr.fire_change_event()

            self.push_change_event(attr_name, Exception(f"test exception {self._base}"))

            attr.fire_change_event(test_exception)

        elif event_type == EventType.ALARM_EVENT:
            self.push_alarm_event(attr_name, self._base + 1)

            self.push_alarm_event(
                attr_name, self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )

            attr.set_value(self._base + 3)
            attr.fire_alarm_event()

            self.push_alarm_event(attr_name, Exception(f"test exception {self._base}"))

            attr.fire_alarm_event(test_exception)

        elif event_type == EventType.DATA_READY_EVENT:
            self.push_data_ready_event(attr_name, self._base + 1)

    @command
    def send_events(self, event_type: int):
        self._send_events("attr", event_type)

    @command
    def send_slow_event(self):
        self.push_change_event("slow_attr", 42)

    @command
    def send_event_no_data(self, attr_name: str):
        self.push_event(attr_name, [], [])

    @command
    def send_archive_event_no_data(self, attr_name: str):
        self.push_archive_event(attr_name)

    @command
    def send_change_event_no_data(self, attr_name: str):
        self.push_change_event(attr_name)

    @command
    def send_alarm_event_no_data(self, attr_name: str):
        self.push_alarm_event(attr_name)

    @command
    def send_change_event_with_dim_argument(self):
        dim_x_dim_y_unsupported = "dim_x and dim_y arguments are no longer supported"
        now = time.time()

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, 1, 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, dim_x=1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, dim_x=1, dim_y=1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, now, AttrQuality.ATTR_VALID, 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("attr", 42, now, AttrQuality.ATTR_VALID, 1, 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("dev_encoded_attr", "a", "b", 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("dev_encoded_attr", "a", "b", 1, 1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("dev_encoded_attr", "a", "b", dim_x=1)

        with pytest.raises(TypeError, match=dim_x_dim_y_unsupported):
            self.push_change_event("dev_encoded_attr", "a", "b", dim_x=1, dim_y=1)

        # check some valid dev encoded events work
        self.push_change_event("dev_encoded_attr", "a", "b")
        self.push_change_event(
            "dev_encoded_attr", "a", "b", now, AttrQuality.ATTR_VALID
        )

    @command(dtype_in=str)
    def add_dyn_attr(self, name):
        attr = attribute(name=name, dtype="float", fget=self.read)
        self.add_attribute(attr)

    @command(dtype_in=str)
    def delete_dyn_attr(self, name):
        self.remove_attribute(name)

    def read(self, attr):
        attr.set_value(1.23)


cmd_list = {
    "Init",
    "State",
    "Status",
    "reset",
    "add_dyn_attr",
    "delete_dyn_attr",
    "send_events",
    "send_event_no_data",
    "send_slow_event",
    "send_archive_event_no_data",
    "send_change_event_no_data",
    "send_alarm_event_no_data",
    "send_change_event_with_dim_argument",
}

attr_list = {
    "attr",
    "attr_decorator_with_kwords",
    "attr_class_with_kwords",
    "dev_encoded_attr",
    "slow_attr",
    "State",
    "Status",
}

DEVICE_NAME = "test/nodb/eventdevice"


# Device fixture
@pytest.fixture(scope="module")
def event_device_context():
    context = DeviceTestContext(
        EventDevice, device_name=DEVICE_NAME, host="127.0.0.1", process=True
    )
    with context:
        yield context


@pytest.fixture(scope="module")
def event_device_with_green_modes(event_device_context, green_mode_device_proxy):
    return green_mode_device_proxy(event_device_context.get_device_access())


@pytest.fixture(scope="module")
def event_device(event_device_context):
    return DeviceProxy(event_device_context.get_device_access())


# Tests
def assert_events_received(proxy, expected_res):
    for retry_count in range(MAX_RETRIES):
        proxy.read_attribute("state", wait=True)
        if len(event_results) >= len(expected_res):
            assert_close(event_results, expected_res)
            return
        time.sleep(DELAY_PER_RETRY)
    timeout_seconds = MAX_RETRIES * DELAY_PER_RETRY
    pytest.fail(
        f"Timeout, waiting for event, after {timeout_seconds} sec over {MAX_RETRIES} retries. "
        f"Occasionally happens, probably due to CI test runtime environment"
    )


def run_event_test(proxy, event_type, cb, expected_res):
    event_results.clear()
    proxy.command_inout("reset", wait=True)

    eid_change = proxy.subscribe_event("attr", event_type, cb, wait=True)

    # Trigger events from command
    proxy.command_inout("send_events", event_type, wait=True)

    # Trigger events from attribute write method
    proxy.write_attribute("attr", event_type, wait=True)

    # Trigger events from attribute read method
    proxy.read_attribute("attr", wait=True)

    # Test the event values
    assert_events_received(proxy, expected_res)

    # Unsubscribe
    proxy.unsubscribe_event(eid_change)


def test_old_push_event_signatures_no_longer_supported(event_device):
    event_device.send_change_event_with_dim_argument()


def test_change_event(event_device_with_green_modes):
    expected_res = [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
        11,
        12,
        13,
        "Exception: test exception 10\n",
        "Exception: test exception 11\n",
        21,
        22,
        23,
        "Exception: test exception 20\n",
        "Exception: test exception 21\n",
    ]

    if event_device_with_green_modes.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device_with_green_modes,
            EventType.CHANGE_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device_with_green_modes,
                EventType.CHANGE_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device_with_green_modes,
            EventType.CHANGE_EVENT,
            event_callback,
            expected_res,
        )


def test_alarm_event(event_device):
    expected_res = [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
        11,
        12,
        13,
        "Exception: test exception 10\n",
        "Exception: test exception 11\n",
        21,
        22,
        23,
        "Exception: test exception 20\n",
        "Exception: test exception 21\n",
    ]

    run_event_test(
        event_device,
        EventType.ALARM_EVENT,
        event_callback,
        expected_res,
    )


def test_user_event(event_device):
    expected_res = [
        0,
        1,
        2,
        "Exception: test exception 0\n",
        11,
        12,
        "Exception: test exception 10\n",
        21,
        22,
        "Exception: test exception 20\n",
    ]

    run_event_test(
        event_device,
        EventType.USER_EVENT,
        event_callback,
        expected_res,
    )


def test_archive_event(event_device):
    expected_res = [
        0,
        1,
        2,
        "Exception: test exception 0\n",
        11,
        12,
        "Exception: test exception 10\n",
        21,
        22,
        "Exception: test exception 20\n",
    ]

    run_event_test(
        event_device,
        EventType.ARCHIVE_EVENT,
        event_callback,
        expected_res,
    )


def test_subscribe_data_ready_event(event_device):
    expected_res = [1, 11, 21]
    run_event_test(
        event_device,
        EventType.DATA_READY_EVENT,
        event_callback,
        expected_res,
    )


def test_subscribe_interface_event(event_device):

    def cb(event):
        if len(event_results) == 0:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list
        elif len(event_results) == 1:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list | {"bla"}
        else:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list

        event_results.append(True)

    event_results.clear()

    # Subscribe
    eid = event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb, wait=True)
    # Trigger an event
    event_device.command_inout("add_dyn_attr", "bla", wait=True)
    event_device.read_attribute("bla", wait=True)
    # Wait for tango event
    assert_events_received(event_device, [True, True])

    event_device.command_inout("delete_dyn_attr", "bla", wait=True)
    # Wait for tango event
    assert_events_received(event_device, [True, True, True])
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_push_event_with_event_callback(event_device):
    string = StringIO()
    cb = EventCallback(fd=string)

    # to reduce tests amount here we test only change event
    eid = event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, wait=True)
    # trigger an event
    event_device.command_inout("send_events", EventType.CHANGE_EVENT, wait=True)
    # wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(cb.get_events()) > 5:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
            f"Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values and timestamp
    events = cb.get_events()
    results = [evt.attr_value.value for evt in events[:4]]
    assert results == [0, 1, 2, 3]
    assert events[2].attr_value.time.totime() == 3.0
    assert events[4].errors[0].desc == "Exception: test exception 0\n"
    assert events[5].errors[0].desc == "Exception: test exception 1\n"
    for evt in events:
        assert evt.device is event_device

    # Check string
    for line in [
        "TEST/NODB/EVENTDEVICE ATTR CHANGE SUBSUCCESS [ATTR_VALID] 0",
        "TEST/NODB/EVENTDEVICE ATTR CHANGE UPDATE [ATTR_VALID] 1",
        "TEST/NODB/EVENTDEVICE ATTR CHANGE UPDATE [ATTR_WARNING] 2",
        "TEST/NODB/EVENTDEVICE ATTR CHANGE UPDATE [ATTR_VALID] 3",
        "TEST/NODB/EVENTDEVICE ATTR CHANGE UPDATE [PyDs_PythonError] Exception: test exception 0",
        "TEST/NODB/EVENTDEVICE ATTR CHANGE UPDATE [PyDs_PythonError] Exception: test exception 1",
    ]:
        assert line in string.getvalue()
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_send_events_no_data(event_device):
    event_device.command_inout("send_event_no_data", "state", wait=True)
    event_device.command_inout("send_archive_event_no_data", "State", wait=True)
    event_device.command_inout("send_change_event_no_data", "STaTe", wait=True)
    event_device.command_inout("send_alarm_event_no_data", "state", wait=True)

    event_device.command_inout("send_event_no_data", "status", wait=True)
    event_device.command_inout("send_archive_event_no_data", "Status", wait=True)
    event_device.command_inout("send_change_event_no_data", "STaTus", wait=True)
    event_device.command_inout("send_alarm_event_no_data", "status", wait=True)

    expected_err_msg = (
        "Cannot push event for attribute attr without data. "
        "Pushing event without data parameter is only allowed for State and Status attributes."
    )

    with pytest.raises(DevFailed, match=expected_err_msg):
        event_device.command_inout("send_event_no_data", "attr", wait=True)

    with pytest.raises(DevFailed, match=expected_err_msg):
        event_device.command_inout("send_archive_event_no_data", "attr", wait=True)

    with pytest.raises(DevFailed, match=expected_err_msg):
        event_device.command_inout("send_change_event_no_data", "attr", wait=True)

    with pytest.raises(DevFailed, match=expected_err_msg):
        event_device.command_inout("send_alarm_event_no_data", "attr", wait=True)


def test_main_thread_is_omni_thread():
    assert is_omni_thread()


def test_ensure_omni_thread_main_thread_is_omni_thread():
    with EnsureOmniThread():
        assert is_omni_thread()


def test_user_thread_is_not_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is False


def test_ensure_omni_thread_user_thread_is_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        with EnsureOmniThread():
            thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is True


def test_subscribe_change_event_from_user_thread(event_device):
    event_results.clear()

    def thread_func():
        with EnsureOmniThread():
            eid = event_device.subscribe_event(
                "attr", EventType.CHANGE_EVENT, event_callback, wait=True
            )
            while running:
                time.sleep(DELAY_PER_RETRY)
            event_device.unsubscribe_event(eid)

    # Start the thread
    thread = Thread(target=thread_func)
    running = True
    thread.start()
    # Wait for tango events
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(event_results) == 1:
            # Trigger an event (1 result means thread has completed subscription,
            # as that results in an initial callback)
            event_device.command_inout("send_events", EventType.CHANGE_EVENT, wait=True)
        elif len(event_results) > 2:
            # At least 2 events means an event was received after subscription
            break
        time.sleep(DELAY_PER_RETRY)
    # Stop the thread
    running = False

    thread.join()
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
            f"Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values
    assert event_results == [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
    ]


def test_get_events(event_device):
    for receiver in ["cb", "no"]:
        for event_type in EventType.values.values():
            event_results.clear()

            if event_type == EventType.PERIODIC_EVENT:  # needs polling, so skip
                continue
            eid = event_device.subscribe_event("attr", event_type, 1, wait=True)

            # DATA_READY_EVENT does not send automatically at the subscription
            if event_type == EventType.DATA_READY_EVENT:
                event_device.send_events(event_type, wait=True)

            for retry_count in range(MAX_RETRIES):
                if receiver == "no":
                    if len(event_device.get_events(eid)):
                        break
                else:
                    event_device.get_events(eid, event_callback)
                    if len(event_results):
                        break
                time.sleep(DELAY_PER_RETRY)

            if retry_count + 1 >= MAX_RETRIES:
                timeout_seconds = retry_count * DELAY_PER_RETRY
                pytest.fail(
                    f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
                    f"Occasionally happens, probably due to CI test runtime environment"
                )

            event_device.unsubscribe_event(eid)


def test_callback_was_dereferenced(event_device):

    def fcb(_event):
        pass

    initial_refs = len(gc.get_referrers(fcb))
    ids = [
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, fcb, wait=True)
        for _ in range(10)
    ]
    assert initial_refs < len(gc.get_referrers(fcb))

    for id in ids:
        event_device.unsubscribe_event(id, wait=True)

    assert initial_refs == len(gc.get_referrers(fcb))


def test_event_after_unsubscription_crash(event_device):

    class DummyCallback:

        def push_event(self, event):
            pass

    class MainCallback:

        def __init__(self):
            self.device = DeviceProxy(DEVICE_NAME)
            self.eid = self.device.subscribe_event(
                "attr", EventType.CHANGE_EVENT, DummyCallback()
            )
            self.is_first_time = True

        def push_event(self, _event):
            if self.is_first_time:
                # callback from initial subscription
                self.is_first_time = False
            elif self.device:
                # callback from a change event, and haven't unsubscribed yet
                self.device.unsubscribe_event(self.eid)
                self.device = None  # remove reference, so it can be deleted
            return

    for _ in range(50):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, MainCallback())
        event_device.send_events(EventType.CHANGE_EVENT)


def test_events_enabled_by_kwords(event_device):
    """
    In this test we only check, that we can subscribe, i.e., that out kwords were passed to Tango::Attr
    """
    events_to_check = [
        EventType.ALARM_EVENT,
        EventType.ARCHIVE_EVENT,
        EventType.CHANGE_EVENT,
        EventType.DATA_READY_EVENT,
    ]

    for attr_name in ["attr_decorator_with_kwords", "attr_class_with_kwords"]:
        eids = [
            event_device.subscribe_event(
                attr_name, event_type, event_callback, wait=True
            )
            for event_type in events_to_check
        ]
        for eid in eids:
            event_device.unsubscribe_event(eid)


subscription_modes_and_expected_results = (
    # subscription mode; expected subscription time; should we expect subscription event; expected event time; should be data in event
    (EventSubMode.Sync, 0.1, False, None, False),
    (EventSubMode.SyncRead, 1.1, True, 0.1, True),
    (EventSubMode.Async, 0.1, True, 0.1, False),
    (EventSubMode.AsyncRead, 0.1, True, 1.1, True),
    (EventSubMode.Stateless, 1.1, True, 0.1, True),
)


def wait_for_single_event(proxy, events, timeout) -> EventData:
    t0 = time.time()
    while time.time() - t0 < timeout:
        proxy.read_attribute("state", wait=True)
        if len(events) == 1:
            break
        time.sleep(DELAY_PER_RETRY)
    assert len(events) == 1
    return events[0]


@pytest.mark.parametrize(
    "subscription_modes_and_expected_results",
    subscription_modes_and_expected_results,
    ids=[str(mode) for mode, _, _, _, _ in subscription_modes_and_expected_results],
)
def test_async_events_subscription(subscription_modes_and_expected_results):
    (
        subscription_mode,
        expected_subscription_time,
        should_expect_subscription_event,
        expected_event_time,
        should_be_data_in_event,
    ) = subscription_modes_and_expected_results

    test_event_results = []

    def cb(evt):
        test_event_results.append(evt)

    with DeviceTestContext(EventDevice, process=True) as event_device:
        start_time = time.time()
        eid = event_device.subscribe_event(
            "slow_attr", EventType.CHANGE_EVENT, cb, subscription_mode
        )

        assert time.time() - start_time <= expected_subscription_time

        if should_expect_subscription_event:
            event = wait_for_single_event(
                event_device, test_event_results, expected_event_time
            )
            assert event.event_reason == EventReason.SubSuccess

            if should_be_data_in_event:
                assert test_event_results[0].attr_value is not None

        test_event_results.clear()
        event_device.send_slow_event()
        event = wait_for_single_event(event_device, test_event_results, timeout=0.1)
        assert event.event_reason == EventReason.Update
        assert event.attr_value is not None

        event_device.unsubscribe_event(eid)


def test_async_events_subscription_fails():

    test_event_results = []

    def cb(evt):
        test_event_results.append(evt)

    with DeviceTestContext(Device, process=True) as event_device:
        eid = event_device.subscribe_event(
            "non_existent_attr",
            EventType.CHANGE_EVENT,
            cb,
            EventSubMode.Async,
        )

        event = wait_for_single_event(event_device, test_event_results, 0.1)
        assert event.event_reason == EventReason.SubFail
        assert event.attr_value is None

        event_device.unsubscribe_event(eid)


def test_subscribe_event_signatures():
    """
    Signatures to be supported:

        subscribe_event(self,            event_type, cb,        sub_mode=EventSubMode.SyncRead, *, __GREEN_KWARGS__) -> int
        subscribe_event(self,            event_type, cb,        stateless=False,                *, __GREEN_KWARGS__) -> int

        subscribe_event(self, attr_name, event_type, cb,        sub_mode=EventSubMode.SyncRead, extract_as=ExtractAs.Numpy, *, __GREEN_KWARGS__) -> int
        subscribe_event(self, attr_name, event_type, queuesize, sub_mode=EventSubMode.SyncRead, extract_as=ExtractAs.Numpy, *, __GREEN_KWARGS__) -> int
        subscribe_event(self, attr_name, event_type, cb,        filters=[], stateless=False,    extract_as=ExtractAs.Numpy, *, __GREEN_KWARGS__) -> int
        subscribe_event(self, attr_name, event_type, queuesize, filters=[], stateless=False,    extract_as=ExtractAs.Numpy, *, __GREEN_KWARGS__) -> int
    """

    last_called_method_and_args = []

    def cb(evnt):
        pass

    cb_with_push_event = EventCallback()

    def subscription_call_mock(method, *args):
        last_called_method_and_args.append((method, *args))
        return len(last_called_method_and_args)

    def check_last_called_method(*method_and_args):
        for called, expected in zip(last_called_method_and_args[-1], method_and_args):
            if callable(expected):
                callback = inspect.unwrap(called.push_event)
                assert callback == expected
            else:
                assert called == expected

    # functionality is mocked, so we don't need a real device
    event_device = DeviceProxy("tango://127.0.0.1:0/dummy/test/device#dbase=no")

    with pytest.warns(PyTangoUserWarning):
        event_device.unfreeze_dynamic_interface()

    event_device.__subscribe_event_global_with_stateless_flag = (
        lambda *args: subscription_call_mock(
            "__subscribe_event_global_with_stateless_flag", *args
        )
    )
    event_device.__subscribe_event_global_with_sub_mode = (
        lambda *args: subscription_call_mock(
            "__subscribe_event_global_with_sub_mode", *args
        )
    )
    event_device.__subscribe_event_attrib_with_stateless_flag = (
        lambda *args: subscription_call_mock(
            "__subscribe_event_attrib_with_stateless_flag", *args
        )
    )
    event_device.__subscribe_event_attrib_with_sub_mode = (
        lambda *args: subscription_call_mock(
            "__subscribe_event_attrib_with_sub_mode", *args
        )
    )

    with pytest.raises(
        TypeError, match="This method is only for Interface Change Events"
    ):
        event_device.subscribe_event(EventType.CHANGE_EVENT)

    with pytest.raises(IndexError, match="Expected parameter 'cb'"):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT)

    event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb)
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        EventSubMode.SyncRead,
    )
    event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb=cb)
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        EventSubMode.SyncRead,
    )
    event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb_with_push_event)
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb_with_push_event.push_event,
        EventSubMode.SyncRead,
    )
    event_device.subscribe_event(
        EventType.INTERFACE_CHANGE_EVENT, cb=cb_with_push_event
    )
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb_with_push_event.push_event,
        EventSubMode.SyncRead,
    )

    with pytest.raises(TypeError, match="Parameter 'cb' must be callable object"):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb=None)

    with pytest.raises(TypeError, match="Parameter 'cb' must be callable object"):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, None)

    with pytest.raises(
        IndexError,
        match="Expected parameter 'cb' as either positional arg 2, ",
    ):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT)

    event_device.subscribe_event(
        EventType.INTERFACE_CHANGE_EVENT, cb, EventSubMode.AsyncRead
    )
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
    )
    event_device.subscribe_event(
        EventType.INTERFACE_CHANGE_EVENT, cb, sub_mode=EventSubMode.AsyncRead
    )
    check_last_called_method(
        "__subscribe_event_global_with_sub_mode",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
    )

    with pytest.warns(
        DeprecationWarning, match="The 'stateless' parameter is deprecated"
    ):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb, False)

    check_last_called_method(
        "__subscribe_event_global_with_stateless_flag",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        False,
    )
    with pytest.warns(
        DeprecationWarning, match="The 'stateless' parameter is deprecated"
    ):
        event_device.subscribe_event(
            EventType.INTERFACE_CHANGE_EVENT, cb, stateless=False
        )
    check_last_called_method(
        "__subscribe_event_global_with_stateless_flag",
        EventType.INTERFACE_CHANGE_EVENT,
        cb,
        False,
    )

    with pytest.raises(TypeError, match="Invalid type for parameter"):
        event_device.subscribe_event(EventType.INTERFACE_CHANGE_EVENT, cb, None)

    with pytest.raises(TypeError, match="Invalid type for parameter"):
        event_device.subscribe_event(
            EventType.INTERFACE_CHANGE_EVENT, cb, sub_mode=None
        )

    with pytest.raises(TypeError, match="Invalid type for parameter"):
        event_device.subscribe_event(
            EventType.INTERFACE_CHANGE_EVENT, cb, stateless=None
        )

    with pytest.raises(IndexError, match="Expected parameter 'event_type'"):
        event_device.subscribe_event("attr")

    with pytest.raises(TypeError, match="Invalid type for parameter"):
        event_device.subscribe_event("attr", None)

    with pytest.raises(TypeError, match="Invalid type for parameter"):
        event_device.subscribe_event("attr", event_type=None)

    with pytest.raises(
        TypeError, match="Either parameter 'queuesize' .* or parameter 'cb'"
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT)

    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )
    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb=cb)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )
    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb_with_push_event)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb_with_push_event.push_event,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )
    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb=cb_with_push_event)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb_with_push_event.push_event,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )

    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, 1)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        1,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )
    event_device.subscribe_event("attr", EventType.CHANGE_EVENT, queuesize=1)
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        1,
        EventSubMode.SyncRead,
        ExtractAs.Numpy,
    )

    with pytest.raises(
        TypeError, match="Either parameter 'queuesize' .* or parameter 'cb'"
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, None)

    with pytest.raises(TypeError, match="'cb' and 'queuesize' cannot be used together"):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb=cb,
            queuesize=1,
        )

    with pytest.raises(TypeError, match="Invalid type for parameter 'cb=None'"):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb=None)

    with pytest.raises(TypeError, match="Invalid type for parameter 'queuesize="):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, queuesize=None)

    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, [])
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        False,
        ExtractAs.Numpy,
        [],
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, filters=[])
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        False,
        ExtractAs.Numpy,
        [],
    )

    with pytest.raises(TypeError, match="Invalid type for parameter 'filters="):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, filters=None)

    event_device.subscribe_event(
        "attr", EventType.CHANGE_EVENT, cb, EventSubMode.AsyncRead
    )
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Numpy,
    )
    event_device.subscribe_event(
        "attr", EventType.CHANGE_EVENT, cb, sub_mode=EventSubMode.AsyncRead
    )
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Numpy,
    )
    with pytest.raises(TypeError, match="Invalid type for parameter 'sub_mode"):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, sub_mode=None)
    with pytest.raises(TypeError, match="Invalid type for parameter 'stateless"):
        event_device.subscribe_event(
            "attr", EventType.CHANGE_EVENT, cb, [], EventSubMode.SyncRead
        )
    with pytest.raises(
        TypeError, match="'sub_mode' and 'filters' cannot be used together"
    ):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            filters=[],
            sub_mode=EventSubMode.SyncRead,
        )
    with pytest.raises(
        TypeError, match="'sub_mode' and 'stateless' cannot be used together"
    ):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            stateless=False,
            sub_mode=EventSubMode.SyncRead,
        )

    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, [], True)
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Numpy,
        [],
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event(
            "attr", EventType.CHANGE_EVENT, cb, [], stateless=True
        )
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Numpy,
        [],
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event(
            "attr", EventType.CHANGE_EVENT, cb, filters=["a", "b"], stateless=True
        )
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Numpy,
        ["a", "b"],
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, stateless=True)
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Numpy,
        [],
    )
    with pytest.raises(TypeError, match="Invalid type for parameter 'sub_mode"):
        event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, False)
    with pytest.raises(TypeError, match="Invalid type for parameter 'stateless"):
        event_device.subscribe_event(
            "attr", EventType.CHANGE_EVENT, cb, [], stateless=None
        )

    event_device.subscribe_event(
        "attr", EventType.CHANGE_EVENT, cb, EventSubMode.AsyncRead, ExtractAs.Tuple
    )
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Tuple,
    )
    event_device.subscribe_event(
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        extract_as=ExtractAs.Tuple,
    )
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Tuple,
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            [],
            True,
            ExtractAs.Tuple,
        )
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Tuple,
        [],
    )
    with pytest.warns(
        DeprecationWarning,
        match="The 'stateless' and 'filters' parameters are deprecated",
    ):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            [],
            True,
            extract_as=ExtractAs.Tuple,
        )
    check_last_called_method(
        "__subscribe_event_attrib_with_stateless_flag",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        True,
        ExtractAs.Tuple,
        [],
    )

    with pytest.raises(
        TypeError, match="Invalid type for parameter 'extract_as' at position 4"
    ):
        event_device.subscribe_event(
            "attr", EventType.CHANGE_EVENT, cb, EventSubMode.SyncRead, None
        )

    with pytest.raises(TypeError, match="Invalid type for parameter 'extract_as"):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            EventSubMode.SyncRead,
            extract_as=None,
        )

    event_device.subscribe_event(
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Tuple,
        green_mode=GreenMode.Synchronous,
    )
    check_last_called_method(
        "__subscribe_event_attrib_with_sub_mode",
        "attr",
        EventType.CHANGE_EVENT,
        cb,
        EventSubMode.AsyncRead,
        ExtractAs.Tuple,
    )

    with pytest.raises(
        TypeError,
        match="Got unexpected keyword argument.*submode.*\nAllowed.*sub_mode.*",
    ):
        event_device.subscribe_event(
            "attr",
            EventType.CHANGE_EVENT,
            cb,
            submode=EventSubMode.SyncRead,
            extract_as=None,
        )
