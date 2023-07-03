"""Support for GoXLR Utility sensors."""
from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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

    sensor_descriptions: list[GoXLRUtilitySensorEntityDescription] = [
        GoXLRUtilitySensorEntityDescription(
            key="profile_name",
            name="Profile name",
            icon="mdi:headphones-settings",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_visible_default=False,
            value=lambda data: data.profile_name,
        ),
        GoXLRUtilitySensorEntityDescription(
            key="microphone_profile_name",
            name="Microphone profile name",
            icon="mdi:microphone-settings",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_visible_default=False,
            value=lambda data: data.mic_profile_name,
        ),
    ]

    entities = [
        GoXLRUtilitySensor(
            coordinator,
            description,
            entry.data.copy(),
        )
        for description in sensor_descriptions
    ]
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
