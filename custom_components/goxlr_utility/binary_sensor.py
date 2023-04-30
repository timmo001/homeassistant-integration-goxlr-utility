"""Support for GoXLR Utility binary sensors."""
from __future__ import annotations

from typing import Any

from goxlrutilityapi.const import MUTED_STATE

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import GoXLRUtilityDataUpdateCoordinator
from .entity import GoXLRUtilityBinarySensorEntityDescription, GoXLRUtilityEntity

NAME_MAP = {
    "Mic": "Microphone",
    "LineIn": "Line In",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoXLR Utility sensor based on a config entry."""
    coordinator: GoXLRUtilityDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    fader_status = coordinator.data.fader_status

    binary_sensor_descrpitions = [
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.a.channel.lower()}",
            name=f"{NAME_MAP.get(fader_status.a.channel, fader_status.a.channel)} muted",
            icon="mdi:volume-off",
            value=lambda data: data.fader_status.a.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.b.channel.lower()}",
            name=f"{NAME_MAP.get(fader_status.b.channel, fader_status.b.channel)} muted",
            icon="mdi:volume-off",
            value=lambda data: data.fader_status.b.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.c.channel.lower()}",
            name=f"{NAME_MAP.get(fader_status.c.channel, fader_status.c.channel)} muted",
            icon="mdi:volume-off",
            value=lambda data: data.fader_status.c.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.d.channel.lower()}",
            name=f"{NAME_MAP.get(fader_status.d.channel, fader_status.d.channel)} muted",
            icon="mdi:volume-off",
            value=lambda data: data.fader_status.d.mute_state == MUTED_STATE,
        ),
    ]

    # for key, field in coordinator.data.button_down.__fields__.items():
    #     binary_sensor_descrpitions.append(
    #         GoXLRUtilityBinarySensorEntityDescription(
    #             key=f"button_{key}",
    #             name=f"Button {field.} pressed",
    #             icon="mdi:gesture-tap-button",
    #             # value=lambda data: data.button_down[key],
    #         )
    #     )

    entities = []
    for description in binary_sensor_descrpitions:
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
