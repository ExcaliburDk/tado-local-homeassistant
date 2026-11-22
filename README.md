# Tado Local - Home Assistant Integration

![Tado Local](https://img.shields.io/badge/Tado-Local_Control-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-green.svg)
![IoT Class](https://img.shields.io/badge/IoT_Class-Local_Push-orange.svg)
![Latest Version](https://img.shields.io/badge/Version-v1.1.6-brightgreen.svg)
![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)

## 🚀 Introduction
This custom integration for **Home Assistant** allows you to interface completely locally with your Tado devices via the **TadoLocal** bridge (e.g. running on QNAP NAS, Docker, or Raspberry Pi).

Unlike the standard Tado cloud integration, **this component does not rely on Tado Cloud for routine heating operations**. It communicates directly with the local bridge service via HomeKit and REST to retrieve real-time state and send commands. This ensures instant updates, zero internet latency, full offline functionality during internet outages, and eliminates Tado Cloud API rate limits.

---

## ✨ Key Features

- **100% Local Push Control**:
  - Uses Server-Sent Events (SSE) to update Home Assistant instantly the moment a change occurs (target temp, valve adjustment, window open).
  - Operates independently of Tado cloud servers.
- **Full Climate Control**:
  - `HEAT`: Set target temperature (5.0 °C to 25.0 °C in 0.5 °C steps).
  - `AUTO`: Resumes Tado Smart Schedule (`heating_enabled=true&persistant=true`).
  - `OFF`: Shuts off zone heating (maintains frost protection setpoint).
- **Real-time HVAC Action (`hvac_action`)**:
  - Displays actual valve state on Home Assistant cards: **Heating** (when valve is actively demanding heat), **Idle** (target reached), **Cooling**, or **Off**.
- **Thermostat Device & Room Mapping**:
  - Physical thermostat devices are automatically named after their assigned room: `Tado <Room> (<Serial>)` (e.g. `Tado Entrance (VA1229472256)`).
  - Automatically suggests the corresponding Home Assistant Area for easy organization.
- **Physical Device Identification ("Identify / Blink Display")**:
  - Adds an **Identify (Blink Display)** button for each physical radiator thermostat (VAxxx). Clicking it makes the thermostat's LED matrix blink, making physical device identification effortless.
- **On-Demand Cloud & Battery Sync**:
  - Dedicated **Sync Cloud and Batteries** button (`button.tado_local_sync_cloud_and_batteries`) triggers an instant background fetch (`POST /refresh/cloud`) to update battery levels and API quota stats.
- **Comprehensive Sensors**:
  - **Climate**: Thermostat entities for each zone with target temp, current temp, and `battery_low` attribute.
  - **Sensors**: Humidity levels, target/current temperatures, server status, API rate limit counters (Daily Limit, Used %, Remaining calls).
  - **Binary Sensors**: Heating active, cooling active, window open detection, battery warning.
  - **Configuration**: Configurable window open detection and timeout entities (up to 480 min).

---

## 📋 Changelog

### v1.1.6
- ✨ **Identify (Blink Display)**: Added `TadoIdentifyButton` entity for all radiator thermostats (`button.tado_<room>_<serial>_identify`). Pressing it physically blinks the LED display on the valve via HomeKit identify routine.
- 🌐 Added localized naming strings and icons for identify entities.

### v1.1.5
- 🔥 **Native `hvac_action`**: Climate entities now report real-time heating state (`HEATING` when `cur_heating` is true, `IDLE` when target temp reached, `OFF` when heating is disabled), giving accurate orange flame status in Lovelace cards.

### v1.1.4
- 🏷️ **Thermostat Device Naming**: Thermostats are now named `Tado <Room> (<Serial>)` instead of just serial numbers.
- 🏠 **Suggested Areas**: Automatically assigns Home Assistant Area matching the Tado room name upon discovery.
- 🔋 **Battery Low Attribute**: Added `battery_low` boolean attribute directly to climate entities for easy dashboard badges.
- 🔄 **Cloud & Battery Sync Button**: Added `Sync Cloud and Batteries` button entity calling `POST /refresh/cloud`.

### v1.1.3
- 🛡️ **Session Leak Fix**: Switched to Home Assistant's managed `async_get_clientsession(hass)` to resolve `aiohttp.ClientSession` warnings and leaks (Issue #11).
- ❄️ **Lower Min Temperature**: Reduced minimum target temperature from 7.0 °C to 5.0 °C.
- ⏱️ **Extended Window Timeout**: Expanded window open timeout configuration range up to 480 minutes (8 hours) (Issue #10).
- 📅 **Persistent Smart Schedule**: Fixed `AUTO` mode resume by sending `heating_enabled=true&persistant=true` (Issue #1).
- 📜 **License**: Added GPL-3.0 license to comply with upstream repository (Issue #9).

---

## 🛠️ Prerequisites

You must have the **TadoLocal** server running on your local network (e.g. running as a Docker container on QNAP NAS, Synology, Unraid, or Linux):
- GitHub Repository: [ExcaliburDk/TadoLocalForQnap_private](https://github.com/ExcaliburDk/TadoLocalForQnap_private)
- Default API Port: `4407` (or `4408` if mapped).

---

## 📦 Installation

### Option 1: Via HACS (Recommended)
1. In Home Assistant, open **HACS** → **Integrations**.
2. Click the three dots in the top right corner → **Custom repositories**.
3. Enter Repository URL: `https://github.com/ExcaliburDk/tado-local-homeassistant` and Category: **Integration**.
4. Click **Add**, find **Tado Local** in the list, and click **Download**.
5. Restart Home Assistant.
6. Go to **Settings** → **Devices & Services** → **Add Integration** → search for **Tado Local**.
7. Enter your TadoLocal Server IP (e.g. `10.0.0.181`) and Port (`4407` or `4408`).

### Option 2: Manual Installation
1. Download the latest release from the [Releases](https://github.com/ExcaliburDk/tado-local-homeassistant/releases) page.
2. Copy the `custom_components/tado_local` folder into your Home Assistant `<config>/custom_components/` directory.
3. Restart Home Assistant.
4. Add the integration via **Settings** → **Devices & Services**.

---

## ☕ Credits & Attribution
- Based on upstream work by [array81/tado-local](https://github.com/array81/tado-local) and [ampscm/TadoLocal](https://github.com/ampscm/TadoLocal).
- Maintained and extended by [@ExcaliburDk](https://github.com/ExcaliburDk).

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.
