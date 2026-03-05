"""
FILE: custom_components/thesan_vmc/sensor.py

Supporto Sensor per Thesan VMC.
"""
import logging
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, ThesanDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori da config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        ThesanTemperatureSensor(coordinator, entry, "temp_int", "Temperatura Interna"),
        ThesanTemperatureSensor(coordinator, entry, "temp_ext", "Temperatura Esterna"),
        ThesanHumiditySensor(coordinator, entry),
        ThesanFilterSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors)


class ThesanSensorBase(CoordinatorEntity, SensorEntity):
    """Classe base per i sensori Thesan."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ThesanDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_name: str,
    ) -> None:
        """Inizializza il sensore."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = sensor_name
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Thesan",
            "model": "AIRCARE VMC",
        }


class ThesanTemperatureSensor(ThesanSensorBase):
    """Sensore temperatura per Thesan VMC."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: ThesanDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_name: str,
    ) -> None:
        """Inizializza il sensore temperatura."""
        super().__init__(coordinator, entry, sensor_key, sensor_name)

    @property
    def native_value(self) -> float | None:
        """Ritorna il valore del sensore."""
        return self.coordinator.data.get(self._sensor_key)


class ThesanHumiditySensor(ThesanSensorBase):
    """Sensore umidità per Thesan VMC."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: ThesanDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il sensore umidità."""
        super().__init__(coordinator, entry, "humidity", "Umidità Interna")

    @property
    def native_value(self) -> float | None:
        """Ritorna il valore del sensore."""
        return self.coordinator.data.get("humidity")


class ThesanFilterSensor(ThesanSensorBase):
    """Sensore giorni filtro rimanenti per Thesan VMC."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_icon = "mdi:air-filter"

    def __init__(
        self,
        coordinator: ThesanDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il sensore filtro."""
        super().__init__(coordinator, entry, "filter_days", "Giorni Filtro Rimanenti")

    @property
    def native_value(self) -> int | None:
        """Ritorna il valore del sensore."""
        return self.coordinator.data.get("filter_days")