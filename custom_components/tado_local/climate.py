import logging
from typing import Any, Dict

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_NONE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
    PRECISION_TENTHS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, MANUFACTURER, format_model

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Configura le entità Climate."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    base_url = data["base_url"]

    entities = []
    zones_list = coordinator.data.get("zones", [])

    for zone in zones_list:
        entities.append(TadoLocalClimate(coordinator, zone, base_url))

    async_add_entities(entities)


class TadoLocalClimate(CoordinatorEntity, ClimateEntity):
    """Rappresentazione di una Zona Tado Local."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_precision = PRECISION_TENTHS
    _attr_min_temp = 5.0
    _attr_max_temp = 25.0
    _attr_target_temperature_step = 0.5

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.PRESET_MODE
    )

    _attr_preset_modes = [PRESET_HOME, PRESET_AWAY, PRESET_NONE]

    def __init__(self, coordinator, initial_data, base_url):
        super().__init__(coordinator)
        self._zone_id = initial_data.get("zone_id") or initial_data.get("id")
        self._attr_name = ""  # remove double name from Climate control
        self._device_name = initial_data.get("name", f"Zone {self._zone_id}")
        self._attr_unique_id = f"tado_local_zone_{self._zone_id}"
        self._base_url = base_url
        self._attr_preset_mode = PRESET_NONE
        self._update_preset_count = 0

        self._can_cool = (
            initial_data.get("zone_type", "HEATING") == "AIR_CONDITIONING"
        )
        if self._can_cool:
            self._attr_hvac_modes = [
                HVACMode.HEAT,
                HVACMode.COOL,
                HVACMode.OFF,
                HVACMode.AUTO,
            ]
        else:
            self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]

    @property
    def device_info(self):
        """Device Info per la Zona Logica."""
        return {
            "identifiers": {(DOMAIN, "zone", self._zone_id)},
            "name": self._device_name,
            "manufacturer": MANUFACTURER,
            "model": format_model("zone_control"),
        }

    @property
    def _zone_data(self) -> dict:
        raw_data = self.coordinator.data
        if not raw_data:
            return {}
        zones_list = raw_data.get("zones", [])
        for zone in zones_list:
            zid = zone.get("zone_id") or zone.get("id")
            if zid == self._zone_id:
                return zone.get("state", zone)
        return {}

    @property
    def current_temperature(self):
        return self._zone_data.get("cur_temp_c")

    @property
    def target_temperature(self):
        return self._zone_data.get("target_temp_c")

    @property
    def hvac_mode(self) -> HVACMode:
        mode = self._zone_data.get("mode")
        if self._update_preset_count > 0:
            self._update_preset_count -= 1

        if mode == 0:
            if self._attr_preset_mode == PRESET_HOME and self._update_preset_count == 0:
                self._attr_preset_mode = PRESET_NONE
            return HVACMode.OFF

        if self._attr_preset_mode == PRESET_HOME:
            return HVACMode.AUTO

        if self._attr_preset_mode == PRESET_AWAY and self._update_preset_count == 0:
            self._attr_preset_mode = PRESET_NONE
        return HVACMode.COOL if (mode == 2 and self._can_cool) else HVACMode.HEAT

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.AUTO:
            self._attr_preset_mode = PRESET_NONE
            # Issue #1 Fix: Use persistent heating_enabled=true to resume Tado Smart Schedule
            url = f"{self._base_url}/zones/{self._zone_id}/set"
            params = {
                "persistant": "true",
                "heating_enabled": "true",
            }
            session = async_get_clientsession(self.hass)
            try:
                async with session.post(url, params=params) as response:
                    if response.status != 200:
                        _LOGGER.error("Errore resume schedule Tado: %s", await response.text())
                    else:
                        await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Errore connessione resume schedule: %s", err)
            return

        mode = None
        temp_param = None
        if hvac_mode == HVACMode.OFF:
            mode = 0
            temp_param = 0
        elif hvac_mode == HVACMode.HEAT:
            mode = 1
            temp_param = -1
        elif hvac_mode == HVACMode.COOL and self._can_cool:
            mode = 2
        else:
            _LOGGER.debug("Errore invalid mode: %s", hvac_mode)
            return

        await self._async_send_zone_update(temperature=temp_param, mode=mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode

        if preset_mode == PRESET_NONE:
            return

        if self._update_preset_count > 0:
            return
        self._update_preset_count = 4

        url = f"{self._base_url}/zones/{self._zone_id}/set"
        params = {
            "persistant": "true",
            "heating_enabled": "true" if preset_mode == PRESET_HOME else "false",
        }

        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    _LOGGER.error("Errore update Tado: %s", await response.text())
                else:
                    await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Errore connessione update: %s", err)

        _LOGGER.debug("Preset: %s ", self._attr_preset_mode)
        self._attr_preset_mode = preset_mode

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        devices = self.coordinator.data.get("devices", []) if self.coordinator.data else []
        zone_devices = [
            d for d in devices
            if d.get("zone_id") == self._zone_id
        ]
        if zone_devices:
            attrs["battery_low"] = any(
                d.get("state", {}).get("battery_low", False) for d in zone_devices
            )
            attrs["devices"] = [
                d.get("serial_number") for d in zone_devices if d.get("serial_number")
            ]
        return attrs

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        await self._async_send_zone_update(temp)

    async def _async_send_zone_update(self, temperature=None, mode=None):
        url = f"{self._base_url}/zones/{self._zone_id}/set"
        params = {}
        if temperature is not None:
            params["temperature"] = str(temperature)
        if mode is not None:
            params["heating_mode"] = str(mode)
        if not params:
            return

        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    _LOGGER.error("Errore update Tado: %s", await response.text())
                else:
                    await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Errore connessione update: %s", err)
