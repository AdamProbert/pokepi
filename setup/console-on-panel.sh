#!/bin/bash
# Puts the Linux text console on the SPI panel (fbcon=map:1).
# RetroArch's KMS driver needs the panel to already be lit by something before it
# will use it, and the console does that. You also get boot messages on the screen.
# Undo: remove " fbcon=map:1" from /boot/firmware/cmdline.txt (backup at cmdline.txt.bak-pokepi).
set -e
F=/boot/firmware/cmdline.txt
sudo cp "$F" "$F.bak-pokepi"
grep -q 'fbcon=map:1' "$F" || sudo sed -i '1 s/$/ fbcon=map:1/' "$F"
echo "Done. Rebooting..."
sudo systemctl reboot
