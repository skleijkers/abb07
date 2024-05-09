from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .device.abb07device import ABB07Device

from homeassistant.const import (
    Platform,
    CONF_DEVICE,
)

from .const import (
    DOMAIN,
    CONF_KEEP_CONNECTED,
)

CONFIG_SCHEMA = vol.Schema(
	{
		DOMAIN: vol.Schema({
                    vol.Required(CONF_DEVICE): cv.string,
                    vol.Optional(CONF_KEEP_CONNECTED, default=False): cv.boolean,
		})
	},
	extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    conf = config[DOMAIN]
    device = conf.get(CONF_DEVICE)
    keep_connected = conf.get(CONF_KEEP_CONNECTED)

    if DOMAIN not in config:
        return False

    abb07dev = ABB07Device(device, keep_connected)
    hass.data[DOMAIN] = abb07dev

    hass.async_create_task(async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config))
    return True
