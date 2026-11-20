#!/usr/bin/env python3
"""Turns the Qw/ST Pad and the Display HAT Mini buttons into one virtual gamepad.

The pad has no interrupt line wired, so we poll it over I2C. Presses go out through
uinput as a normal Linux gamepad called "Pokepi Pad", which RetroArch (or anything
else) picks up like a USB controller.

Run: sudo python3 pad_gamepad.py   (needs /dev/uinput, the systemd service runs it as root)
"""
import signal
import sys
import time

from evdev import UInput, ecodes as e
from smbus2 import SMBus
import RPi.GPIO as GPIO

PAD_BUS = 1
PAD_ADDRESS = 0x21
POLL_HZ = 250

# TCA9555 registers
REG_INPUT = 0x00
REG_OUTPUT = 0x02
REG_CONFIG = 0x06
LED_BITS = (6, 7, 9, 10)          # active low

# Qw/ST Pad bit -> key. Face buttons follow the Nintendo layout (A on the right).
PAD_KEYS = {
    1: e.BTN_DPAD_UP,
    2: e.BTN_DPAD_LEFT,
    3: e.BTN_DPAD_RIGHT,
    4: e.BTN_DPAD_DOWN,
    5: e.BTN_SELECT,              # minus
    11: e.BTN_START,              # plus
    12: e.BTN_SOUTH,              # B
    13: e.BTN_WEST,               # Y
    14: e.BTN_EAST,               # A
    15: e.BTN_NORTH,              # X
}

# Display HAT Mini buttons (BCM pins, pressed = low). A/B sit left of the screen, X/Y right.
HAT_KEYS = {
    5: e.BTN_TL,                  # HAT A -> L
    16: e.BTN_TR,                 # HAT X -> R
    6: e.BTN_MODE,                # HAT B -> menu / hotkey
    24: e.BTN_THUMBL,             # HAT Y -> fast forward
}

DEVICE_NAME = "Pokepi Pad"


def setup_pad(bus):
    led_mask = sum(1 << b for b in LED_BITS)
    bus.write_word_data(PAD_ADDRESS, REG_CONFIG, 0xFFFF & ~led_mask)
    set_leds(bus, 0b0001)


def set_leds(bus, pattern):
    out = 0xFFFF
    for i, bit in enumerate(LED_BITS):
        if (pattern >> i) & 1:
            out &= ~(1 << bit)
    bus.write_word_data(PAD_ADDRESS, REG_OUTPUT, out)


def main():
    keys = list(PAD_KEYS.values()) + list(HAT_KEYS.values())
    ui = UInput({e.EV_KEY: keys}, name=DEVICE_NAME, vendor=0x1209, product=0x7050, version=1)

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in HAT_KEYS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    bus = SMBus(PAD_BUS)
    setup_pad(bus)

    running = True

    def stop(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    state = {}
    errors = 0
    period = 1.0 / POLL_HZ
    while running:
        start = time.monotonic()
        pressed = {}
        try:
            raw = bus.read_word_data(PAD_ADDRESS, REG_INPUT)
            errors = 0
            for bit, key in PAD_KEYS.items():
                pressed[key] = not (raw >> bit) & 1
        except OSError:
            # A loose cable shouldn't kill the service. Release pad keys and keep trying.
            errors += 1
            for key in PAD_KEYS.values():
                pressed[key] = False
            if errors % POLL_HZ == 1:
                print("pad read failed, retrying", file=sys.stderr, flush=True)
                try:
                    setup_pad(bus)
                except OSError:
                    pass
        for pin, key in HAT_KEYS.items():
            pressed[key] = GPIO.input(pin) == GPIO.LOW

        changed = False
        for key, down in pressed.items():
            if state.get(key) != down:
                ui.write(e.EV_KEY, key, int(down))
                state[key] = down
                changed = True
        if changed:
            ui.syn()

        time.sleep(max(0.0, period - (time.monotonic() - start)))

    try:
        set_leds(bus, 0)
    except OSError:
        pass
    ui.close()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
