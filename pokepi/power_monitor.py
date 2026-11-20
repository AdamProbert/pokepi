#!/usr/bin/env python3
"""Watches the UPS battery and shuts the Pi down safely before it runs flat.

Reads the INA219 on the Waveshare UPS HAT (C) every few seconds. If the battery stays
below LOW_VOLTS while discharging for a while, it powers off cleanly so saves and the
SD card are safe. It also writes the latest reading to /run/pokepi/battery.json so
other things (a battery icon, say) can show it later.

Run: sudo python3 power_monitor.py   (the systemd service runs it as root)
"""
import json
import os
import subprocess
import time

from smbus2 import SMBus

UPS_BUS = 1
UPS_ADDRESS = 0x43
SHUNT_OHMS = 0.1

CHECK_EVERY_S = 5
LOW_VOLTS = 3.30          # shut down below this...
LOW_FOR_S = 30            # ...if it stays there this long while discharging
WARN_VOLTS = 3.50
FULL_VOLTS = 4.20
EMPTY_VOLTS = 3.00

STATUS_FILE = "/run/pokepi/battery.json"


def read_reg(bus, reg):
    v = bus.read_word_data(UPS_ADDRESS, reg)
    return ((v & 0xFF) << 8) | (v >> 8)       # INA219 is big-endian


def read_battery(bus):
    volts = (read_reg(bus, 0x02) >> 3) * 0.004
    shunt = read_reg(bus, 0x01)
    if shunt & 0x8000:
        shunt -= 1 << 16
    amps = shunt * 10e-6 / SHUNT_OHMS          # positive = charging
    return volts, amps


def percent(volts):
    return max(0, min(100, round((volts - EMPTY_VOLTS) / (FULL_VOLTS - EMPTY_VOLTS) * 100)))


def write_status(volts, amps):
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    tmp = STATUS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"volts": round(volts, 3), "milliamps": round(amps * 1000),
                   "percent": percent(volts), "charging": amps > 0,
                   "time": int(time.time())}, f)
    os.replace(tmp, STATUS_FILE)


def main():
    bus = SMBus(UPS_BUS)
    low_since = None
    warned = False
    while True:
        try:
            volts, amps = read_battery(bus)
        except OSError:
            print("couldn't read the UPS, trying again", flush=True)
            time.sleep(CHECK_EVERY_S)
            continue

        write_status(volts, amps)
        discharging = amps < 0

        if discharging and volts < WARN_VOLTS and not warned:
            print(f"battery low: {volts:.2f} V", flush=True)
            warned = True
        elif volts >= WARN_VOLTS + 0.1:
            warned = False

        if discharging and volts < LOW_VOLTS:
            low_since = low_since or time.monotonic()
            if time.monotonic() - low_since >= LOW_FOR_S:
                print(f"battery at {volts:.2f} V for {LOW_FOR_S}s, shutting down", flush=True)
                subprocess.run(["systemctl", "poweroff"])
                return
        else:
            low_since = None

        time.sleep(CHECK_EVERY_S)


if __name__ == "__main__":
    main()
