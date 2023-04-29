"""Support for GoXLR Utility sensors."""
from __future__ import annotations

from typing import Any, cast

from goxlrutilityapi.helper import get_volume_percentage

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import GoXLRUtilityDataUpdateCoordinator
from .entity import GoXLRUtilityEntity, GoXLRUtilitySensorEntityDescription

SENSOR_TYPES: tuple[GoXLRUtilitySensorEntityDescription, ...] = (
    GoXLRUtilitySensorEntityDescription(
        key="volume_chat",
        name="Chat Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "chat"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_console",
        name="Console Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "console"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_headphones",
        name="Headphones Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "headphones"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_line_in",
        name="Line In Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "line_in"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_line_out",
        name="Line Out Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "line_out"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_mic_monitor",
        name="Microphone Monitor Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "mic_monitor"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_microphone",
        name="Microphone Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "mic"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_music",
        name="Music Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "music"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_sample",
        name="Sample Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "sample"),
    ),
    GoXLRUtilitySensorEntityDescription(
        key="volume_system",
        name="System Volume",
        native_unit_of_measurement="%",
        icon="mdi:volume-medium",
        value=lambda data: get_volume_percentage(data, "system"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoXLR Utility sensor based on a config entry."""
    coordinator: GoXLRUtilityDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SENSOR_TYPES:
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
