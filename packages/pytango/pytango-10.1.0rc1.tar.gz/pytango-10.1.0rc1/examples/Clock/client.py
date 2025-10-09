#!/usr/bin/env python
# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Simple client to show how to connect to a Clock device from ClockDS

usage: client clock_dev_name
"""

import sys
import tango

if len(sys.argv) != 2:
    print("must provide one and only one clock device name")
    sys.exit(1)

clock = tango.DeviceProxy(sys.argv[1])
t = clock.time
gmt = clock.gmtime
noon = clock.noon
display = clock.display
print(t)
print(gmt)
print(noon, noon.name, noon.value)
if noon == noon.AM:
    print("Good morning!")
print(clock.ctime(t))
print(clock.mktime(gmt))
print(display, display.name, display.value)
clock.display = display.ANALOG
clock.display = "DIGITAL"  # you can use a valid string to set the value
print(clock.display, clock.display.name, clock.display.value)
display_type = type(display)  # or even create your own IntEnum type
analog = display_type(0)
clock.display = analog
print(clock.display, clock.display.name, clock.display.value)
clock.display = clock.display.DIGITAL
print(clock.display, clock.display.name, clock.display.value)
