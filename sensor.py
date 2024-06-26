from __future__ import annotations

from homeassistant.const import UnitOfElectricPotential, UnitOfElectricCurrent, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN
from .util import ABB07Data
from .device.abb07device import ABB07Device

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription( # Local input voltage
        key="liv",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Remote input voltage
        key="riv",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Local output voltage
        key="lov",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Remote output voltage
        key="rov",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Local current
        key="li",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Microcontroller temperature
        key="mt",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Mosfet temperature
        key="ft",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Remote temperature
        key="rt",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Target voltage
        key="vtrgt",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Float voltage
        key="vfloat",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Boost voltage
        key="vboost",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription( # Device running in seconds
        key="devicerunning",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription( # Device uptime in seconds
        key="deviceuptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None,) -> None:

    if discovery_info is None:
        return

    entities = [
        ABB07Sensor(description)
        for description in SENSOR_TYPES
    ]

    abb07dev = hass.data[DOMAIN]
    abb07data = ABB07Data(hass, entities, abb07dev)
    await abb07data.async_update()
    async_add_entities(entities)


class ABB07Sensor(SensorEntity):

    _attr_entity_registry_enabled_default = True
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, description: SensorEntityDescription) -> None:
        self.entity_description = description

    @callback
    def data_updated(self, abb07data: ABB07Data):
        sensor_type = self.entity_description.key
        self._attr_native_value = abb07data.data[sensor_type]
        if self.hass:
            self.async_write_ha_state()

    @property
    def name(self) -> str:
        return DOMAIN + "_" + self.entity_description.key

    @property
    def unique_id(self) -> str:
        return DOMAIN + "_" + self.entity_description.key
