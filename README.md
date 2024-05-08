# Implementation of the Ablemail ABB-07 as Home Assistant integration

The Ablemail ABB-07 (ABB07) is a serial to bluetooh device for communication with their chargers. See their website for the products compatible with the ABB-07 https://ablemail.co.uk/. They provide an app for IOS and Android for readout and adjusting settings.

This Home Assistant integration is only for readout and has been tested on the AMT12-2 Tickle charger.

## Requirements

- The bleak library, can be installed with "pip install bleak" (unfortunately the requirements don't work due to conflicting dependancies).
- Bluetooth device set to passive scanning in Home Assistant.
- Low power mode of the ABB-07 disabled, as the wake-up call isn't implemented.

## Installation

Git clone this repository in config/custom_components/abb07 and add the following lines to the configuration.yaml of Home Assistant:

```bash
abb07:
  adapter: "hci0" # Bluetooth adapter name
  device: "XX:XX:XX:XX:XX:XX" # Identifier of ABB-07 bluetooth module (MAC address)
```
