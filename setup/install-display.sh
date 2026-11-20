#!/bin/bash
# Hands the Display HAT Mini over to the kernel panel-mipi-dbi driver, so it shows up
# as a normal display (/dev/fb0 and a DRM device) instead of being driven from Python.
#
# Run from the repo root on the Pi: bash setup/install-display.sh
# Undo: delete the "# pokepi display" block from /boot/firmware/config.txt
#       (backup at config.txt.bak-display) and reboot.
#
# Note: once this is in, the kernel owns GPIO9 and GPIO13, so the old Python display
# tests (test_display.py, test_all.py) will fail. The pad and UPS tests still work.
set -e
cd "$(dirname "$0")/.."

python3 setup/make_panel_bin.py /tmp/panel.bin
sudo install -m 644 /tmp/panel.bin /lib/firmware/panel.bin

CFG=/boot/firmware/config.txt
sudo cp "$CFG" "$CFG.bak-display"
if ! grep -q '^# pokepi display' "$CFG"; then
    sudo tee -a "$CFG" > /dev/null <<'EOF'
# pokepi display
dtoverlay=mipi-dbi-spi,spi0-1,speed=64000000,write-only
dtparam=width=320,height=240,width-mm=41,height-mm=31
dtparam=dc-gpio=9,backlight-gpio=13
EOF
fi
echo "Done. Rebooting..."
sudo systemctl reboot
