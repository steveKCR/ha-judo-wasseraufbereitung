# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-07

### Added

- Initial release of JUDO JUcontrol Local integration
- Support for all major JUDO device families:
  - **i-soft SAFE+** / **i-soft K SAFE+** (water softener with leak protection)
  - **i-soft PRO** / **i-soft PRO L** (water softener with leak protection and scenes)
  - **i-soft** / **i-soft K** (water softener with leak alarm)
  - **SOFTwell P / S / K / KP / KS** (basic water softener)
  - **ZEWA i-SAFE** / **PROM-i-SAFE** / **ZEWA i-SAFE FILT** (leak protection)
  - **i-dos eco** (dosing pump)
  - **i-fill 60** (heating fill system)
- Auto-detection of device type during setup
- Configurable polling interval (30s, 1min, 2min, 5min, 10min)
- **Sensors**: water hardness, salt supply (weight & range), total/soft water volume, operating hours, extraction limits, dosing status, fill pressure, and more
- **Buttons**: start regeneration, reset notification, start micro-leak test, start learning mode
- **Switches**: leak protection, vacation mode, sleep mode
- **Numbers**: desired water hardness, salt supply, salt shortage warning, max extraction duration/volume/flow rate, sleep duration
- **Selects**: hardness unit, pump operation mode, fill valve mode, micro-leak mode
- **Binary Sensors**: learning mode active
- Options flow for changing polling interval after setup
- English and German translations
- Diagnostics support
- MIT License

[1.0.0]: https://github.com/timo-neumeier/JUcontrol_local/releases/tag/v1.0.0
