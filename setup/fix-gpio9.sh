#!/bin/bash
# Frees GPIO9 (Display HAT Mini DC pin) from the SPI driver by remapping spi0 to pins 10/11 only.
# Undo: remove the "dtoverlay=spi0-nomiso" line from /boot/firmware/config.txt (backup at config.txt.bak-pokepi).
set -e
cat > /tmp/spi0-nomiso.dts <<'EOF'
/dts-v1/;
/plugin/;
/ {
    compatible = "brcm,bcm2835";
    fragment@0 {
        target = <&spi0_pins>;
        __overlay__ {
            brcm,pins = <10 11>;
            brcm,function = <4>;
        };
    };
};
EOF
dtc -@ -q -I dts -O dtb -o /tmp/spi0-nomiso.dtbo /tmp/spi0-nomiso.dts
sudo cp /tmp/spi0-nomiso.dtbo /boot/firmware/overlays/
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.bak-pokepi
grep -q '^dtoverlay=spi0-nomiso' /boot/firmware/config.txt || echo 'dtoverlay=spi0-nomiso' | sudo tee -a /boot/firmware/config.txt
echo "Done. Rebooting..."
sudo systemctl reboot
