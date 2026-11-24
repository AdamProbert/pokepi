# Common Pokepi commands. Run from the repo root on the PC (Git Bash), e.g. `just ssh`.
# `just` with no arguments lists the recipes.

set shell := ["bash", "-cu"]
set windows-shell := ["bash", "-cu"]

pi := "adam@pokepi"
# Where the repo is copied to on the Pi
pi_dir := "pokepi"

default:
    @just --list

# Open a shell on the Pi
ssh:
    ssh {{pi}}

# Copy the repo (scripts, config, tests) to the Pi
sync:
    tar -cf - --exclude=.git --exclude='docs/build-log/photos' . | ssh {{pi}} "mkdir -p {{pi_dir}} && tar -x -C {{pi_dir}}"

# Sync, then run a setup script on the Pi, e.g. `just setup enable-audio`
setup script: sync
    ssh -t {{pi}} "cd {{pi_dir}} && bash setup/{{script}}.sh"

# Sync and reinstall the RetroArch config and pad mapping, then restart RetroArch
retroarch-config: sync
    ssh -t {{pi}} "cd {{pi_dir}} && bash setup/install-retroarch-config.sh && sudo systemctl restart pokepi-retroarch"

# Sync and reinstall the pad and power services
services: sync
    ssh -t {{pi}} "cd {{pi_dir}} && bash setup/install-power.sh"

# Restart RetroArch on the panel
restart-retroarch:
    ssh -t {{pi}} "sudo systemctl restart pokepi-retroarch"

# Restart the pad service
restart-pad:
    ssh -t {{pi}} "sudo systemctl restart pokepi-pad"

# Show whether the Pokepi services are running
status:
    ssh {{pi}} "systemctl --no-pager is-active pokepi-pad pokepi-power pokepi-retroarch; cat /run/pokepi/battery.json 2>/dev/null; echo; vcgencmd measure_temp; vcgencmd get_throttled"

# Follow the logs of a service, e.g. `just logs pokepi-retroarch`
logs service="pokepi-pad":
    ssh -t {{pi}} "journalctl -u {{service}} -f"

# Copy ROMs to ~/roms on the Pi, e.g. `just roms "Pokemon Crystal.gbc"`
[positional-arguments]
roms +files:
    scp "$@" {{pi}}:roms/

# Play a test tone and voice through the speaker
speaker-test: sync
    ssh -t {{pi}} "cd {{pi_dir}} && bash pi-tests/test_speaker.sh"

# Set the system volume, e.g. `just volume 70`
volume percent:
    ssh -t {{pi}} "amixer -q sset Master {{percent}}% && sudo alsactl store"

# Show the WiFi self-check log from the boot partition
netfix-log lines="60":
    ssh {{pi}} "tail -n {{lines}} /boot/firmware/netfix.log"

# Shut the Pi down cleanly (hard power cuts can break the WiFi config)
shutdown:
    ssh -t {{pi}} "sudo systemctl poweroff"

# Reboot the Pi
reboot:
    ssh -t {{pi}} "sudo systemctl reboot"
