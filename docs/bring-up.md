# Bring-up notes

These are the steps that got the screen, pad and UPS working on a fresh Raspberry Pi OS trixie Lite install. They're in the order I did them.

## 1. OS and access

Flash Raspberry Pi OS trixie Lite (64-bit) with Raspberry Pi Imager. Set the hostname to `pokepi`, add the user and Wi-Fi, and turn on SSH with key login. After that `ssh adam@pokepi` works from Git Bash on the PC.

## 2. Turn on SPI and I2C

```bash
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
```

## 3. Packages

```bash
sudo apt install -y i2c-tools python3-pil python3-numpy python3-libgpiod python3-smbus2 python3-rpi-lgpio python3-venv
```

`i2cdetect` lives in `/usr/sbin`, so it's `sudo i2cdetect -y 1` (or the full path) if it isn't on your PATH.

## 4. Python venv

```bash
python3 -m venv --system-site-packages ~/pokepi-venv
~/pokepi-venv/bin/pip install --no-deps displayhatmini==0.0.2 st7789==0.0.4
```

The versions matter. `st7789` 1.x pulls in `gpiodevice`, which didn't work here. 0.0.4 uses `RPi.GPIO`, and trixie already provides that through the `rpi-lgpio` package, hence `--no-deps` and `--system-site-packages`.

## 5. Free up GPIO9 for the screen

The Display HAT Mini uses GPIO9 as its DC (data/command) pin. GPIO9 is also SPI0 MISO, so once SPI is on the kernel claims it and the screen stays blank. The screen never sends anything back, so we don't need MISO at all.

`setup/fix-gpio9.sh` builds a tiny overlay that remaps `spi0_pins` to just GPIO10 (MOSI) and GPIO11 (SCLK). It copies it to `/boot/firmware/overlays/`, backs up `config.txt` to `config.txt.bak-pokepi`, adds `dtoverlay=spi0-nomiso` and reboots.

```bash
scp setup/fix-gpio9.sh adam@pokepi:~/
ssh adam@pokepi 'bash ~/fix-gpio9.sh'
```

To undo it, remove the `dtoverlay=spi0-nomiso` line from `/boot/firmware/config.txt` (or restore the backup) and reboot.

## 6. Check the I2C devices

```bash
sudo i2cdetect -y 1
```

You should see `21` (Qw/ST Pad) and `43` (UPS HAT).

## 7. Run the tests

```bash
~/pokepi-venv/bin/python ~/test_display.py
~/pokepi-venv/bin/python ~/test_pad.py
~/pokepi-venv/bin/python ~/test_ups.py
~/pokepi-venv/bin/python ~/test_all.py
```

## Reference

### Qw/ST Pad bits

The pad is a TCA9555 16-bit expander. Inputs read 0 when a button is pressed.

| Button | Bit |
| --- | --- |
| Up | 1 |
| Left | 2 |
| Right | 3 |
| Down | 4 |
| Minus | 5 |
| Plus | 11 |
| B | 12 |
| Y | 13 |
| A | 14 |
| X | 15 |

The 4 LEDs are on bits 6, 7, 9 and 10. Other addresses (0x23, 0x25, 0x27) are picked by cutting traces on the back.

### UPS HAT

The INA219 is big-endian, so the bytes need swapping after an smbus word read. Bus voltage is register 0x02 (shift right 3, times 4 mV) and it reads about 4.21 V on a full battery. Shunt is 0.1 ohm and positive current means it's charging.

### Display HAT Mini pins

| Function | GPIO |
| --- | --- |
| SPI MOSI | 10 |
| SPI SCLK | 11 |
| Chip select | CE1 (7) |
| DC | 9 |
| Backlight | 13 |
| Button A / B / X / Y | 5 / 6 / 16 / 24 |
| RGB LED R / G / B | 17 / 27 / 22 |

## WiFi lost after power cuts

On this Raspberry Pi OS (trixie, set up by Imager through cloud-init) WiFi lives in netplan, and NetworkManager writes its own `90-NM-*.yaml` copies into `/etc/netplan`. Pulling the power shortly after boot left both of them at 0 bytes, and one empty netplan file stops netplan from generating any connections, so the Pi boots fine but never joins WiFi.

`setup/netfix.sh` lives on the boot partition as `/boot/firmware/netfix.sh` and cloud-init runs it early on every boot (a `bootcmd` in `user-data`). It turns on persistent journald logs, moves empty or unreadable netplan files to `/var/backups/netplan-broken`, rebuilds the WiFi config from `/boot/firmware/network-config` if no WiFi connection is left, and restarts NetworkManager. It logs each boot to `/boot/firmware/netfix.log`, which you can read by putting the SD card in a PC.

If the Pi is ever stuck offline anyway, change the instance id in both `cmdline.txt` (`ds=nocloud;i=...`) and `meta-data` on the boot partition. cloud-init then treats the next boot as a first boot and rewrites the network config (same user, password and WiFi; `ssh_deletekeys: false` keeps the host keys).

Shutting down properly (hold HAT B for 3 s, or `sudo poweroff`) avoids it.
