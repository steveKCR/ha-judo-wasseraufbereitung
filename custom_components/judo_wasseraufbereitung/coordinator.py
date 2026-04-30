"""Data update coordinator für JUDO i-soft K SAFE+."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api_client import (
    JudoApiClient,
    JudoAuthError,
    JudoConnectionError,
)
from .const import DOMAIN, MODEL

_LOGGER = logging.getLogger(__name__)


class JudoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polling-Coordinator – nur die für i-soft K SAFE+ nötigen Befehle."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: JudoApiClient,
        scan_interval: int,
    ) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{MODEL}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.serial_number: int = 0
        self.sw_version: str = "unbekannt"
        self._initial_fetch_done = False
        # Für Durchfluss-Berechnung
        self._prev_total_water: int | None = None
        self._prev_total_water_time: datetime | None = None

    async def _fetch_static(self) -> None:
        """Statische Daten einmalig holen."""
        try:
            self.serial_number = await self.client.get_serial_number()
            self.sw_version = await self.client.get_software_version()
        except (JudoConnectionError, JudoAuthError):
            _LOGGER.warning("Statische Gerätedaten konnten nicht gelesen werden")

    async def _async_update_data(self) -> dict[str, Any]:
        """Aktuelle Werte holen."""
        if not self._initial_fetch_done:
            await self._fetch_static()
            self._initial_fetch_done = True

        # Lokale Snapshots der Tracking-Werte – erst nach Erfolg übernehmen
        prev_water = self._prev_total_water
        prev_time = self._prev_total_water_time
        new_water: int | None = None
        new_time: datetime | None = None

        try:
            water_hardness = await self.client.get_water_hardness()
            total_water = await self.client.get_total_water()
            soft_water = await self.client.get_soft_water()
            salt_weight_g, salt_range_days = await self.client.get_salt_supply()

            now = datetime.now(timezone.utc)
            current_flow_lph: float | None = None
            if prev_water is not None and prev_time is not None:
                delta_l = total_water - prev_water
                delta_s = (now - prev_time).total_seconds()
                if delta_s > 0 and delta_l >= 0:
                    current_flow_lph = round(delta_l / delta_s * 3600, 1)
                else:
                    current_flow_lph = 0.0
            new_water = total_water
            new_time = now

            data: dict[str, Any] = {
                "water_hardness": water_hardness,
                "total_water_l": total_water,
                "soft_water_l": soft_water,
                "salt_weight_g": salt_weight_g,
                "salt_range_days": salt_range_days,
                "current_flow_lph": current_flow_lph,
            }

            # Tracking-Werte erst nach erfolgreichem Update commiten
            if new_water is not None and new_time is not None:
                self._prev_total_water = new_water
                self._prev_total_water_time = new_time

            return data

        except JudoAuthError as err:
            raise UpdateFailed(f"Authentifizierung fehlgeschlagen: {err}") from err
        except JudoConnectionError as err:
            raise UpdateFailed(f"Verbindung fehlgeschlagen: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Datenabruf: {err}") from err
