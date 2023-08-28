# Implementation of the Ablemail ABB-07 as Python object

The Ablemail ABB-07 (ABB07) is a serial to bluetooh device for communication with their chargers. See their website for the products compatible with the ABB-07 https://ablemail.co.uk/. They provide an app for IOS and Android for readout and adjusting settings.

This Python object is only for readout and has been tested on the AMT12-2 Tickle charger.

# Requirements

- The bleak library, can be installed with "pip install bleak"
- Bluetooth device set to passive scanning

# Test script

With the provided abb07test.py the ABB-07 can be tested. It will try to make connection with the ABB-07 and does one reading. It will print this reading as a JSON string.

The testscript needs two arguments, the bluetooth adapter (hci0) and the bluetooth device id of the ABB-07 (XX:XX:XX:XX:XX:XX).
