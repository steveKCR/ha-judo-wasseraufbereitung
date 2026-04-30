"""Sensor-Plattform – 8 fokussierte Sensoren für i-soft K SAFE+."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoCoordinator
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[JudoSensorEntityDescription, ...] = (
    JudoSensorEntityDescription(
        key="current_flow_rate",
        translation_key="current_flow_rate",
        icon="mdi:water-pump",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement="L/h",
        suggested_display_precision=1,
        value_fn=lambda d: d.get("current_flow_lph"),
    ),
    JudoSensorEntityDescription(
        key="total_water_m3",
        translation_key="total_water_m3",
        icon="mdi:water",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        value_fn=lambda d: round(d.get("total_water_l", 0) / 1000, 3),
    ),
    JudoSensorEntityDescription(
        key="total_water_liters",
        translation_key="total_water_liters",
        icon="mdi:water",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=0,
        value_fn=lambda d: d.get("total_water_l", 0),
    ),
    JudoSensorEntityDescription(
        key="soft_water_m3",
        translation_key="soft_water_m3",
        icon="mdi:water-check",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        value_fn=lambda d: round(d.get("soft_water_l", 0) / 1000, 3),
    ),
    JudoSensorEntityDescription(
        key="soft_water_liters",
        translation_key="soft_water_liters",
        icon="mdi:water-check",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        suggested_display_precision=0,
        value_fn=lambda d: d.get("soft_water_l", 0),
    ),
    JudoSensorEntityDescription(
        key="salt_range_days",
        translation_key="salt_range_days",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.DAYS,
        value_fn=lambda d: d.get("salt_range_days"),
    ),
    JudoSensorEntityDescription(
        key="salt_weight_kg",
        translation_key="salt_weight_kg",
        icon="mdi:shaker-outline",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        suggested_display_precision=2,
        value_fn=lambda d: round(d.get("salt_weight_g", 0) / 1000, 2),
    ),
    JudoSensorEntityDescription(
        key="water_hardness",
        translation_key="water_hardness",
        icon="mdi:water-opacity",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="°dH",
        value_fn=lambda d: d.get("water_hardness"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        JudoSensor(coordinator, desc) for desc in SENSORS
    )


class JudoSensor(JudoEntity, SensorEntity):
    """Standard-Sensor."""

    entity_description: JudoSensorEntityDescription

    def __init__(
        self,
        coordinator: JudoCoordinator,
        description: JudoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
