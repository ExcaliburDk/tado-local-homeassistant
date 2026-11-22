# Tado Local - Home Assistant Integration

![Tado Local](https://img.shields.io/badge/Tado-Local_Control-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-green.svg)
![IoT Class](https://img.shields.io/badge/IoT_Class-Local_Push-orange.svg)
![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)

## 🚀 Introduction
This custom integration for **Home Assistant** allows you to interface completely locally with your Tado devices via the [TadoLocal](https://github.com/ampscm/TadoLocal) bridge.
Unlike the standard cloud integration, **this component does not rely on Tado Cloud for routine operation**. It communicates directly with the local bridge service to retrieve status and send commands. This ensures instant updates, works without an internet connection, and avoids API rate limits.

## ✨ Features
- **100% Local Control**: No cloud dependency for daily temperature and state changes.
- **Instant Updates (Local Push)**: Uses Server-Sent Events (SSE) to update Home Assistant the moment a change occurs (e.g. window open, manual adjustment).
- **Smart Control Modes**:
  - `OFF` (0°C): Turns off heating for the zone (maintaining setpoint).
  - `AUTO`: Resumes the Tado Smart Schedule using persistent heating (`heating_enabled=true&persistant=true`).
  - `HEAT`: Sets a manual target temperature (down to 5.0 °C).
- **Detailed Sensors**:
  - **Climate**: Thermostat control for every zone (min 5.0 °C, max 25.0 °C, step 0.5 °C).
  - **Sensors**: Humidity levels, target/current temperatures, server status, API quotas, and serial numbers.
  - **Binary Sensors**: Heating active status, cooling active status, open window status, and battery low warnings.
  - **Diagnostic Text**: Configurable window open/rest timeout entities (up to 480 min).

## 🛠 Prerequisites
Before installing this integration, you **must** have the **TadoLocal** server running on your network (for example on QNAP NAS or Docker).
The integration connects to the TadoLocal API (default port `4407`, test port `4408`).

## 🛠 Installation

### 1️⃣ Install via HACS (Recommended)
1. Open Home Assistant and navigate to **HACS** → **Integrations** → **Custom Repositories**.
2. Add your repository URL (`https://github.com/ExcaliburDk/tado-local-homeassistant`) as type **Integration**.
3. Download and restart Home Assistant.
4. Navigate to **Settings** → **Devices & Services** → **Add Integration** → Search for **Tado Local**.
5. Enter your TadoLocal IP (e.g. `10.0.0.181`) and Port (`4407` or `4408`).

### 2️⃣ Manual Installation
1. Copy the `custom_components/tado_local` directory into your Home Assistant `/config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings** → **Devices & Services**.

## ☕ Credits & Attribution
Based on the upstream work by [array81/tado-local](https://github.com/array81/tado-local) and the underlying TadoLocal server by [ampscm](https://github.com/ampscm/TadoLocal).

## 📜 License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0) to match the upstream repository license and resolve Issue #9.
