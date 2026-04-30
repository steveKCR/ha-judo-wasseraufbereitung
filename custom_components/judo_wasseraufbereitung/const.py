"""Konstanten für die JUDO Wasseraufbereitung Integration."""

from __future__ import annotations

DOMAIN = "judo_wasseraufbereitung"
MANUFACTURER = "JUDO Wasseraufbereitung GmbH"
MODEL = "i-soft K SAFE+"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Connectivity"

SCAN_INTERVAL_OPTIONS = {
    30: "30 Sekunden",
    60: "1 Minute",
    120: "2 Minuten",
    300: "5 Minuten",
}

# Geräte-Typcodes für i-soft K SAFE+
SUPPORTED_DEVICE_TYPES = (0x42, 0x67)

# Wunschwasserhärte 1–30 °dH als Dropdown
WATER_HARDNESS_OPTIONS: list[str] = [str(i) for i in range(1, 31)]
