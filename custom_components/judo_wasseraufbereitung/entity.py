"""Basis-Entity für die JUDO Wasseraufbereitung Integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import JudoCoordinator


class JudoEntity(CoordinatorEntity[JudoCoordinator]):
    """Gemeinsame Basis aller JUDO-Entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator, entity_key: str) -> None:
        super().__init__(coordinator)
        serial = coordinator.serial_number
        self._attr_unique_id = f"judo_{serial}_{entity_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            name=f"JUDO {MODEL}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=coordinator.sw_version,
            serial_number=str(serial),
        )
