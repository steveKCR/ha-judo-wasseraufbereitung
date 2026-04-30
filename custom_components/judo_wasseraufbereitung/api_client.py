"""REST-API-Client für JUDO i-soft K SAFE+."""

from __future__ import annotations

import asyncio
import logging
import re

import aiohttp

_LOGGER = logging.getLogger(__name__)

_HEX_PATTERN = re.compile(r"^[0-9a-fA-F]*$")
_CONNECT_TIMEOUT = 10
_READ_TIMEOUT = 15


def _validate_hex(value: str) -> str:
    if not _HEX_PATTERN.match(value):
        raise ValueError(f"Invalid hex string: {value!r}")
    return value


def _parse_int_lsb(hex_str: str, num_bytes: int) -> int:
    """Little-Endian Hex zu Integer."""
    data = bytes.fromhex(hex_str[: num_bytes * 2])
    return int.from_bytes(data, byteorder="little")


def _int_to_hex_lsb(value: int, num_bytes: int) -> str:
    """Integer zu Little-Endian Hex (uppercase)."""
    return value.to_bytes(num_bytes, byteorder="little").hex().upper()


class JudoApiClient:
    """Schlanker Client speziell für i-soft K SAFE+."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._host = host
        self._auth = aiohttp.BasicAuth(username, password)
        self._session = session
        self._base_url = f"http://{host}"
        self._timeout = aiohttp.ClientTimeout(
            connect=_CONNECT_TIMEOUT, total=_READ_TIMEOUT
        )

    @property
    def host(self) -> str:
        return self._host

    async def _send(self, command_hex: str, data_hex: str = "") -> str:
        """REST-Befehl absenden mit 429-Retry."""
        _validate_hex(command_hex)
        if data_hex:
            _validate_hex(data_hex)

        url = f"{self._base_url}/api/rest/{command_hex}{data_hex}"
        _LOGGER.debug("GET %s", url)

        try:
            return await self._do_request(url)
        except _Retry:
            _LOGGER.debug("Gerät beschäftigt (429), Retry in 2s: %s", url)
            await asyncio.sleep(2)
            try:
                return await self._do_request(url)
            except _Retry as err:
                raise JudoConnectionError(
                    f"Gerät {self._host} dauerhaft beschäftigt"
                ) from err

    async def _do_request(self, url: str) -> str:
        try:
            async with self._session.get(
                url, auth=self._auth, timeout=self._timeout
            ) as response:
                if response.status == 401:
                    raise JudoAuthError("Ungültige Anmeldedaten")
                if response.status == 429:
                    raise _Retry()
                if response.status != 200:
                    raise JudoCommandError(
                        f"HTTP {response.status} für {url}"
                    )
                result = await response.json(content_type=None)
                if isinstance(result, dict) and "data" in result:
                    return str(result["data"])
                return ""
        except aiohttp.ClientError as err:
            raise JudoConnectionError(
                f"Verbindung zu {self._host} fehlgeschlagen: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise JudoConnectionError(
                f"Verbindung zu {self._host} Timeout"
            ) from err

    # ------------------------------------------------------------------ #
    # Lese-Befehle                                                        #
    # ------------------------------------------------------------------ #

    async def get_device_type(self) -> int:
        """0xFF – Gerätetyp."""
        data = await self._send("FF", "00")
        return int(data, 16) if data else 0

    async def get_serial_number(self) -> int:
        """0x06 – Seriennummer (4 Byte LSB)."""
        data = await self._send("06", "00")
        return _parse_int_lsb(data, 4) if data else 0

    async def get_software_version(self) -> str:
        """0x01 – Softwareversion."""
        data = await self._send("01", "00")
        if not data or len(data) < 6:
            return "unbekannt"
        b = bytes.fromhex(data[:6])
        major = b[2]
        minor = b[1]
        patch_char = chr(b[0]) if 0x20 <= b[0] <= 0x7E else ""
        return f"{major}.{minor}{patch_char}"

    async def get_water_hardness(self) -> int:
        """0x51 – aktuelle Wunschwasserhärte in °dH."""
        data = await self._send("51", "00")
        return _parse_int_lsb(data, 2) if data and len(data) >= 4 else 0

    async def get_total_water(self) -> int:
        """0x28 – Gesamtwassermenge in Litern."""
        data = await self._send("28", "00")
        return _parse_int_lsb(data, 4) if data and len(data) >= 8 else 0

    async def get_soft_water(self) -> int:
        """0x29 – Enthärtetes Wasser in Litern."""
        data = await self._send("29", "00")
        return _parse_int_lsb(data, 4) if data and len(data) >= 8 else 0

    async def get_salt_supply(self) -> tuple[int, int]:
        """0x56 – Salzvorrat: (Gewicht in g, Reichweite in Tagen)."""
        data = await self._send("56", "00")
        if not data or len(data) < 8:
            return (0, 0)
        weight = _parse_int_lsb(data[:4], 2)
        days = _parse_int_lsb(data[4:8], 2)
        return weight, days

    # ------------------------------------------------------------------ #
    # Schreib-Befehle                                                     #
    # ------------------------------------------------------------------ #

    async def set_water_hardness(self, dh: int) -> None:
        """0x30 – Wunschwasserhärte setzen (1–30 °dH)."""
        if not 1 <= dh <= 30:
            raise ValueError(f"°dH muss 1–30 sein, war {dh}")
        await self._send("30", f"00{dh:02X}")

    async def open_leak_protection(self) -> None:
        """0x3D – Leckageschutz öffnen (Wasser an)."""
        await self._send("3D", "00")

    async def close_leak_protection(self) -> None:
        """0x3C – Leckageschutz schließen (Wasser aus)."""
        await self._send("3C", "00")


# ---------------------------------------------------------------------- #
# Exceptions                                                              #
# ---------------------------------------------------------------------- #


class JudoConnectionError(Exception):
    """Verbindungsfehler."""


class JudoAuthError(Exception):
    """Authentifizierungsfehler."""


class JudoCommandError(Exception):
    """Befehlsausführungsfehler."""


class _Retry(Exception):
    """Internes Signal für 429-Retry."""
