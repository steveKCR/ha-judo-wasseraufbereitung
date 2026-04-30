"""Diagnostics für die JUDO Wasseraufbereitung Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import JudoCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]

    redacted = dict(entry.data)
    for key in (CONF_HOST, CONF_USERNAME, CONF_PASSWORD):
        if key in redacted:
            redacted[key] = "**REDACTED**"

    return {
        "config": redacted,
        "device": {
            "serial_number": coordinator.serial_number,
            "sw_version": coordinator.sw_version,
        },
        "data": coordinator.data,
    }
