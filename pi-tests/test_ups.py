#!/usr/bin/env python3
"""Waveshare UPS HAT (C) test: reads battery voltage and current from the INA219.

Run: python3 test_ups.py [address]   (Ctrl+C to quit)
Unplug the charger to see current reverse sign.
"""
import sys
import time
from smbus2 import SMBus

ADDRESS = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x43
SHUNT_OHMS = 0.1


def read_reg(bus, reg):
    v = bus.read_word_data(ADDRESS, reg)
    return ((v & 0xFF) << 8) | (v >> 8)       # INA219 is big-endian


def percent(volts):
    return max(0.0, min(100.0, (volts - 3.0) / (4.2 - 3.0) * 100))


with SMBus(1) as bus:
    while True:
        bus_v = (read_reg(bus, 0x02) >> 3) * 0.004
        shunt = read_reg(bus, 0x01)
        if shunt & 0x8000:
            shunt -= 1 << 16
        amps = shunt * 10e-6 / SHUNT_OHMS
        print(f"battery {bus_v:5.2f} V  current {amps * 1000:7.1f} mA  ~{percent(bus_v):3.0f}%")
        time.sleep(1)
