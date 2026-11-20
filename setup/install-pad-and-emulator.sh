#!/bin/bash
# Installs the pad service, RetroArch and the GB/GBC/GBA cores.
# Run from the repo root on the Pi: bash setup/install-pad-and-emulator.sh
set -e
cd "$(dirname "$0")/.."

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    python3-evdev python3-smbus2 python3-rpi-lgpio evtest \
    retroarch libretro-gambatte libretro-mgba

# Pad -> virtual gamepad service
sudo install -D -m 755 pokepi/pad_gamepad.py /opt/pokepi/pad_gamepad.py
sudo install -m 644 setup/pokepi-pad.service /etc/systemd/system/pokepi-pad.service
echo uinput | sudo tee /etc/modules-load.d/uinput.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now pokepi-pad.service

mkdir -p ~/roms ~/saves ~/states
echo
echo "Done. 'systemctl status pokepi-pad' should say active (running)."
echo "Check buttons with: sudo evtest   (pick 'Pokepi Pad')"
