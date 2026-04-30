"""Config Flow für JUDO Wasseraufbereitung."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import (
    JudoApiClient,
    JudoAuthError,
    JudoConnectionError,
)
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    SCAN_INTERVAL_OPTIONS,
    SUPPORTED_DEVICE_TYPES,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.In(
            SCAN_INTERVAL_OPTIONS
        ),
    }
)


class JudoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config Flow – prüft Verbindung und Gerätetyp."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            session = async_get_clientsession(self.hass)
            client = JudoApiClient(
                host,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                session,
            )
            try:
                device_type = await client.get_device_type()
                serial = await client.get_serial_number()
            except JudoAuthError:
                errors["base"] = "invalid_auth"
            except JudoConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unerwarteter Fehler im Config Flow")
                errors["base"] = "unknown"
            else:
                if device_type not in SUPPORTED_DEVICE_TYPES:
                    errors["base"] = "unsupported_device"
                else:
                    await self.async_set_unique_id(f"judo_{serial}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="JUDO i-soft K SAFE+",
                        data={
                            CONF_HOST: host,
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                            "device_type": device_type,
                            "serial_number": serial,
                        },
                    )

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> JudoOptionsFlow:
        return JudoOptionsFlow(config_entry)


class JudoOptionsFlow(OptionsFlow):
    """Optionen für die Integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options.get(
            CONF_SCAN_INTERVAL
        ) or self._config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current
                    ): vol.In(SCAN_INTERVAL_OPTIONS),
                }
            ),
        )
