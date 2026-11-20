#!/bin/bash
# Starts RetroArch on the panel at boot (and restarts it if it quits).
# Run from the repo root on the Pi: bash setup/enable-autostart.sh
# Undo: sudo systemctl disable --now pokepi-retroarch && sudo systemctl enable --now getty@tty1
set -e
cd "$(dirname "$0")/.."
sudo install -m 644 setup/pokepi-retroarch.service /etc/systemd/system/pokepi-retroarch.service
sudo systemctl daemon-reload
sudo systemctl disable getty@tty1.service || true
sudo systemctl enable --now pokepi-retroarch.service
systemctl --no-pager status pokepi-retroarch | head -5
