# Home Assistant integration of the Ablemail ABB-07

The Ablemail ABB-07 (ABB07) is a serial to bluetooh device for communication with their chargers. See their website for the products compatible with the ABB-07 https://ablemail.co.uk/. They provide an app for IOS and Android for readout and adjusting settings.

This Home Assistant integration is only for readout and has been tested on the AMT12-2 Tickle charger.

The integration provides all available sensors from the ABB-07 / charger, depending on the type of charger attached not all the sensors will provide a valid output:

- abb07_liv: Local Input Voltage
- abb07_riv: Remote Input Voltage
- abb07_lov: Local Output Voltage
- abb07_rov: Remote Output Voltage
- abb07_li: Local current
- abb07_mt: Microcontroller Temperature
- abb07_ft: Mosfet Temperature
- abb07_rt: Remote Temperature
- abb07_vtrgt: Target Voltage
- abb07_vfloat: Float Input Voltage
- abb07_vboost: Boost Input Voltage
- abb07_runningtime: Time in seconds the charger has run (provided current between input and output)
- abb07_runningtime: Uptime of the charger in seconds


## Requirements

- Bluetooth device set to passive scanning in Home Assistant.
- Low power mode of the charger disabled, as the wake-up call isn't implemented.

## Installation

Open a terminal in Home Assistant and git clone this repository in ~/config/custom_components/abb07

```bash
git clone https://github.com/skleijkers/abb07 ~/config/custom_components/abb07
```

Add the following lines to the configuration.yaml of Home Assistant:

```bash
abb07:
  device: "XX:XX:XX:XX:XX:XX" # Identifier of ABB-07 bluetooth module (MAC address layout)
  keep_connected: False # Keep the connection to the ABB-07 open or close it after each request (optional, default: False)
```

### Setting the bluetooth device in Home Assistant to passive scanning

- Open your Home Assistant.
- Go to Configuration -> Devices & services.
- Click on Bluetooth (for further configuration of the bluetooth integration).
- Click on Configure link.
- Check the Passive scanning and click on Send.

### Disable the low power mode on the ABB-07

- Open the Ablemail Device Manager for Android or IOS on your phone.
- Connect to the ABB-07 (while in reach of the device and after the device has just been powered on).
- Go to Device Settings and change the Low Power mode to Disabled.
- Send the settings to the device.

> [!WARNING]
> After changing the mode setting of the charger, the device settings are reset to the default and the Low Power mode is enabled again. 

## Documentation

### keep_connected option

Default the keep_connected option is set to False, thus opening and closing the connection to the ABB-07 on every request for sensor data. In this mode it's possible to use the app alongside the integration as it is not possible to have two open connections to the ABB-07.

While the app has the connection open to the ABB-07, the integration will not be able to connect to the ABB-07 and the reading(s) will be skipped. After disconnecting the app, the integration will be able to connect again and continue with the readings.

Setting the keep_connected option to True gives the integration exclusive access to the ABB-07 and no readings will be missed. Default (at the moment not configurable) every 1 minute the integration will try a reading and update the Entities in Home Assistant.