"""Support for GoXLR Utility binary sensors."""
from __future__ import annotations

from typing import Any

from goxlrutilityapi.const import MUTED_STATE, NAME_MAP
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

    fader_status = coordinator.data.fader_status

    fader_a: MapItem | None = NAME_MAP.get(fader_status.a.channel)
    fader_b: MapItem | None = NAME_MAP.get(fader_status.b.channel)
    fader_c: MapItem | None = NAME_MAP.get(fader_status.c.channel)
    fader_d: MapItem | None = NAME_MAP.get(fader_status.d.channel)

    binary_sensor_descrpitions = [
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.a.channel.lower()}",
            name=f"{fader_a.name if fader_a else fader_status.a.channel} muted",
            icon=fader_a.icon if fader_a else "mdi:volume-off",
            value=lambda data: data.fader_status.a.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.b.channel.lower()}",
            name=f"{fader_b.name if fader_b else fader_status.b.channel} muted",
            icon=fader_b.icon if fader_b else "mdi:volume-off",
            value=lambda data: data.fader_status.b.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.c.channel.lower()}",
            name=f"{fader_c.name if fader_c else fader_status.c.channel} muted",
            icon=fader_c.icon if fader_c else "mdi:volume-off",
            value=lambda data: data.fader_status.c.mute_state == MUTED_STATE,
        ),
        GoXLRUtilityBinarySensorEntityDescription(
            key=f"muted_{fader_status.d.channel.lower()}",
            name=f"{fader_d.name if fader_d else fader_status.d.channel} muted",
            icon=fader_d.icon if fader_d else "mdi:volume-off",
            value=lambda data: data.fader_status.d.mute_state == MUTED_STATE,
        ),
    ]

    for key in coordinator.data.button_down.__dict__:
        map_item: MapItem | None = NAME_MAP.get(key)
        binary_sensor_descrpitions.append(
            GoXLRUtilityBinarySensorEntityDescription(
                key=f"button_{key}",
                name=f"{map_item.name if map_item else key} pressed",
                icon=map_item.icon if map_item else "mdi:button-pointer",
                entity_category=EntityCategory.DIAGNOSTIC,
                entity_registry_visible_default=False,
                value=lambda data, item_key=key: data.button_down.__dict__.get(
                    item_key, None
                ),
            )
        )

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
