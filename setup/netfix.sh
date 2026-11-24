#!/bin/bash
# Pokepi WiFi self-check. Runs early on every boot (cloud-init bootcmd).
# Logs the WiFi config state to /boot/firmware/netfix.log and, if the WiFi
# config is missing or broken, moves broken files aside and rebuilds it from
# /boot/firmware/network-config.
LOG=/boot/firmware/netfix.log
exec >> "$LOG" 2>&1
echo "===== $(date '+%F %T') boot $(cat /proc/sys/kernel/random/boot_id)"

# Keep logs across reboots so the next failure can be diagnosed.
if [ ! -f /etc/systemd/journald.conf.d/pokepi-persistent.conf ]; then
    mkdir -p /etc/systemd/journald.conf.d /var/log/journal
    printf '[Journal]\nStorage=persistent\n' > /etc/systemd/journald.conf.d/pokepi-persistent.conf
    systemctl restart systemd-journald && echo "enabled persistent journal"
fi

echo "-- /etc/netplan"
ls -la --time-style=+%F_%T /etc/netplan
echo "-- generated NM connections"
ls -la /run/NetworkManager/system-connections 2>&1

broken=0
python3 -c 'import yaml' 2>/dev/null && HAVE_YAML=1 || HAVE_YAML=0
yaml_ok() { [ "$HAVE_YAML" = 0 ] || python3 -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); assert isinstance(d,dict)' "$1" 2>/dev/null; }
for f in /etc/netplan/*.yaml; do
    [ -e "$f" ] || continue
    if [ ! -s "$f" ] || ! yaml_ok "$f"; then
        echo "BROKEN: $f ($(stat -c %s "$f") bytes)"
        mkdir -p /var/backups/netplan-broken
        mv "$f" "/var/backups/netplan-broken/$(basename "$f").$(date +%s)"
        broken=1
    fi
done
netplan generate || { echo "netplan generate failed"; broken=1; }

if ! grep -lqs 'type=wifi' /run/NetworkManager/system-connections/*.nmconnection; then
    echo "no WiFi connection found, rebuilding from boot partition"
    install -m 600 /boot/firmware/network-config /etc/netplan/50-pokepi-wifi.yaml
    broken=1
fi

if [ "$broken" = 1 ]; then
    netplan generate && echo "regenerated"
    systemctl --no-block restart NetworkManager.service && echo "queued NetworkManager restart"
else
    echo "WiFi config looks fine"
fi
sync
