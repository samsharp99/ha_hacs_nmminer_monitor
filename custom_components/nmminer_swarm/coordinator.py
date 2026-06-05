"""Data coordinator for NMMiner Swarm."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NMMinerApiClient, NMMinerApiError, NMMinerSwarmData

_LOGGER = logging.getLogger(__name__)


class NMMinerDataUpdateCoordinator(DataUpdateCoordinator[NMMinerSwarmData]):
    """Coordinates one swarm poll for all sensors."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NMMinerApiClient,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NMMiner Swarm",
            update_interval=update_interval,
            always_update=False,
        )
        self.client = client

    async def _async_update_data(self) -> NMMinerSwarmData:
        try:
            return await self.client.async_get_swarm()
        except NMMinerApiError as err:
            raise UpdateFailed(str(err)) from err
