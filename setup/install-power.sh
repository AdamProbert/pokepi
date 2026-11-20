#!/bin/bash
# Installs the shutdown button (in the pad service), the low battery monitor and
# lets RetroArch's own Shutdown and Restart menu options work.
# Run from the repo root on the Pi: bash setup/install-power.sh
set -e
cd "$(dirname "$0")/.."

sudo install -D -m 755 pokepi/pad_gamepad.py /opt/pokepi/pad_gamepad.py
sudo install -m 755 pokepi/power_monitor.py /opt/pokepi/power_monitor.py
sudo install -m 644 setup/pokepi-power.service /etc/systemd/system/pokepi-power.service

# RetroArch runs as adam and calls "shutdown". This lets adam power off and reboot
# without a password, even with an SSH session open.
if ! command -v pkaction > /dev/null; then
    sudo apt-get install -y --no-install-recommends polkitd
fi
sudo install -D -m 644 setup/50-pokepi-power.rules /etc/polkit-1/rules.d/50-pokepi-power.rules

sudo systemctl daemon-reload
sudo systemctl enable --now pokepi-power.service
sudo systemctl restart pokepi-pad.service polkit.service
echo
systemctl --no-pager is-active pokepi-pad pokepi-power
cat /run/pokepi/battery.json 2>/dev/null && echo
