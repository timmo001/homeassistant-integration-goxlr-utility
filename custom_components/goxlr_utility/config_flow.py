"""Config flow for GoXLR Utility integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from goxlrutilityapi.const import DEFAULT_PORT
from goxlrutilityapi.helper import get_mixer_from_status
from goxlrutilityapi.websocket_client import WebsocketClient
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONNECTION_ERRORS, DOMAIN
from .helper import CannotConnect, setup_connection

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(
            CONF_PORT,
            default=DEFAULT_PORT,
        ): int,
    }
)


async def listen_for_patches(
    websocket_client: WebsocketClient,
) -> None:
    """Listen for patches from GoXLR Utility."""
    try:
        await websocket_client.listen()
    except CONNECTION_ERRORS as exception:
        _LOGGER.warning("Connection error: %s", exception)
        raise CannotConnect from exception


async def validate_input(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    websocket_client = await setup_connection(hass, data)

    listener_task = hass.async_create_background_task(
        listen_for_patches(websocket_client),
        name="GoXLR Utility Patch Listener",
    )

    status = await websocket_client.get_status()
    mixer = get_mixer_from_status(status)
    if mixer is None:
        raise CannotConnect("No mixer found")

    listener_task.cancel()
    await websocket_client.disconnect()

    return {
        "title": f"{mixer.hardware.usb_device.manufacturer_name} - {mixer.hardware.usb_device.product_name}",
        "identifier": mixer.hardware.serial_number,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoXLR Utility."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except (asyncio.TimeoutError, CannotConnect):
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["identifier"])
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
