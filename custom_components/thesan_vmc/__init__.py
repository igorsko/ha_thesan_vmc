"""
FILE: custom_components/thesan_vmc/__init__.py

Integrazione Thesan VMC per Home Assistant.
"""
import logging
import aiohttp
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

DOMAIN = "thesan_vmc"
PLATFORMS = [Platform.FAN, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura l'integrazione da config entry."""
    host = entry.data[CONF_HOST]
    session = async_get_clientsession(hass)
    
    coordinator = ThesanDataUpdateCoordinator(hass, session, host)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove l'integrazione."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class ThesanDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordina gli aggiornamenti dei dati dal VMC Thesan."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, host: str):
        """Inizializza il coordinator."""
        self.host = host
        self.session = session
        self.base_url = f"http://{host}"
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        """Recupera i dati dal dispositivo."""
        data = {}
        
        try:
            # Velocità ventola
            async with self.session.get(f"{self.base_url}/speed", timeout=5) as resp:
                if resp.status == 200:
                    speed_text = await resp.text()
                    data["speed"] = int(speed_text.strip())
                    _LOGGER.debug("Velocità letta: %s", data["speed"])
            
            # Modalità - SEMPRE come prima cosa dopo velocità
            try:
                async with self.session.get(f"{self.base_url}/mode", timeout=5) as resp:
                    if resp.status == 200:
                        mode_text = await resp.text()
                        mode_text = mode_text.strip()
                        if mode_text:
                            data["mode"] = int(mode_text)
                            _LOGGER.debug("Modalità letta: %s", data["mode"])
                        else:
                            data["mode"] = 0  # Default a Manuale se vuoto
                            _LOGGER.debug("Modalità vuota, imposto default: 0")
            except (ValueError, aiohttp.ClientError) as err:
                _LOGGER.warning("Errore lettura modalità: %s, imposto default 0", err)
                data["mode"] = 0  # Default a Manuale
            
            # Temperatura interna
            try:
                async with self.session.get(f"{self.base_url}/temp_int", timeout=5) as resp:
                    if resp.status == 200:
                        temp_text = await resp.text()
                        data["temp_int"] = float(temp_text.strip())
            except (ValueError, aiohttp.ClientError):
                pass
            
            # Temperatura esterna
            try:
                async with self.session.get(f"{self.base_url}/temp_ext", timeout=5) as resp:
                    if resp.status == 200:
                        temp_text = await resp.text()
                        data["temp_ext"] = float(temp_text.strip())
            except (ValueError, aiohttp.ClientError):
                pass
            
            # Umidità interna
            try:
                async with self.session.get(f"{self.base_url}/hr_int", timeout=5) as resp:
                    if resp.status == 200:
                        humidity_text = await resp.text()
                        data["humidity"] = float(humidity_text.strip())
            except (ValueError, aiohttp.ClientError):
                pass
            
            # Giorni filtro rimanenti
            try:
                async with self.session.get(f"{self.base_url}/d_filter", timeout=5) as resp:
                    if resp.status == 200:
                        filter_text = await resp.text()
                        data["filter_days"] = int(filter_text.strip())
            except (ValueError, aiohttp.ClientError):
                pass
            
            _LOGGER.debug("Dati completi letti: %s", data)
            return data
            
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Errore comunicazione con Thesan VMC: {err}")

    async def async_set_speed(self, speed: int) -> bool:
        """Imposta la velocità della ventola."""
        try:
            async with self.session.post(
                f"{self.base_url}/speed",
                data=str(speed),
                timeout=5
            ) as resp:
                if resp.status == 200:
                    await self.async_request_refresh()
                    return True
                return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Errore impostazione velocità: %s", err)
            return False

    async def async_set_mode(self, mode: int) -> bool:
        """Imposta la modalità della VMC (0=Manuale, 1=Auto, 2=Bypass)."""
        try:
            async with self.session.post(
                f"{self.base_url}/mode",
                data=str(mode),
                timeout=5
            ) as resp:
                if resp.status == 200:
                    await self.async_request_refresh()
                    return True
                return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Errore impostazione modalità: %s", err)
            return False