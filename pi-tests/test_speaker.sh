#!/bin/bash
# Checks the I2S amp shows up and plays a test tone and some speech.
set -e
echo "== Sound cards"
aplay -l
echo
echo "== Setting volume to 60%"
# The Master control only appears after something has played once.
speaker-test -D default -c 2 -t sine -f 440 -l 1 -p 1 > /dev/null 2>&1 || true
amixer -q sset Master 60% || true
echo "== Tone: left, right (5 s)"
speaker-test -D default -c 2 -t sine -f 440 -l 1
echo "== Voice test"
speaker-test -D default -c 2 -t wav -l 1
