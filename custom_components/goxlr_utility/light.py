"""Support for GoXLR Utility lights."""
from __future__ import annotations

import logging
from typing import Any, cast

from goxlrutilityapi.const import KEY_MAP, NAME_MAP
from goxlrutilityapi.models.map_item import MapItem

from homeassistant.components.light import ATTR_RGB_COLOR, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.color as color_util

from .const import DOMAIN
from .coordinator import GoXLRUtilityDataUpdateCoordinator
from .entity import GoXLRUtilityEntity, GoXLRUtilityLightEntityDescription, ItemType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoXLR Utility light based on a config entry."""
    coordinator: GoXLRUtilityDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    light_descrpitions = [
        GoXLRUtilityLightEntityDescription(
            key="light_accent",
            name="Accent",
            icon="mdi:television-ambient-light",
            item_type=ItemType.ACCENT,
            hex=lambda data, _: data.lighting.simple.accent.colour_one,
        ),
    ]

    for key in coordinator.data.lighting.buttons.__dict__:
        button_map_item: MapItem | None = NAME_MAP.get(key)
        light_descrpitions.extend(
            [
                GoXLRUtilityLightEntityDescription(
                    key=f"light_button_{key}_active",
                    name=f"{button_map_item.name if button_map_item else key} active",
                    icon=button_map_item.icon if button_map_item else None,
                    item_type=ItemType.BUTTON_ACTIVE,
                    item_key=key,
                    hex=lambda data, item_key: getattr(
                        data.lighting.buttons, item_key
                    ).colours.colour_one,
                ),
                GoXLRUtilityLightEntityDescription(
                    key=f"light_button_{key}_inactive",
                    name=f"{button_map_item.name if button_map_item else key} inactive",
                    icon=button_map_item.icon if button_map_item else None,
                    item_type=ItemType.BUTTON_INACTIVE,
                    item_key=key,
                    hex=lambda data, item_key: getattr(
                        data.lighting.buttons, item_key
                    ).colours.colour_two,
                ),
            ]
        )

    for key in coordinator.data.lighting.faders.__dict__:
        fader_map_item: MapItem | None = NAME_MAP.get(key)
        light_descrpitions.extend(
            [
                GoXLRUtilityLightEntityDescription(
                    key=f"light_fader_{key}_top",
                    name=f"{fader_map_item.name if fader_map_item else key} top",
                    icon=fader_map_item.icon if fader_map_item else None,
                    item_type=ItemType.FADER_TOP,
                    item_key=key,
                    hex=lambda data, item_key: getattr(
                        data.lighting.faders, item_key
                    ).colours.colour_one,
                ),
                GoXLRUtilityLightEntityDescription(
                    key=f"light_fader_{key}_bottom",
                    name=f"{fader_map_item.name if fader_map_item else key} bottom",
                    icon=fader_map_item.icon if fader_map_item else None,
                    item_type=ItemType.FADER_BOTTOM,
                    item_key=key,
                    hex=lambda data, item_key: getattr(
                        data.lighting.faders, item_key
                    ).colours.colour_two,
                ),
            ]
        )

    entities = []
    for description in light_descrpitions:
        entities.append(
            GoXLRUtilityLight(
                coordinator,
                description,
                entry.data.copy(),
            )
        )

    async_add_entities(entities)


class GoXLRUtilityLight(GoXLRUtilityEntity, LightEntity):
    """Define a GoXLR Utility light."""

    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    entity_description: GoXLRUtilityLightEntityDescription

    def __init__(
        self,
        coordinator: GoXLRUtilityDataUpdateCoordinator,
        description: GoXLRUtilityLightEntityDescription,
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
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.rgb_color != (0, 0, 0)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        hex_value = self.entity_description.hex(
            self.coordinator.data,
            self.entity_description.item_key,
        )
        return (
            cast(tuple[int, int, int], tuple(color_util.rgb_hex_to_rgb_list(hex_value)))
            if hex_value
            else None
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if self.coordinator.client is None:
            return

        hex_value = color_util.color_rgb_to_hex(
            *kwargs.get(ATTR_RGB_COLOR, (255, 255, 255))
        )

        if self.entity_description.item_type == ItemType.ACCENT:
            await self.coordinator.client.set_accent_color(hex_value)
            return

        item_key = self.entity_description.item_key
        if (key := KEY_MAP.get(item_key)) is None:
            return

        if self.entity_description.item_type == ItemType.BUTTON_ACTIVE:
            await self.coordinator.client.set_button_color(
                key,
                hex_value,
                getattr(
                    self.coordinator.data.lighting.buttons, item_key
                ).colours.colour_two,
            )
        elif self.entity_description.item_type == ItemType.BUTTON_INACTIVE:
            await self.coordinator.client.set_button_color(
                key,
                getattr(
                    self.coordinator.data.lighting.buttons, item_key
                ).colours.colour_one,
                hex_value,
            )
        elif self.entity_description.item_type == ItemType.FADER_TOP:
            await self.coordinator.client.set_fader_color(
                key,
                hex_value,
                getattr(
                    self.coordinator.data.lighting.faders, item_key
                ).colours.colour_two,
            )
        elif self.entity_description.item_type == ItemType.FADER_BOTTOM:
            await self.coordinator.client.set_fader_color(
                key,
                getattr(
                    self.coordinator.data.lighting.faders, item_key
                ).colours.colour_one,
                hex_value,
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        if self.coordinator.client is None:
            return

        if self.entity_description.item_type == ItemType.ACCENT:
            await self.coordinator.client.set_accent_color("000000")
            return

        item_key = self.entity_description.item_key
        if (key := KEY_MAP.get(item_key)) is None:
            return

        if self.entity_description.item_type == ItemType.BUTTON_ACTIVE:
            await self.coordinator.client.set_button_color(
                key,
                "000000",
                getattr(
                    self.coordinator.data.lighting.buttons, item_key
                ).colours.colour_two,
            )
        elif self.entity_description.item_type == ItemType.BUTTON_INACTIVE:
            await self.coordinator.client.set_button_color(
                key,
                getattr(
                    self.coordinator.data.lighting.buttons, item_key
                ).colours.colour_one,
                "000000",
            )
        elif self.entity_description.item_type == ItemType.FADER_TOP:
            await self.coordinator.client.set_fader_color(
                key,
                "000000",
                getattr(
                    self.coordinator.data.lighting.faders, item_key
                ).colours.colour_two,
            )
        elif self.entity_description.item_type == ItemType.FADER_BOTTOM:
            await self.coordinator.client.set_fader_color(
                key,
                getattr(
                    self.coordinator.data.lighting.faders, item_key
                ).colours.colour_one,
                "000000",
            )
