"""Select-Plattform – Wunschwasserhärte als Dropdown."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, WATER_HARDNESS_OPTIONS
from .coordinator import JudoCoordinator
from .entity import JudoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WaterHardnessSelect(coordinator)])


class WaterHardnessSelect(JudoEntity, SelectEntity):
    """Wunschwasserhärte 1–30 °dH (Dropdown, mit Read-Back)."""

    _attr_translation_key = "set_water_hardness"
    _attr_icon = "mdi:water-opacity"
    _attr_options = WATER_HARDNESS_OPTIONS

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator, "set_water_hardness")

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get("water_hardness")
        if value is None or not 1 <= value <= 30:
            return None
        return str(value)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.set_water_hardness(int(option))
        await self.coordinator.async_request_refresh()
