"""Test the GoXLR Utility config flow."""
from unittest.mock import AsyncMock, patch

from goxlrutilityapi.const import DEFAULT_HOST, DEFAULT_PORT
from goxlrutilityapi.exceptions import ConnectionErrorException
from goxlrutilityapi.helpers.tests.models.status import StatusFactory
from goxlrutilityapi.models.status import Status
from polyfactory.pytest_plugin import register_fixture
import pytest

from homeassistant import config_entries
from homeassistant.components.goxlr_utility.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

pytestmark = pytest.mark.usefixtures("mock_setup_entry")
status_factory_fixture = register_fixture(StatusFactory, name="fixture_status")


async def test_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fixture_status: Status,
) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_USER,
        },
    )
    assert "type" in result and result["type"] == FlowResultType.FORM
    assert "errors" in result and result["errors"] == {}

    with patch("goxlrutilityapi.websocket_client.WebsocketClient.connect"), patch(
        "goxlrutilityapi.websocket_client.WebsocketClient.listen"
    ), patch(
        "goxlrutilityapi.websocket_client.WebsocketClient.get_status",
        return_value=fixture_status,
    ), patch(
        "goxlrutilityapi.websocket_client.WebsocketClient.disconnect"
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: DEFAULT_HOST,
                CONF_PORT: DEFAULT_PORT,
            },
        )
        await hass.async_block_till_done()

    assert "type" in result2 and result2["type"] == FlowResultType.CREATE_ENTRY
    # assert "title" in result2 and result2["title"] == FIXTURE_NAME
    assert "data" in result2 and result2["data"] == {
        CONF_HOST: DEFAULT_HOST,
        CONF_PORT: DEFAULT_PORT,
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_USER,
        },
    )

    with patch(
        "goxlrutilityapi.websocket_client.WebsocketClient.connect",
        side_effect=ConnectionErrorException,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: DEFAULT_HOST,
                CONF_PORT: DEFAULT_PORT,
            },
        )

    assert "type" in result2 and result2["type"] == FlowResultType.FORM
    assert "errors" in result2 and result2["errors"] == {"base": "cannot_connect"}
