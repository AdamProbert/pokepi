"""Minimal Qw/ST Pad driver for Raspberry Pi (TCA9555 over I2C, smbus2).

Bit numbers come from Pimoroni's qwstpad library. Buttons read 0 when pressed.
"""
from smbus2 import SMBus

DEFAULT_ADDRESS = 0x21          # alternates: 0x23, 0x25, 0x27 (rear cut traces)
BUTTONS = {"U": 1, "L": 2, "R": 3, "D": 4, "-": 5,
           "+": 11, "B": 12, "Y": 13, "A": 14, "X": 15}
LEDS = (6, 7, 9, 10)
LED_ACTIVE_LOW = True           # flip if the player LEDs look inverted

REG_INPUT = 0x00                # input port 0/1 (word read)
REG_OUTPUT = 0x02               # output port 0/1
REG_CONFIG = 0x06               # config port 0/1, 1 = input


class QwSTPad:
    def __init__(self, bus=1, address=DEFAULT_ADDRESS):
        self.bus = SMBus(bus)
        self.address = address
        led_mask = sum(1 << b for b in LEDS)
        self.bus.write_word_data(address, REG_CONFIG, 0xFFFF & ~led_mask)
        self.set_leds(0)

    def raw(self):
        return self.bus.read_word_data(self.address, REG_INPUT)

    def read_buttons(self):
        state = self.raw()
        return {name: not (state >> bit) & 1 for name, bit in BUTTONS.items()}

    def set_leds(self, pattern):
        """pattern: 4-bit int, bit 0 = LED 1."""
        out = 0xFFFF
        for i, bit in enumerate(LEDS):
            on = (pattern >> i) & 1
            level = (not on) if LED_ACTIVE_LOW else on
            if not level:
                out &= ~(1 << bit)
        self.bus.write_word_data(self.address, REG_OUTPUT, out)
