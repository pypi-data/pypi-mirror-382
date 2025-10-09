# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later

import time

from tango import DeviceProxy
from tango.test_context import DeviceTestContext
from tango.server import Device, attribute


class TestDevice(Device):
    _value = 0.0

    @attribute
    def double_scalar(self) -> float:
        self._value += 1.0
        return self._value

    @double_scalar.write
    def double_scalar(self, value: float) -> None:
        self._value = value


def eval_telemetry_overhead(
    device_name, num_reads_per_iteration=100, num_iterations=200
):
    time_per_iteration = []
    dp = DeviceProxy(device_name)

    for i in range(num_iterations):
        start = time.perf_counter()
        for _ in range(num_reads_per_iteration):
            _ = dp.read_attribute("double_scalar")
        end = time.perf_counter()
        duration_ms = (end - start) * 1000.0
        print(
            f"  {i:3d} Total execution time for {num_reads_per_iteration} iterations: {duration_ms:.3f} milliseconds."
        )
        tpi = duration_ms / num_reads_per_iteration
        print(f"  {i:3d} Average execution time per iteration: {tpi:.3f} milliseconds")
        time_per_iteration.append(tpi)

    average_tpi = sum(time_per_iteration) / num_iterations
    square_sum = 0.0
    for tpi in time_per_iteration:
        square_sum += (tpi - average_tpi) * (tpi - average_tpi)

    rms_tpi = (square_sum / num_iterations) ** 0.5

    print(f"Average execution time: {average_tpi:.3f} milliseconds.")
    print(f"Standard deviation of execution times: {rms_tpi:.3f} milliseconds.")


def benchmark_python_client_and_python_server():
    with DeviceTestContext(TestDevice, device_name="test/device/1", process=True):
        print("Python server running, and runing Python client benchmark now...")
        eval_telemetry_overhead(
            "test/device/1", num_reads_per_iteration=100, num_iterations=100
        )


def benchmark_cpp_client_and_python_server():
    context = DeviceTestContext(
        TestDevice, device_name="test/device/1", process=True, port=44555
    )
    with context:
        print(
            f"Python server running - run C++ client benchmark now for {context.get_device_access()}"
        )
        time.sleep(100)


def benchmark_python_client_and_cpp_server():
    eval_telemetry_overhead(
        "sys/tg_test/1", num_reads_per_iteration=100, num_iterations=100
    )


if __name__ == "__main__":
    # Run one of the following:
    benchmark_python_client_and_python_server()
    # benchmark_cpp_client_and_python_server()
    # benchmark_python_client_and_cpp_server()
