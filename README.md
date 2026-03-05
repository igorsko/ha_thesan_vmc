# Thesan VMC - Home Assistant Custom Component

This is a custom component for Home Assistant to integrate with Thesan VMC (Controlled Mechanical Ventilation) devices.

## Features
- **Local Control**: Connects locally to the Thesan device via its local IP address.
- **Fan Control**: Control the fan speed and mode (Auto, Manual, Bypass).
- **Sensors**: Monitor internal/external temperature, internal humidity, and remaining filter days.

## Installation
1. Copy the `ha_thesan_vmc` folder to your Home Assistant `custom_components` directory as `thesan_vmc`.
2. Restart Home Assistant.
3. Add the integration from the Home Assistant UI via **Settings** -> **Devices & Services** -> **Add Integration** and search for "Thesan VMC".
4. Enter the local IP address/hostname of your Thesan VMC device.

## Configuration
During the configuration flow, you will be prompted to enter the **Host** IP address of the VMC device. Ensure the device is reachable from your Home Assistant instance over the local network.
