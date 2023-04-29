"""Helper for GoXLR Utility integration."""
from __future__ import annotations

import logging
from typing import Any

import async_timeout
from goxlrutilityapi.websocket_client import WebsocketClient

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONNECTION_ERRORS

_LOGGER = logging.getLogger(__name__)


async def setup_connection(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> WebsocketClient:
    """Set up connection to GoXLR Utility."""
    async with async_timeout.timeout(10):
        websocket_client = WebsocketClient()
        try:
            await websocket_client.connect(
                data["host"],
                data["port"],
                async_get_clientsession(hass),
            )
        except CONNECTION_ERRORS as exception:
            _LOGGER.warning("Connection error: %s", exception)
            raise CannotConnect from exception

        return websocket_client


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
