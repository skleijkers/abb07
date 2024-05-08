import logging, asyncio

from datetime import datetime, timedelta
from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from .device.abb07device import ABB07Device


class ABB07Data:

    def __init__(self, hass, devices, abb07dev):
        self.devices = devices
        self.data = {}
        self.hass = hass
        self.unsub_schedule_update: CALLBACK_TYPE | None = None
        self._abb07dev = abb07dev

    async def update_devices(self):
        if not self.devices:
            return

        for dev in self.devices:
            dev.data_updated(self)

    @callback
    def async_schedule_update(self, minute=1):
        nxt = dt_util.utcnow() + timedelta(minutes=minute)
        self.unsub_schedule_update = async_track_point_in_utc_time(
            self.hass, self.async_update, nxt
        )

    async def _async_update(self):
        if not self._abb07dev.is_connected:
            if not await self._abb07dev.connect(self._abb07dev.adapter, self._abb07dev.addr_str, self._abb07dev.addr_type, self._abb07dev.timeout):
                logging.error(f'Could not connect to ABB07')
                return {}

        await self._abb07dev.get_sensor_data()
        return self._abb07dev.sensordata

    async def async_update(self, *_):
        data = await self._async_update()
        if data:
            self.data = data
            await self.update_devices()
        self.async_schedule_update(1)