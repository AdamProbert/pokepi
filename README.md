# Pokepi

Pokepi is a handheld games console I'm designing, building and programming myself. It's a Raspberry Pi Zero 2 W in a 3D printed case with a small SPI screen, an I2C gamepad, a battery HAT and a speaker.

This repo has the setup scripts, test scripts and notes from getting the hardware working. The case CAD isn't in here (yet).

## Hardware

| Part | What it does | How it connects |
| --- | --- | --- |
| Raspberry Pi Zero 2 W | The computer. 4 cores at 1 GHz, 512 MB RAM | |
| Pimoroni Display HAT Mini | 2.0" 320x240 IPS screen (ST7789), 4 buttons, RGB LED | SPI0 CE1, DC on GPIO9, backlight on GPIO13 |
| Pimoroni Qw/ST Pad | D-pad, ABXY, plus and minus, 4 LEDs (TCA9555 expander) | I2C bus 1, address 0x21 |
| Waveshare UPS HAT (C) | Battery, charging, voltage and current (INA219) | I2C bus 1, address 0x43 |
| MAX98357A I2S amp | 3 W class D mono amp for the speaker | I2S on GPIO 18, 19 and 21, plus 5V and GND |
| 20 x 30 mm speaker | 8 ohm 1 W, 4.6 mm thick | Bare leads into the amp's terminals |

The screen isn't HDMI, everything that draws to it goes over SPI.

The full parts list, including the case screws and inserts, is in [docs/parts.md](docs/parts.md). Audio wiring is in [docs/audio.md](docs/audio.md).

## Software on the Pi

- Raspberry Pi OS trixie Lite (64-bit), headless, kernel 6.18
- SPI and I2C turned on
- A custom `spi0-nomiso` overlay so the screen can use GPIO9 (see below)
- The screen driven by the kernel `panel-mipi-dbi` driver once the emulator is set up
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
- `pokepi/pad_gamepad.py` turns the pad and HAT buttons into a virtual gamepad.
- `setup/` also has the install scripts for the screen driver, pad service and RetroArch.
- `config/` has the RetroArch settings and pad mapping.

## Common commands

The `justfile` has shortcuts for the usual jobs from the PC, such as `just ssh`, `just sync`, `just setup enable-audio`, `just roms "game.gbc"`, `just restart-retroarch`, `just status` and `just netfix-log`. Run `just` to list them all. It needs [just](https://github.com/casey/just) (`winget install Casey.Just`) and runs its recipes in Git Bash.

## Running the tests

Copy the tests across and run them with the venv's Python.

```bash
scp pi-tests/*.py adam@pokepi:~/
ssh adam@pokepi
~/pokepi-venv/bin/python ~/test_all.py
```

Ctrl+C quits.

## Playing games

RetroArch runs on the screen with the GB/GBC (gambatte) and GBA (mGBA) cores. How it fits together and how to set it up is in [docs/emulator.md](docs/emulator.md).

## Build log

Photos and notes from the build are in [docs/build-log](docs/build-log/README.md).
