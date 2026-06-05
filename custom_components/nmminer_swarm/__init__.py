"""NMMiner Swarm integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NMMinerApiClient
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import NMMinerDataUpdateCoordinator


type NMMinerConfigEntry = ConfigEntry[NMMinerDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NMMinerConfigEntry) -> bool:
    """Set up NMMiner Swarm from a config entry."""
    session = async_get_clientsession(hass)
    client = NMMinerApiClient(session, entry.data[CONF_URL])

    interval_seconds = int(entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    coordinator = NMMinerDataUpdateCoordinator(
        hass,
        client,
        timedelta(seconds=interval_seconds),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NMMinerConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
