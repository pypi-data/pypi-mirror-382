# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
import logging
import os
import sys
import time

import pytest
import socket
from subprocess import Popen, PIPE

from tango import DevState
from tango.test_utils import wait_for_proxy

# Helpers

MAX_STARTUP_TIME_SEC = 30.0


def start_database(port, inst):
    python = sys.executable
    tests_directory = os.path.dirname(__file__)
    cmd = (
        f"{python} -u -m tango.databaseds.database"
        f" --host=127.0.0.1 --port={port}"
        f" --logging_level=2 {inst}"
    )
    env = os.environ.copy()
    env["PYTANGO_DATABASE_NAME"] = ":memory:"  # Don't write to disk
    logging.debug("Starting databaseds subprocess...")
    proc = Popen(
        cmd.split(), cwd=tests_directory, stdout=PIPE, bufsize=1, text=True, env=env
    )
    logging.debug("Waiting for databaseds to startup...")
    try:
        wait_for_tango_server_startup(proc)
    except RuntimeError:
        proc.terminate()
        raise

    return proc


def wait_for_tango_server_startup(proc):
    t0 = time.time()
    for line in proc.stdout:
        now = time.time()
        elapsed = now - t0
        print(line, end="")
        if "Ready to accept request" in line:
            logging.debug(f"Databaseds startup complete after {elapsed:.1f} sec")
            break
        if elapsed > MAX_STARTUP_TIME_SEC:
            msg = f"Databaseds startup timed out after {elapsed:.1f} sec"
            logging.error(msg)
            raise RuntimeError(msg)


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture()
def tango_database_test():
    port = get_open_port()
    inst = 2

    proc = start_database(port, inst)
    logging.debug("Waiting for databaseds proxy...")
    proxy = wait_for_proxy(f"tango://127.0.0.1:{port}/sys/database/2")
    logging.debug("Databaseds proxy is ready")

    yield proxy

    proc.terminate()
    logging.debug("Terminated databaseds")
    print("Remaining databaseds output:")
    for line in proc.stdout:
        print(line, end="")


# Tests
def test_ping(tango_database_test):
    duration = tango_database_test.ping(wait=True)
    assert isinstance(duration, int)


def test_status(tango_database_test):
    assert tango_database_test.status() == "The device is in ON state."


def test_state(tango_database_test):
    assert tango_database_test.state() == DevState.ON


def test_device_property(tango_database_test):
    test_property_name = "test property"
    test_property_value = "test property text"

    tango_database_test.put_property({test_property_name: test_property_value})
    return_property_list = tango_database_test.get_property_list("*")
    assert len(return_property_list) == 1
    assert return_property_list[0] == test_property_name

    return_property = tango_database_test.get_property("test property")
    assert return_property[test_property_name][0] == test_property_value


def test_info(tango_database_test):
    info = tango_database_test.info()

    assert info.dev_class == "DataBase"
    assert info.doc_url == "Doc URL = http://www.tango-controls.org"
    assert info.server_id == "DataBaseds/2"
