#!/bin/bash
# Copies the Pokepi RetroArch config and pad autoconfig into place. No sudo needed.
# Run from the repo root on the Pi: bash setup/install-retroarch-config.sh
set -e
cd "$(dirname "$0")/.."
RA=~/.config/retroarch
mkdir -p "$RA/autoconfig/udev" ~/roms ~/saves ~/states
[ -f "$RA/retroarch.cfg" ] && cp "$RA/retroarch.cfg" "$RA/retroarch.cfg.bak"
sed "s#~/#$HOME/#g" config/retroarch.cfg > "$RA/retroarch.cfg"
cp "config/autoconfig/Pokepi Pad.cfg" "$RA/autoconfig/udev/"
echo "joypad_autoconfig_dir = \"$RA/autoconfig\"" >> "$RA/retroarch.cfg"
echo "Installed to $RA"
