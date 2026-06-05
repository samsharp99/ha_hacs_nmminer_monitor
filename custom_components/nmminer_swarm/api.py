"""API client and parsing helpers for NMMiner Swarm."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import DEFAULT_TIMEOUT


class NMMinerApiError(Exception):
    """Raised when the NMMiner API cannot be read."""


@dataclass(frozen=True)
class NMMinerDevice:
    """Normalized NMMiner device data."""

    ip: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class NMMinerSwarmData:
    """Normalized NMMiner swarm data."""

    summary: dict[str, Any]
    devices: dict[str, NMMinerDevice]


class NMMinerApiClient:
    """Small async client for the NMMiner swarm endpoint."""

    def __init__(self, session: ClientSession, url: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        self._session = session
        self._url = normalize_url(url)
        self._timeout = timeout

    async def async_get_swarm(self) -> NMMinerSwarmData:
        """Fetch and normalize swarm data."""
        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.get(self._url)
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (TimeoutError, ClientError, ClientResponseError, ValueError) as err:
            raise NMMinerApiError(f"Unable to fetch NMMiner swarm data from {self._url}") from err

        if not isinstance(payload, dict):
            raise NMMinerApiError("NMMiner swarm endpoint did not return a JSON object")

        summary = payload.get("summary") or {}
        devices_raw = payload.get("devices") or []

        if not isinstance(summary, dict):
            summary = {}
        if not isinstance(devices_raw, list):
            devices_raw = []

        devices: dict[str, NMMinerDevice] = {}
        for item in devices_raw:
            if not isinstance(item, dict):
                continue
            ip = str(item.get("ip") or "").strip()
            if not ip:
                continue
            devices[ip] = NMMinerDevice(ip=ip, raw=item)

        return NMMinerSwarmData(summary=summary, devices=devices)


def normalize_url(url: str) -> str:
    """Normalize a configured URL.

    Accepts:
    - http://192.168.1.10/swarm
    - 192.168.1.10/swarm
    - 192.168.1.10
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"

    if url.endswith("/"):
        url = url[:-1]

    if not url.endswith("/swarm"):
        url = f"{url}/swarm"

    return url


_RATE_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([KMGTPE]?)(?:H/s)?\s*$", re.IGNORECASE)
_DIFF_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([KMGTPE]?)\s*$", re.IGNORECASE)

_MULTIPLIERS = {
    "": 1,
    "K": 1_000,
    "M": 1_000_000,
    "G": 1_000_000_000,
    "T": 1_000_000_000_000,
    "P": 1_000_000_000_000_000,
    "E": 1_000_000_000_000_000_000,
}


def parse_hashrate(value: Any) -> float | None:
    """Parse strings like 993.22KH/s, 1.9715M, or plain numbers into H/s."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None
    match = _RATE_RE.match(text)
    if not match:
        return parse_float(value)

    number = float(match.group(1))
    suffix = match.group(2).upper()
    return number * _MULTIPLIERS.get(suffix, 1)


def parse_difficulty(value: Any) -> float | None:
    """Parse difficulty-ish values like 139.0T, 480.5K, 1.000."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None

    # bestDiff sometimes looks like: "0.000 /480.5K".
    if "/" in text:
        text = text.split("/")[-1].strip()

    match = _DIFF_RE.match(text)
    if not match:
        return parse_float(text)

    number = float(match.group(1))
    suffix = match.group(2).upper()
    return number * _MULTIPLIERS.get(suffix, 1)


def parse_float(value: Any) -> float | None:
    """Parse a float or return None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:
    """Parse an int or return None."""
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(parsed)
