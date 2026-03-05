"""
FILE: custom_components/thesan_vmc/config_flow.py

Config flow per Thesan VMC.
"""
import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "thesan_vmc"


class ThesanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il config flow per Thesan VMC."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gestisce lo step iniziale configurato dall'utente."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            
            # Verifica connessione
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(f"http://{host}/device", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "res" in data and "Thesan" in data["res"]:
                            # Connessione riuscita
                            await self.async_set_unique_id(host)
                            self._abort_if_unique_id_configured()
                            
                            return self.async_create_entry(
                                title=user_input.get(CONF_NAME, "Thesan VMC"),
                                data=user_input,
                            )
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Errore inaspettato: %s", err)
                errors["base"] = "unknown"

        # Mostra il form
        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="192.168.1.100"): str,
            vol.Optional(CONF_NAME, default="Thesan VMC"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )