#!/usr/bin/env python3
"""Builds panel.bin, the ST7789 init commands for the kernel panel-mipi-dbi driver.

The sequence is the one Pimoroni's st7789 0.0.4 library sends for the Display HAT Mini.
The only change is MADCTL. The library uses 0x70 and rotates the image 180 degrees in
software, here the panel does the rotation itself (0xB0).

Run: python3 make_panel_bin.py panel.bin [madctl]
"""
import sys

MAGIC = b"MIPI DBI" + bytes(7)
VERSION = 1
DELAY = 0x00   # command 0 with one param means "sleep this many ms"

madctl = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB0

COMMANDS = [
    (0x01, []),                         # SWRESET
    (DELAY, [150]),
    (0x11, []),                         # SLPOUT
    (DELAY, [120]),
    (0x36, [madctl]),                   # MADCTL
    (0x3A, [0x05]),                     # COLMOD 16-bit
    (0xB2, [0x0C, 0x0C, 0x00, 0x33, 0x33]),
    (0xB7, [0x14]),
    (0xBB, [0x37]),
    (0xC0, [0x2C]),
    (0xC2, [0x01]),
    (0xC3, [0x12]),
    (0xC4, [0x20]),
    (0xD0, [0xA4, 0xA1]),
    (0xC6, [0x0F]),                     # 60 Hz
    (0xE0, [0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54, 0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23]),
    (0xE1, [0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44, 0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23]),
    (0x21, []),                         # INVON, this panel needs inversion
    (0x29, []),                         # DISPON
    (DELAY, [100]),
]

data = bytearray(MAGIC)
data.append(VERSION)
for cmd, params in COMMANDS:
    data.append(cmd)
    data.append(len(params))
    data.extend(params)

with open(sys.argv[1], "wb") as f:
    f.write(data)
print(f"wrote {len(data)} bytes to {sys.argv[1]} (MADCTL 0x{madctl:02X})")
