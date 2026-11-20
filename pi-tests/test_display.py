#!/usr/bin/env python3
"""Display HAT Mini test: colour bars, text, and the 4 HAT buttons drive the RGB LED.

Run: python3 test_display.py   (Ctrl+C to quit)
"""
import time
from PIL import Image, ImageDraw, ImageFont
from displayhatmini import DisplayHATMini

W, H = DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)
hat = DisplayHATMini(img)
hat.set_backlight(1.0)
try:
    font = ImageFont.load_default(size=22)
except TypeError:
    font = ImageFont.load_default()

colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
           (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0)]
bar = W // len(colours)
for i, c in enumerate(colours):
    draw.rectangle((i * bar, 0, (i + 1) * bar, H // 2), fill=c)

BUTTONS = {"A": (hat.BUTTON_A, (1, 0, 0)), "B": (hat.BUTTON_B, (0, 1, 0)),
           "X": (hat.BUTTON_X, (0, 0, 1)), "Y": (hat.BUTTON_Y, (1, 1, 1))}

try:
    while True:
        pressed = [n for n, (pin, _) in BUTTONS.items() if hat.read_button(pin)]
        r = g = b = 0
        for n in pressed:
            cr, cg, cb = BUTTONS[n][1]
            r, g, b = max(r, cr), max(g, cg), max(b, cb)
        hat.set_led(r * 0.5, g * 0.5, b * 0.5)
        draw.rectangle((0, H // 2, W, H), fill=(20, 20, 40))
        draw.text((10, H // 2 + 10), "Pokepi display test", font=font, fill="white")
        draw.text((10, H // 2 + 50), "HAT: " + (" ".join(pressed) or "-"), font=font, fill="yellow")
        hat.display()
        time.sleep(0.05)
except KeyboardInterrupt:
    hat.set_led(0, 0, 0)
