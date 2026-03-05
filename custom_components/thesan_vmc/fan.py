"""
FILE: custom_components/thesan_vmc/fan.py

Supporto Fan per Thesan VMC.
"""
import logging
from typing import Any
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from . import DOMAIN, ThesanDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (1, 5)  # Range velocità quando acceso

# Modalità supportate
PRESET_MODE_MANUAL = "Manuale"
PRESET_MODE_AUTO = "Auto"
PRESET_MODE_BYPASS = "Bypass"

PRESET_MODES = [PRESET_MODE_MANUAL, PRESET_MODE_AUTO, PRESET_MODE_BYPASS]

# Mappatura modalità nome -> numero (CORRETTA in base ai test)
MODE_TO_VALUE = {
    PRESET_MODE_AUTO: 0,      # Auto = 0 (verificato con test)
    PRESET_MODE_MANUAL: 1,    # Manuale = 1 (verificato con test)
    PRESET_MODE_BYPASS: 2,    # Bypass = 2
}

# Mappatura modalità numero -> nome
VALUE_TO_MODE = {
    0: PRESET_MODE_AUTO,
    1: PRESET_MODE_MANUAL,
    2: PRESET_MODE_BYPASS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura il fan da config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ThesanVMCFan(coordinator, entry)])


class ThesanVMCFan(CoordinatorEntity, FanEntity):
    """Rappresenta il VMC Thesan come Fan entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = PRESET_MODES

    def __init__(
        self,
        coordinator: ThesanDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Thesan",
            "model": "AIRCARE VMC",
        }

    @property
    def is_on(self) -> bool:
        """Ritorna True se il fan è acceso."""
        speed = self.coordinator.data.get("speed", 0)
        return speed > 0

    @property
    def percentage(self) -> int | None:
        """Ritorna la velocità corrente come percentuale."""
        speed = self.coordinator.data.get("speed")
        if speed is None:
            return None
        
        if speed == 0:
            return 0
        
        return ranged_value_to_percentage(SPEED_RANGE, speed)

    @property
    def preset_mode(self) -> str | None:
        """Ritorna la modalità corrente."""
        mode_value = self.coordinator.data.get("mode")
        _LOGGER.debug("preset_mode chiamato, mode_value: %s", mode_value)
        if mode_value is None:
            return None
        return VALUE_TO_MODE.get(mode_value, PRESET_MODE_MANUAL)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Imposta la modalità preset."""
        mode_value = MODE_TO_VALUE.get(preset_mode)
        if mode_value is not None:
            await self.coordinator.async_set_mode(mode_value)

    @property
    def speed_count(self) -> int:
        """Ritorna il numero di velocità supportate."""
        return SPEED_RANGE[1]

    async def async_set_percentage(self, percentage: int) -> None:
        """Imposta la velocità del fan."""
        if percentage == 0:
            speed = 0
        else:
            speed = int(percentage_to_ranged_value(SPEED_RANGE, percentage))
        
        await self.coordinator.async_set_speed(speed)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Accende il fan impostando una velocità."""
        if percentage is None:
            # Se già acceso, mantieni velocità corrente, altrimenti imposta velocità 2
            current_speed = self.coordinator.data.get("speed", 0)
            speed = current_speed if current_speed > 0 else 2
        else:
            speed = int(percentage_to_ranged_value(SPEED_RANGE, percentage))
            # Assicurati che non sia 0 quando si vuole accendere
            if speed == 0:
                speed = 1
        
        await self.coordinator.async_set_speed(speed)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Spegne il fan impostando velocità a 0."""
        await self.coordinator.async_set_speed(0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Ritorna attributi extra."""
        attrs = {}
        
        mode_value = self.coordinator.data.get("mode")
        if mode_value is not None:
            attrs["mode_value"] = mode_value
            attrs["mode_name"] = VALUE_TO_MODE.get(mode_value, "Sconosciuto")
        
        raw_speed = self.coordinator.data.get("speed")
        if raw_speed is not None:
            attrs["raw_speed"] = raw_speed
        
        return attrs