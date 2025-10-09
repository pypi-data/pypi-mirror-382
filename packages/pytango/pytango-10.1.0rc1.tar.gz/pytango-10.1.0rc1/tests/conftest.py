# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Load tango-specific pytest fixtures."""

import multiprocessing
import sys
import os
import json
import shutil
from functools import partial
from subprocess import Popen

import pytest

from tango import DeviceProxy, GreenMode, Util
from tango.asyncio import DeviceProxy as asyncio_DeviceProxy
from tango.gevent import DeviceProxy as gevent_DeviceProxy
from tango.futures import DeviceProxy as futures_DeviceProxy
from tango.test_utils import (
    ClassicAPISimpleDeviceClass,
    ClassicAPISimpleDeviceImpl,
    attr_data_format,
    attribute_numpy_typed_values,
    attribute_typed_values,
    attribute_wrong_numpy_typed,
    base_type,
    command_numpy_typed_values,
    command_typed_values,
    dev_encoded_values,
    extract_as,
    general_typed_values,
    server_green_mode,
    server_serial_model,
    state,
    wait_for_nodb_proxy_via_pid,
)

from tango._tango import _dump_cpp_coverage

__all__ = (
    "state",
    "general_typed_values",
    "command_typed_values",
    "attribute_typed_values",
    "command_numpy_typed_values",
    "attribute_numpy_typed_values",
    "attribute_wrong_numpy_typed",
    "dev_encoded_values",
    "server_green_mode",
    "server_serial_model",
    "attr_data_format",
    "extract_as",
    "base_type",
)

device_proxy_map = {
    GreenMode.Synchronous: DeviceProxy,
    GreenMode.Futures: futures_DeviceProxy,
    GreenMode.Asyncio: partial(asyncio_DeviceProxy, wait=True),
    GreenMode.Gevent: gevent_DeviceProxy,
}


def pytest_addoption(parser):
    parser.addoption(
        "--run_extra_src_tests",
        action="store_true",
        default=False,
        help="run extra tests only for source builds",
    )
    parser.addoption(
        "--write_cpp_coverage",
        action="store_true",
        default=False,
        help="write cpp coverage data during tests",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "extra_src_test: mark test as only for source builds"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_extra_src_tests"):
        # --run_extra_src_tests given in cli: do not skip those tests
        return
    skip_extra_src_test = pytest.mark.skip(
        reason="need --run_extra_src_tests option to run"
    )
    for item in items:
        if "extra_src_test" in item.keywords:
            item.add_marker(skip_extra_src_test)


@pytest.hookimpl()
def pytest_sessionfinish(session):
    """Collects all tests to be run and outputs to bat script"""
    if "--collect-only" in sys.argv and "-q" in sys.argv and "nt" in os.name:
        print("Generating windows test script...")
        script_path = os.path.join(os.path.dirname(__file__), "run_tests_win.bat")
        with open(script_path, "w") as f:
            f.write("REM this script will run all tests separately.\r\n")
            for item in session.items:
                lines = [
                    # First attempt for a single test
                    f'pytest -c pytest_win_config.toml "{item.nodeid}"',
                    # Retry test once, if it failed
                    "if %errorlevel% equ 1 (",
                    f'    pytest --lf -c pytest_win_config.toml "{item.nodeid}"',
                    # Abort if pytest could not execute properly
                    # From: https://docs.pytest.org/en/7.1.x/reference/exit-codes.html
                    #   Exit code 0: All tests were collected and passed successfully
                    #   Exit code 1: Tests were collected and run but some of the tests failed
                    #   Exit code 2: Test execution was interrupted by the user
                    #   Exit code 3: Internal error happened while executing tests
                    #   Exit code 4: pytest command line usage error
                    #   Exit code 5: No tests were collected
                    ") else if %errorlevel% geq 2 if %errorlevel% leq 5 (",
                    "    exit /b %errorlevel%",
                    ")",
                ]
                f.writelines([f"{line}\r\n" for line in lines])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport():
    """Produces summary.json file for quick windows test summary"""
    summary_path = "summary.json"

    outcome = yield  # Run all other pytest_runtest_makereport non wrapped hooks
    result = outcome.get_result()
    if result.when == "call" and "nt" in os.name and os.path.isfile(summary_path):
        with open(summary_path, "r+") as f:
            summary = f.read()
            try:
                summary = json.loads(summary)
            except Exception:
                summary = []
            finally:
                outcome = str(result.outcome).capitalize()
                test = {
                    "testName": result.nodeid,
                    "outcome": outcome,
                    "durationMilliseconds": result.duration,
                    "StdOut": result.capstdout,
                    "StdErr": result.capstderr,
                }
                summary.append(test)
                f.seek(0)
                f.write(json.dumps(summary))
                f.truncate()


def start_server(host, server, inst, device):
    exe = shutil.which(server)
    cmd = f"{exe} {inst} -ORBendPoint giop:tcp:{host}:0 -nodb -dlist {device}"
    proc = Popen(cmd.split(), close_fds=True)
    proc.poll()
    return proc


@pytest.fixture(
    params=GreenMode.values.values(),
    ids=str,
    scope="module",
)
def tango_test_with_green_modes(request):
    green_mode = request.param
    server = "TangoTest"
    inst = "test"
    device = "sys/tg_test/17"
    host = "127.0.0.1"
    proc = start_server(host, server, inst, device)
    proxy = wait_for_nodb_proxy_via_pid(
        proc.pid, host, device, device_proxy_map[green_mode]
    )

    yield proxy

    proc.terminate()
    # let's not wait for it to exit, that takes too long :)


@pytest.fixture(scope="module")
def tango_test():
    green_mode = GreenMode.Synchronous
    server = "TangoTest"
    inst = "test"
    device = "sys/tg_test/17"
    host = "127.0.0.1"
    proc = start_server(host, server, inst, device)
    proxy = wait_for_nodb_proxy_via_pid(
        proc.pid, host, device, device_proxy_map[green_mode]
    )

    yield proxy

    proc.terminate()


@pytest.fixture(scope="function")
def tango_test_process_device_trl_with_function_scope():
    green_mode = GreenMode.Synchronous
    server = "TangoTest"
    inst = "test"
    device = "sys/tg_test/18"
    host = "127.0.0.1"
    proc = start_server(host, server, inst, device)
    proxy = wait_for_nodb_proxy_via_pid(
        proc.pid, host, device, device_proxy_map[green_mode]
    )

    device_trl = (
        f"tango://{proxy.get_dev_host()}:{proxy.get_dev_port()}/"
        f"{proxy.dev_name()}#dbase=no"
    )
    yield proc, device_trl

    proc.terminate()


@pytest.fixture(
    params=GreenMode.values.values(),
    ids=str,
    scope="module",
)
def green_mode_device_proxy(request):
    green_mode = request.param
    return device_proxy_map[green_mode]


def run_mixed_server():
    util = Util(
        [
            "MixedServer",
            "1",
            "-ORBendPoint",
            "giop:tcp:127.0.0.1:0",
            "-nodb",
            "-dlist",
            "my/mixed/1",
        ]
    )
    util.add_class(
        ClassicAPISimpleDeviceClass,
        ClassicAPISimpleDeviceImpl,
        "ClassicAPISimpleDevice",
    )
    util.add_class("TangoTest", "TangoTest", language="c++")
    u = Util.instance()
    u.server_init()
    u.server_run()


@pytest.fixture(autouse=True)
def flush_cpp_coverage_data(request):
    """
    Flushes C++ coverage data to disk after each test execution
    when --write_cpp_coverage command line argument was passed.
    """

    # nothing on enter
    yield

    if request.config.getoption("--write_cpp_coverage"):
        _dump_cpp_coverage()


@pytest.fixture
def mixed_tango_test_server():
    process = multiprocessing.Process(target=run_mixed_server)
    process.start()

    proxy_waiter = partial(
        wait_for_nodb_proxy_via_pid,
        process.pid,
        "127.0.0.1",
        "dserver/mixedserver/1",
        device_proxy_map[GreenMode.Synchronous],
    )
    yield process, proxy_waiter

    if process.is_alive():
        process.terminate()
        process.join(timeout=3.0)  # Allow TangoTest time to stop DataGenerator
