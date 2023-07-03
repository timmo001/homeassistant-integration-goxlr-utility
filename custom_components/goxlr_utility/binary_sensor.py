"""Support for GoXLR Utility binary sensors."""
from __future__ import annotations

from typing import Any

from goxlrutilityapi.const import NAME_MAP
from goxlrutilityapi.models.map_item import MapItem

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import GoXLRUtilityDataUpdateCoordinator
from .entity import GoXLRUtilityBinarySensorEntityDescription, GoXLRUtilityEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoXLR Utility sensor based on a config entry."""
    coordinator: GoXLRUtilityDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensor_descriptions = []
    for key in vars(coordinator.data.button_down):
        map_item: MapItem | None = NAME_MAP.get(key)
        binary_sensor_descriptions.append(
            GoXLRUtilityBinarySensorEntityDescription(
                key=f"button_{key}",
                name=f"{map_item.name if map_item else key} pressed",
                icon=map_item.icon if map_item else "mdi:button-pointer",
                entity_category=EntityCategory.DIAGNOSTIC,
                value=lambda data, item_key=key: data.button_down.__dict__.get(
                    item_key, None
                ),
            )
        )

    entities = []
    for description in binary_sensor_descriptions:
        entities.append(
            GoXLRUtilitySensor(
                coordinator,
                description,
                entry.data.copy(),
            )
        )

    async_add_entities(entities)


class GoXLRUtilitySensor(GoXLRUtilityEntity, BinarySensorEntity):
    """Define a GoXLR Utility sensor."""

    entity_description: GoXLRUtilityBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: GoXLRUtilityDataUpdateCoordinator,
        description: GoXLRUtilityBinarySensorEntityDescription,
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value(self.coordinator.data)
