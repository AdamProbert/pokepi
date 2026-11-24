# Parts list

Everything that goes into one Pokepi. Prices are what was paid or seen in UK shops in November 2026.

## Electronics

| Part | Qty | Notes |
| --- | --- | --- |
| Raspberry Pi Zero 2 W | 1 | The computer. Needs a soldered 40-pin header for the Display HAT. |
| microSD card | 1 | Raspberry Pi OS trixie Lite (64-bit). |
| Pimoroni Display HAT Mini | 1 | 2.0" 320x240 IPS (ST7789), 4 buttons, RGB LED, Qw/ST socket. Sits on top of the Pi. |
| Pimoroni Qw/ST Pad | 1 | D-pad, ABXY, plus and minus, 4 LEDs (TCA9555, I2C 0x21). 58 x 25 mm. |
| Qw/ST (JST-SH 4-pin) cable | 1 | Pad to the Qw/ST socket on the Display HAT. |
| Waveshare UPS HAT (C) for Pi Zero | 1 | Battery, USB-C charging, power switch and INA219 monitor (I2C 0x43). Sits under the Pi on pogo pins. |
| LiPo battery | 1 | The 1000 mAh cell that comes with the UPS HAT. |
| MAX98357A I2S class D amp breakout | 1 | About 18 x 19 mm. A generic clone board (2-pack for about £6.69); the Adafruit 3006 has the same pins. |
| 20 x 30 mm 8 ohm 1 W speaker, bare leads | 1 | eMagTech 10-pack. 4.6 mm thick. |
| Hook-up wire | ~5 x 10 cm | Amp to the header joints under the Pi (5V, GND, GPIO 18, 19, 21). See [audio.md](audio.md). |

The stack (Display HAT, Pi and UPS HAT with its battery) is 33 mm deep and 66 mm wide.

## Enclosure

The case is the Strata 2 design, printed in PLA on a Bambu P1S (FDM).

Printed parts: front shell, rear shell, screen bezel, pad bracket, D-pad, A/B/X/Y keys, plus and minus keys, 4 HAT keys and 5 speaker slash inserts.

| Hardware | Qty | Where |
| --- | --- | --- |
| M2.5 brass standoffs | 4 | Between the boards in the stack (come with the HATs) |
| M2.5 x 6 pan head screws | 4 | From the back of the rear shell into the stack standoffs |
| M3 heat-set inserts | 4 | Front shell closure posts (4.2 mm pocket, 9.7 mm deep) |
| M3 x 10 socket head screws | 4 | From the back into the heat-set inserts to close the case |
| M3 x 8 screws | 2 | Pad bracket into the plastic posts |
| CA glue | | Screen bezel and slash inserts |
| Hot glue | | Amp and speaker in their cradles |
