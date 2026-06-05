"""Config flow for NMMiner Swarm."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NMMinerApiClient, NMMinerApiError, normalize_url
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class NMMinerSwarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NMMiner Swarm."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = normalize_url(user_input[CONF_URL])
            scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            await self.async_set_unique_id(url)
            self._abort_if_unique_id_configured()

            client = NMMinerApiClient(async_get_clientsession(self.hass), url)

            try:
                await client.async_get_swarm()
            except NMMinerApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_URL: url,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_URL): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=5, max=3600),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
