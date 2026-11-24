#!/bin/bash
# Turns on the MAX98357A I2S amp (BCLK GPIO18, LRCLK GPIO19, DIN GPIO21) and
# makes it the default sound card. Needs a reboot afterwards.
# Run from the repo root on the Pi: bash setup/enable-audio.sh
set -e
cd "$(dirname "$0")/.."
CFG=/boot/firmware/config.txt

sudo cp -n "$CFG" "$CFG.bak-audio" || true

# The Zero 2 W has no analogue out, and HDMI audio only confuses card numbering.
sudo sed -i 's/^dtparam=audio=on/dtparam=audio=off/' "$CFG"

# no-sdmode: the SD pin is left unconnected, so the amp is always on.
if ! grep -q '^dtoverlay=max98357a' "$CFG"; then
    echo 'dtoverlay=max98357a,no-sdmode' | sudo tee -a "$CFG" > /dev/null
fi

sudo install -m 644 setup/asound.conf /etc/asound.conf
echo "Done. Reboot, then run: bash pi-tests/test_speaker.sh"
