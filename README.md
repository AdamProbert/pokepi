# Pokepi

Pokepi is a handheld games console I'm designing, building and programming myself. It's a Raspberry Pi Zero 2 W in a 3D printed case with a small SPI screen, an I2C gamepad and a battery HAT.

This repo has the setup scripts, test scripts and notes from getting the hardware working. The case CAD isn't in here (yet).

## Hardware

| Part | What it does | How it connects |
| --- | --- | --- |
| Raspberry Pi Zero 2 W | The computer. 4 cores at 1 GHz, 512 MB RAM | |
| Pimoroni Display HAT Mini | 2.0" 320x240 IPS screen (ST7789), 4 buttons, RGB LED | SPI0 CE1, DC on GPIO9, backlight on GPIO13 |
| Pimoroni Qw/ST Pad | D-pad, ABXY, plus and minus, 4 LEDs (TCA9555 expander) | I2C bus 1, address 0x21 |
| Waveshare UPS HAT (C) | Battery, charging, voltage and current (INA219) | I2C bus 1, address 0x43 |

The screen isn't HDMI, everything that draws to it goes over SPI.

## Software on the Pi

- Raspberry Pi OS trixie Lite (64-bit), headless, kernel 6.18
- SPI and I2C turned on
- A custom `spi0-nomiso` overlay so the screen can use GPIO9 (see below)
- Python venv at `~/pokepi-venv`, made with `--system-site-packages`
- `displayhatmini` 0.0.2 and `st7789` 0.0.4 in the venv

Full steps are in [docs/bring-up.md](docs/bring-up.md).

## What's in here

- `setup/fix-gpio9.sh` builds and installs the `spi0-nomiso` overlay, then reboots.
- `pi-tests/qwstpad_raw.py` is a small driver for the Qw/ST Pad using smbus2.
- `pi-tests/test_display.py` draws colour bars and lights the RGB LED from the HAT buttons.
- `pi-tests/test_pad.py` prints pad buttons and raw bits as you press them.
- `pi-tests/test_ups.py` prints battery voltage, current and a rough percentage.
- `pi-tests/test_all.py` puts the pad and battery on the screen together.

## Running the tests

Copy the tests across and run them with the venv's Python.

```bash
scp pi-tests/*.py adam@pokepi:~/
ssh adam@pokepi
~/pokepi-venv/bin/python ~/test_all.py
```

Ctrl+C quits.

## Next up

Getting an emulator running on the screen with the pad as the controller. The plan is in [docs/emulator-plan.md](docs/emulator-plan.md).
