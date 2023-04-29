"""Coordinator for GoXLR Utility integration."""
from __future__ import annotations

from asyncio import Task
from datetime import timedelta
import logging
from typing import Any

from goxlrutilityapi.exceptions import (
    ConnectionClosedException,
    ConnectionErrorException,
)
from goxlrutilityapi.helper import get_attribute_names_from_patch, get_mixer_from_status
from goxlrutilityapi.models.patch import Patch
from goxlrutilityapi.models.response import Response
from goxlrutilityapi.models.status import Mixer
from goxlrutilityapi.websocket_client import WebsocketClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .helper import setup_connection


class GoXLRUtilityDataUpdateCoordinator(DataUpdateCoordinator[Mixer]):
    """Class to manage fetching GoXLR Utility data from single endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        LOGGER: logging.Logger,
        *,
        entry: ConfigEntry,
    ) -> None:
        """Initialize global GoXLR Utility data updater."""
        self.title = entry.title
        self.unsub: CALLBACK_TYPE | None = None

        self._entry_data: dict[str, Any] = entry.data.copy()
        self._listener_task: Task | None = None
        self._websocket_client: WebsocketClient | None = None

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    @property
    def is_ready(self) -> bool:
        """Return if the data is ready."""
        return self.data is not None

    async def setup(self) -> None:
        """Set up connection to Websocket."""

        self._websocket_client = await setup_connection(
            self.hass,
            self._entry_data.copy(),
        )

        async def listen_for_patches() -> None:
            """Listen for patches from GoXLR Utility."""
            if self._websocket_client is None:
                raise ConfigEntryNotReady("Websocket not connected")

            try:
                await self._websocket_client.listen(self.patch_callback)
            except (ConnectionClosedException, ConnectionResetError) as exception:
                self.logger.debug(
                    "Websocket connection closed for %s. Will retry: %s",
                    self.title,
                    exception,
                )
                if self.unsub:
                    self.unsub()
                    self.unsub = None
                self.last_update_success = False
                self.async_update_listeners()
            except ConnectionErrorException as exception:
                self.logger.debug(
                    "Connection error occurred for %s. Will retry: %s",
                    self.title,
                    exception,
                )
                if self.unsub:
                    self.unsub()
                    self.unsub = None
                self.last_update_success = False
                self.async_update_listeners()

        self._listener_task = self.hass.async_create_background_task(
            listen_for_patches(),
            name="GoXLR Utility Patch Listener",
        )

        async def cleanup(_: Event) -> None:
            """Disconnect and cleanup items."""
            await self.cleanup()

        # Cleanup on Home Assistant shutdown
        self.unsub = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP,
            cleanup,
        )

    async def cleanup(self) -> None:
        """Disconnect and cleanup items."""
        if self._websocket_client is not None:
            await self._websocket_client.disconnect()

    async def _get_mixer(self) -> Mixer:
        """Get mixer from GoXLR Utility."""
        if self._websocket_client is None or not self._websocket_client.connected:
            raise ConfigEntryNotReady("Websocket not connected")

        # Get status and mixer
        status = await self._websocket_client.get_status()
        mixer = get_mixer_from_status(status)
        if mixer is None:
            raise ConfigEntryNotReady("No mixer found")
        return mixer

    async def _patch_callback_task(
        self,
        patch: Patch,
    ) -> None:
        """Patch response callback task."""
        # Get new data
        new_data = self.data
        if new_data is None:
            self.logger.debug("No data available")
            return

        # Get attribute names from patch path
        attribute_names = get_attribute_names_from_patch(new_data, patch)
        self.logger.info("Update '%s': %s", attribute_names, patch.value)

        # Update data
        current_attribute = new_data
        for attribute_name in attribute_names[:-1]:
            current_attribute = getattr(current_attribute, attribute_name)
        setattr(current_attribute, attribute_names[-1], patch.value)
        self.logger.debug("Updated data: %s", new_data)
        self.async_set_updated_data(new_data)

        # Update listeners
        self.last_update_success = True
        self.async_update_listeners()

    async def patch_callback(
        self,
        response: Response[Patch],
    ) -> None:
        """Patch response callback function."""
        self.hass.async_create_background_task(
            self._patch_callback_task(response.data),
            name="Patch Callback Task",
        )

    async def _async_update_data(self) -> Mixer:
        """Update GoXLR Utility data from WebSocket."""
        if (
            self._websocket_client is None
            or not self._websocket_client.connected
            or self._listener_task is None
        ):
            await self.setup()

        if self.data is None:
            mixer: Mixer = await self._get_mixer()
            self.async_set_updated_data(mixer)
            self.logger.debug("Data updated: %s", mixer)

        if self.data is None:
            raise ConfigEntryNotReady("No data found")

        return self.data
