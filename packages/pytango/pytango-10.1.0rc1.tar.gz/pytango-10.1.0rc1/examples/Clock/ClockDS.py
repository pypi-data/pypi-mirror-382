#!/usr/bin/env python
# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Clock Device server showing how to write a TANGO server with a Clock device
which has attributes:

  - time: read-only scalar float
  - gmtime: read-only sequence (spectrum) of integers
  - noon:  read-only enumerated type

commands:

  - ctime: in: float parameter; returns a string
  - mktime: in: sequence (spectrum) of 9 integers; returns a float

Requires at least PyTango 9.5.0 for type hinting to work.  On earlier
versions, use something like `@attribute(dtype=Noon)`.
"""

import time
from enum import IntEnum

from tango.server import Device, attribute, command


class Noon(IntEnum):
    AM = 0  # DevEnum's must start at 0
    PM = 1  # and increment by 1


class DisplayType(IntEnum):
    ANALOG = 0  # DevEnum's must start at 0
    DIGITAL = 1  # and increment by 1


class Clock(Device):
    display_type = DisplayType.ANALOG

    @attribute
    def time(self) -> float:
        return time.time()

    @attribute(max_dim_x=9)
    def gmtime(self) -> tuple[int]:
        return time.gmtime()

    @attribute
    def noon(self) -> Noon:
        time_struct = time.gmtime(time.time())
        return Noon.AM if time_struct.tm_hour < 12 else Noon.PM

    @attribute
    def display(self) -> DisplayType:
        return self.display_type

    @display.setter
    def display(self, display_type: int):
        # note that we receive an integer, not an enum instance,
        # so we have to convert that to an instance of our enum.
        self.display_type = DisplayType(display_type)

    @command(dtype_in=float, dtype_out=str)
    def ctime(self, seconds):
        """
        Convert a time in seconds since the Epoch to a string in local time.
        This is equivalent to asctime(localtime(seconds)). When the time tuple
        is not present, current time as returned by localtime() is used.
        """
        return time.ctime(seconds)

    @command
    def mktime(self, tupl: tuple[int]) -> float:
        return time.mktime(tuple(tupl))


if __name__ == "__main__":
    Clock.run_server()
