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
)

CONFIG_SCHEMA = vol.Schema(
	{
		DOMAIN: vol.Schema({
                    vol.Required(CONF_DEVICE): cv.string,
		})
	},
	extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    conf = config[DOMAIN]
    device = conf.get(CONF_DEVICE)

    if DOMAIN not in config:
        return False

    abb07dev = ABB07Device(device, 10.0)
    hass.data[DOMAIN] = abb07dev

    hass.async_create_task(async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config))
    return True
