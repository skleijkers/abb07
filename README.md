# Home Assistant integration of the Ablemail ABB-07

The Ablemail ABB-07 (ABB07) is a serial to bluetooh device for communication with their chargers. See their website for the products compatible with the ABB-07 https://ablemail.co.uk/. They provide an app for IOS and Android for readout and adjusting settings.

This Home Assistant integration is only for readout and has been tested on the AMT12-2 Tickle charger.

## Requirements

- Bluetooth device set to passive scanning in Home Assistant.
- Low power mode of the ABB-07 disabled, as the wake-up call isn't implemented.

## Installation

Open a terminal in Home Assistant and git clone this repository in ~/config/custom_components/abb07

```bash
git clone https://github.com/skleijkers/abb07 ~/config/custom_components/abb07
```

Add the following lines to the configuration.yaml of Home Assistant:

```bash
abb07:
  adapter: "hci0" # Bluetooth adapter name
  device: "XX:XX:XX:XX:XX:XX" # Identifier of ABB-07 bluetooth module (MAC address)
```
