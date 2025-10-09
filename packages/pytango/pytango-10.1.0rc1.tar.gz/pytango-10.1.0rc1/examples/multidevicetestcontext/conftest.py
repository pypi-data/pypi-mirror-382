# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
"""
A module defining pytest fixtures for testing with MultiDeviceTestContext
Requires pytest, and at least PyTango 9.5.0
(see commit history for the approach to with earlier versions)
"""

from collections import defaultdict
import pytest
from tango.test_context import MultiDeviceTestContext


@pytest.fixture(scope="module")
def devices_info(request):
    yield getattr(request.module, "devices_info")


@pytest.fixture(scope="function")
def tango_context(devices_info):
    """
    Creates and returns a TANGO MultiDeviceTestContext object.
    """
    with MultiDeviceTestContext(devices_info, process=True) as context:
        yield context
