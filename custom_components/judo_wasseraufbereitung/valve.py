"""Valve-Plattform – Leckageschutz öffnen/schließen."""

from __future__ import annotations

from typing import Any

from homeassistant.components.valve import (
    ValveDeviceClass,
    ValveEntity,
    ValveEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoCoordinator
from .entity import JudoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LeakProtectionValve(coordinator)])


class LeakProtectionValve(JudoEntity, ValveEntity):
    """Leckageschutz – offen = Wasser fließt, geschlossen = abgesperrt."""

    _attr_translation_key = "leak_protection"
    _attr_device_class = ValveDeviceClass.WATER
    _attr_supported_features = (
        ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
    )
    _attr_reports_position = False

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator, "leak_protection")
        # Annahme: Bei Start ist das Ventil offen (Wasser fließt). Wird per
        # Action explizit geschlossen, wechselt der Zustand. Es gibt keinen
        # API-Lesebefehl für den Ventilzustand bei i-soft K SAFE+.
        self._attr_is_closed = False

    async def async_open_valve(self, **kwargs: Any) -> None:
        await self.coordinator.client.open_leak_protection()
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_valve(self, **kwargs: Any) -> None:
        await self.coordinator.client.close_leak_protection()
        self._attr_is_closed = True
        self.async_write_ha_state()
