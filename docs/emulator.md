# Emulator

Pokepi plays games with RetroArch, drawn on the Display HAT Mini with the Qw/ST Pad as the controller. Game Boy and Game Boy Color use the gambatte core, GBA uses mGBA.

There are 3 pieces. The kernel drives the screen, a small service turns the pad into a normal Linux gamepad and RetroArch sits on top of both. No ROMs are included, you bring your own.

## Screen

The Python test scripts push pixels to the screen themselves. That's fine for a test but far too slow for games, so we want the screen to show up as a normal display that anything can draw to.

The old way to do this is fbcp, which copies the HDMI output to the SPI screen. It needs the legacy Broadcom display stack, which is gone on trixie, so that's out.

Instead we use `panel-mipi-dbi-spi`, a kernel driver for SPI panels like the ST7789. Pi OS already ships the `mipi-dbi-spi` overlay. You give it a small firmware file (`/lib/firmware/panel.bin`) with the panel's init commands and the screen appears as DRM `card0` plus `/dev/fb1`. The HDMI side (vc4) becomes `card1` but its GPU still does the rendering.

`setup/make_panel_bin.py` builds the firmware file. It uses the same init sequence as Pimoroni's st7789 library, except the panel does the 180 degree rotation itself (MADCTL 0xB0) where the library did it in software. `setup/install-display.sh` installs it and adds this to `config.txt`.

```
dtoverlay=mipi-dbi-spi,spi0-1,speed=64000000,write-only
dtparam=width=320,height=240,width-mm=41,height-mm=31
dtparam=dc-gpio=9,backlight-gpio=13
```

There's one catch. RetroArch's KMS driver found the panel but refused to use it ("Couldn't find DRM encoder") because nothing had switched it on yet. Putting the text console on the panel with `fbcon=map:1` in `cmdline.txt` fixes that, and you get boot messages on the screen as a bonus. `setup/console-on-panel.sh` adds it.

At 64 MHz a full 320x240 16-bit frame takes about 19 ms, so the ceiling is around 50 fps for full screen updates. Games run at 60, so expect the odd dropped frame. We haven't measured it properly yet.

Once the kernel owns the screen the old Python display tests stop working, since it holds GPIO9 and GPIO13.

## Pad

The pad is an I2C chip with no interrupt line wired, so it has to be polled. `pokepi/pad_gamepad.py` reads it 250 times a second and feeds a virtual gamepad called "Pokepi Pad" through uinput. It also reads the 4 buttons on the Display HAT Mini. It runs as root from `pokepi-pad.service` and lights the pad's first LED while it's running.

| Button | Gamepad | RetroArch |
| --- | --- | --- |
| D-pad | DPAD | D-pad |
| A / B / X / Y | EAST / SOUTH / NORTH / WEST | A / B / X / Y |
| Plus | START | Start |
| Minus | SELECT | Select |
| HAT A (left, top) | TL | L |
| HAT X (right, top) | TR | R |
| HAT B (left, bottom) | MODE | Menu (hold 3 s to shut down) |
| HAT Y (right, bottom) | THUMBL | Fast forward toggle |

Save states, load states and quitting a game are all in the menu.

`config/autoconfig/Pokepi Pad.cfg` tells RetroArch which button number is which. The udev driver numbers buttons in key code order, the order is written at the top of that file.

## RetroArch

RetroArch 1.20 and the cores come from the trixie repos (`retroarch`, `libretro-gambatte`, `libretro-mgba`). It uses the `gl` video driver with the `kms` context, which renders on the VideoCore GPU (OpenGL ES 2.0) and shows it on the panel. RGUI is the menu and the game picker.

`config/retroarch.cfg` only has the settings that differ from the defaults. Audio goes to the I2S amp, see [audio.md](audio.md). Saves go in `~/saves`, states in `~/states` and it auto-saves a state when you quit a game.

`pokepi-retroarch.service` starts it on tty1 at boot and restarts it if it quits.

## Power

There are 3 ways to shut down safely.

- **Hold HAT B for 3 seconds.** The pad LEDs fill up as a countdown, let go before all 4 are lit to cancel. This is handled by the pad service, which runs as root.
- **RetroArch's menu**, Main Menu then Shutdown. RetroArch runs as adam, so a polkit rule (`setup/50-pokepi-power.rules`) lets adam power off and reboot without a password.
- **Low battery.** `pokepi/power_monitor.py` reads the UPS every 5 seconds. If the battery stays under 3.30 V for 30 seconds while discharging, it powers off. 3.30 V is roughly 10% left on this LiPo, so there's some margin before the UPS's own cutoff. It also writes the latest reading to `/run/pokepi/battery.json`, which a battery icon could use later.

After the Pi has shut down the UPS still powers it, so flip the switch on the UPS once the green light stops flashing. `setup/install-power.sh` installs all of this.

## Setting it up from scratch

After the [bring-up steps](bring-up.md), copy the repo to `~/pokepi` on the Pi and run these from there. The 2 that change boot settings reboot the Pi when they finish.

```bash
bash setup/install-pad-and-emulator.sh
bash setup/install-display.sh          # reboots
bash setup/console-on-panel.sh         # reboots
bash setup/install-retroarch-config.sh
bash setup/enable-autostart.sh
bash setup/install-power.sh
```

Then copy your ROMs into `~/roms`.

## Still to do

- Sound. Wiring and setup for the I2S amp and speaker are in [audio.md](audio.md).
- Measuring the real frame rate on GBA games.
- Showing the battery level somewhere, probably a small overlay.
