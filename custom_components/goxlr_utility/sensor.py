"""Support for GoXLR Utility sensors."""
from __future__ import annotations

from typing import Any, cast

from goxlrutilityapi.const import NAME_MAP
from goxlrutilityapi.helper import get_volume_percentage
from goxlrutilityapi.models.map_item import MapItem

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import GoXLRUtilityDataUpdateCoordinator
from .entity import GoXLRUtilityEntity, GoXLRUtilitySensorEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoXLR Utility sensor based on a config entry."""
    coordinator: GoXLRUtilityDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensor_descrpitions = []
    for key in coordinator.data.levels.volumes.__dict__:
        map_item: MapItem | None = NAME_MAP.get(key)
        sensor_descrpitions.append(
            GoXLRUtilitySensorEntityDescription(
                key=f"volume_{key}",
                name=f"{map_item.name if map_item else key} volume",
                native_unit_of_measurement="%",
                icon=map_item.icon if map_item else "mdi:volume-high",
                value=lambda data, key=key: get_volume_percentage(data, key),
            )
        )

    entities = []
    for description in sensor_descrpitions:
        entities.append(
            GoXLRUtilitySensor(
                coordinator,
                description,
                entry.data.copy(),
            )
        )

    async_add_entities(entities)


class GoXLRUtilitySensor(GoXLRUtilityEntity, SensorEntity):
    """Define a GoXLR Utility sensor."""

    entity_description: GoXLRUtilitySensorEntityDescription

    def __init__(
        self,
        coordinator: GoXLRUtilityDataUpdateCoordinator,
        description: GoXLRUtilitySensorEntityDescription,
        entry_data: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(
            coordinator,
            entry_data,
            description.key,
            description.name,
        )
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        try:
            return cast(StateType, self.entity_description.value(self.coordinator.data))
        except TypeError:
            return None
