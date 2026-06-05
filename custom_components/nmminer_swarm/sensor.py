"""Sensors for NMMiner Swarm."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfInformation, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import (
    parse_difficulty,
    parse_difficulty_session,
    parse_float,
    parse_hashrate,
    parse_int,
    parse_string,
    parse_uptime_session,
    parse_uptime_total,
)
from .const import DOMAIN
from .coordinator import NMMinerDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class NMMinerSummarySensorDescription(SensorEntityDescription):
    """Summary sensor description."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass(frozen=True, kw_only=True)
class NMMinerDeviceSensorDescription(SensorEntityDescription):
    """Device sensor description."""

    value_fn: Callable[[dict[str, Any]], Any]


SUMMARY_SENSORS: tuple[NMMinerSummarySensorDescription, ...] = (
    NMMinerSummarySensorDescription(
        key="total_workers",
        translation_key="total_workers",
        native_unit_of_measurement="workers",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_int(data.get("totalWorkers")),
    ),
    NMMinerSummarySensorDescription(
        key="total_hash_rate",
        translation_key="total_hash_rate",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_hashrate(data.get("totalHashRate")),
    ),
    NMMinerSummarySensorDescription(
        key="best_diff",
        translation_key="best_diff",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty(data.get("bestDiff")),
    ),
)

DEVICE_SENSORS: tuple[NMMinerDeviceSensorDescription, ...] = (
    NMMinerDeviceSensorDescription(
        key="hash_rate",
        translation_key="hash_rate",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_hashrate(data.get("hashRate")),
    ),
    NMMinerDeviceSensorDescription(
        key="rssi",
        translation_key="rssi",
        native_unit_of_measurement="dBm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_int(data.get("rssi")),
    ),
    NMMinerDeviceSensorDescription(
        key="free_heap",
        translation_key="free_heap",
        native_unit_of_measurement=UnitOfInformation.KIBIBYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_float(data.get("freeHeap")),
    ),
    NMMinerDeviceSensorDescription(
        key="valid",
        translation_key="valid",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: parse_int(data.get("valid")),
    ),
    NMMinerDeviceSensorDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_float(data.get("temp")),
    ),
    NMMinerDeviceSensorDescription(
        key="best_diff",
        translation_key="best_diff",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty(data.get("bestDiff")),
    ),
    NMMinerDeviceSensorDescription(
        key="pool_diff",
        translation_key="pool_diff",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty(data.get("poolDiff")),
    ),
    NMMinerDeviceSensorDescription(
        key="last_diff",
        translation_key="last_diff",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty(data.get("lastDiff")),
    ),
    NMMinerDeviceSensorDescription(
        key="net_diff",
        translation_key="net_diff",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty(data.get("netDiff")),
    ),
    NMMinerDeviceSensorDescription(
        key="best_diff_session",
        translation_key="best_diff_session",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_difficulty_session(data.get("bestDiff")),
    ),
    NMMinerDeviceSensorDescription(
        key="pool",
        translation_key="pool",
        value_fn=lambda data: parse_string(data.get("pool")),
    ),
    NMMinerDeviceSensorDescription(
        key="uptime_session",
        translation_key="uptime_session",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: parse_uptime_session(data.get("uptime")),
    ),
    NMMinerDeviceSensorDescription(
        key="uptime_total",
        translation_key="uptime_total",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: parse_uptime_total(data.get("uptime")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NMMiner sensors."""
    coordinator: NMMinerDataUpdateCoordinator = entry.runtime_data
    integration_name = entry.data.get(CONF_NAME, "NMMiner Swarm")

    added_device_ips: set[str] = set()

    entities: list[SensorEntity] = [
        NMMinerSummarySensor(coordinator, entry.entry_id, integration_name, description)
        for description in SUMMARY_SENSORS
    ]

    def make_device_entities() -> list[SensorEntity]:
        new_entities: list[SensorEntity] = []
        if coordinator.data is None:
            return new_entities

        for ip in coordinator.data.devices:
            if ip in added_device_ips:
                continue
            added_device_ips.add(ip)
            for description in DEVICE_SENSORS:
                new_entities.append(
                    NMMinerDeviceSensor(
                        coordinator,
                        entry.entry_id,
                        integration_name,
                        ip,
                        description,
                    )
                )
        return new_entities

    entities.extend(make_device_entities())
    async_add_entities(entities)

    @callback
    def _async_add_new_devices() -> None:
        new_entities = make_device_entities()
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))


class NMMinerSummarySensor(CoordinatorEntity[NMMinerDataUpdateCoordinator], SensorEntity):
    """A summary sensor for the NMMiner swarm."""

    entity_description: NMMinerSummarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NMMinerDataUpdateCoordinator,
        entry_id: str,
        integration_name: str,
        description: NMMinerSummarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_summary_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": integration_name,
            "manufacturer": "NMMiner",
        }

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data.summary)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        return dict(self.coordinator.data.summary)


class NMMinerDeviceSensor(CoordinatorEntity[NMMinerDataUpdateCoordinator], SensorEntity):
    """A per-device sensor for the NMMiner swarm."""

    entity_description: NMMinerDeviceSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NMMinerDataUpdateCoordinator,
        entry_id: str,
        integration_name: str,
        ip: str,
        description: NMMinerDeviceSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._ip = ip
        self._entry_id = entry_id
        self._integration_name = integration_name
        safe_ip = ip.replace(".", "_").replace(":", "_")
        self._attr_unique_id = f"{entry_id}_{safe_ip}_{description.key}"

    @property
    def device_info(self) -> dict:
        device = self.coordinator.data.devices.get(self._ip) if self.coordinator.data else None
        info: dict = {
            "identifiers": {(DOMAIN, f"{self._entry_id}_{self._ip}")},
            "name": f"{self._integration_name} {self._ip}",
            "manufacturer": "NMMiner",
            "configuration_url": f"http://{self._ip}",
            "via_device": (DOMAIN, self._entry_id),
        }
        if device:
            board_type = device.raw.get("boardType")
            if board_type:
                info["model"] = board_type
            version = device.raw.get("version")
            if version:
                info["sw_version"] = version
        return info

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None

        device = self.coordinator.data.devices.get(self._ip)
        if device is None:
            return None

        return self.entity_description.value_fn(device.raw)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}

        device = self.coordinator.data.devices.get(self._ip)
        if device is None:
            return {"ip": self._ip, "lastseen": "missing from latest swarm response"}

        raw = device.raw
        return {
            "ip": self._ip,
            "board_type": raw.get("boardType"),
            "pool": raw.get("pool"),
            "share": raw.get("share"),
            "version": raw.get("version"),
            "uptime": raw.get("uptime"),
            "lastseen": raw.get("lastseen"),
            "raw_hash_rate": raw.get("hashRate"),
            "raw_best_diff": raw.get("bestDiff"),
            "raw_net_diff": raw.get("netDiff"),
            "raw_pool_diff": raw.get("poolDiff"),
            "raw_last_diff": raw.get("lastDiff"),
        }
