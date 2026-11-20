#!/usr/bin/env python3
"""Qw/ST Pad test: cycles the 4 LEDs, then prints buttons as you press them.

Run: python3 test_pad.py [address]   (Ctrl+C to quit)
"""
import sys
import time
from qwstpad_raw import QwSTPad, DEFAULT_ADDRESS

address = int(sys.argv[1], 0) if len(sys.argv) > 1 else DEFAULT_ADDRESS
pad = QwSTPad(address=address)
print(f"Qw/ST Pad found at 0x{address:02x}. Watch the LEDs light 1 to 4...")
for i in range(4):
    pad.set_leds(1 << i)
    time.sleep(0.3)
pad.set_leds(0)

print("Press buttons. Raw bits are shown so you can check the mapping.")
last = None
try:
    while True:
        raw = pad.raw()
        if raw != last:
            pressed = [n for n, v in pad.read_buttons().items() if v]
            pad.set_leds(min(len(pressed), 4) and (1 << len(pressed)) - 1)
            print(f"raw={raw:016b}  pressed: {' '.join(pressed) or '(none)'}")
            last = raw
        time.sleep(0.01)
except KeyboardInterrupt:
    pad.set_leds(0)
