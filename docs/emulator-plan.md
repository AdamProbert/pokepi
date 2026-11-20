# Emulator plan

The goal is to play games on the Display HAT Mini with the Qw/ST Pad as the controller. Nothing here has been installed yet, this is the proposal.

There are 3 pieces. Something has to get frames onto the SPI screen, something has to turn the I2C pad into a normal Linux gamepad, and then an emulator sits on top of both.

## Screen

The Python test scripts push pixels themselves, which is fine for a test but far too slow for games. We want the screen to show up as a normal display device so any program can draw to it.

**fbcp / fbcp-ili9341** copies the HDMI framebuffer to the SPI screen. It's what most older guides use. It relies on the legacy Broadcom display stack, which is gone on trixie with the KMS driver, so I'd rather not.

**panel-mipi-dbi-spi** is a kernel driver for SPI panels like the ST7789. Pi OS already ships the `mipi-dbi-spi` overlay (I checked, it's in `/boot/firmware/overlays`). You give it a small firmware file with the ST7789 init commands and the screen appears as its own DRM device plus `/dev/fb0`. This is the current way to do it, so we'll use this.

It needs a `config.txt` change, roughly:

```
dtoverlay=mipi-dbi-spi,spi0-1,speed=64000000
dtparam=compatible=pokepi-st7789\0panel-mipi-dbi-spi
dtparam=width=320,height=240,width-mm=41,height-mm=31
dtparam=reset-gpio=-1,dc-gpio=9,backlight-gpio=13
```

The exact lines get worked out and tested first, then that step is run by hand on the Pi.

At 64 MHz a full 320x240 16-bit frame takes about 19 ms, so the ceiling is around 50 fps for full screen updates. Game Boy and GBA run at 60, so we might see the odd dropped frame. We'll measure it before worrying.

## Pad

The pad is an I2C chip with no interrupt line wired, so it has to be polled. A small Python service reads it about 250 times a second and feeds a virtual gamepad through `uinput` (python-evdev). To the emulator it looks like a normal USB controller. It also lights LED 1 so you can tell it's running.

Mapping is D-pad to the hat, A B X Y to the face buttons, plus to Start and minus to Select. The 4 buttons on the Display HAT Mini become L, R and a hotkey (menu, save state, quit), since the Qw/ST Pad has no shoulder buttons.

It runs as a systemd service so it starts on boot.

## Emulator

**RetroArch** is in the trixie repos (1.20.0) along with the cores we'd want. `libretro-gambatte` for Game Boy and Game Boy Color, `libretro-mgba` for GBA, plus `nestopia` and `snes9x` if you want them. These are all light enough for a Zero 2 W, GBA being the heaviest.

RetroArch's own menu (RGUI) works fine at 320x240 and doubles as the game picker, so no separate frontend to start with. GBA is 240x160 and fits the screen at 1x with borders. Game Boy is 160x144, which can scale up.

The bit I'm least sure of is pointing RetroArch at the SPI panel's DRM device instead of the HDMI one. If that turns out awkward we can render to HDMI and copy across, or just take the HDMI driver out since the case has no HDMI port anyway.

Standalone mGBA is the fallback if RetroArch is too heavy for GBA.

## Order of work

1. Write the panel firmware file and `config.txt` lines. Adam runs the install, then we check `/dev/fb0` shows a test pattern.
2. Write the pad service, install `python3-evdev`, check it with `evtest`.
3. Install RetroArch and the cores, set up the config (video device, input mapping, hotkeys, save locations).
4. Adam copies his own ROMs to `~/roms`. Nothing gets downloaded for him.
5. Start RetroArch on boot as the main screen.

All the scripts, the overlay files and the RetroArch config go in this repo under `setup/` and `pokepi/`.
