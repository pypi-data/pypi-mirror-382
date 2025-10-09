# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
import asyncio
from tango.asyncio import DeviceProxy


async def asyncio_example():
    dev = await DeviceProxy("sys/tg_test/1")
    print(dev.get_green_mode())

    print(await dev.state())

    # in case of high-level API read has to be awaited
    print(await dev.long_scalar)
    print(await dev["long_scalar"])
    print(await getattr(dev, "long_scalar"))

    # while write executed sync
    dev.long_scalar = 1

    # for low-level API both read_attribute and write_attribute have to be awaited
    print(await dev.read_attribute("long_scalar"))
    await dev.write_attribute("long_scalar", 1)


if __name__ == "__main__":
    asyncio.run(asyncio_example())
