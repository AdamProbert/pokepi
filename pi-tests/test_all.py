#!/usr/bin/env python3
"""Everything together: pad buttons and battery shown on the Display HAT Mini.

Run: python3 test_all.py   (Ctrl+C to quit)
"""
import time
from PIL import Image, ImageDraw, ImageFont
from smbus2 import SMBus
from displayhatmini import DisplayHATMini
from qwstpad_raw import QwSTPad

UPS_ADDRESS = 0x43
W, H = DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)
hat = DisplayHATMini(img)
hat.set_backlight(1.0)
pad = QwSTPad()
bus = SMBus(1)
try:
    font = ImageFont.load_default(size=20)
except TypeError:
    font = ImageFont.load_default()

# Button positions on screen, laid out like the case (D-pad left, ABXY right).
LAYOUT = {"U": (70, 70), "D": (70, 150), "L": (30, 110), "R": (110, 110),
          "X": (250, 70), "B": (250, 150), "Y": (210, 110), "A": (290, 110),
          "-": (135, 200), "+": (185, 200)}


def battery_volts():
    try:
        v = bus.read_word_data(UPS_ADDRESS, 0x02)
        v = ((v & 0xFF) << 8) | (v >> 8)
        return (v >> 3) * 0.004
    except OSError:
        return None


last_batt, batt = 0, None
try:
    while True:
        if time.time() - last_batt > 2:
            batt, last_batt = battery_volts(), time.time()
        buttons = pad.read_buttons()
        draw.rectangle((0, 0, W, H), fill=(15, 15, 30))
        draw.text((10, 8), "Pokepi", font=font, fill="white")
        draw.text((180, 8), f"{batt:.2f} V" if batt else "UPS ?", font=font, fill="lime")
        for name, (x, y) in LAYOUT.items():
            on = buttons[name]
            draw.ellipse((x - 18, y - 18, x + 18, y + 18),
                         fill=(240, 200, 40) if on else (60, 60, 80))
            draw.text((x - 6, y - 10), name, font=font, fill="black" if on else "white")
        hat.display()
        time.sleep(1 / 30)
except KeyboardInterrupt:
    pass
