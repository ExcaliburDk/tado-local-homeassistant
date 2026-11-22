"""Provide a text platform for TadoLocal."""
import logging
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, MANUFACTURER, format_model

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up this platform for a specific ConfigEntry(==Gateway)."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    base_url = data["base_url"]

    entities = []
    zones = coordinator.data.get("zones", [])
    for zone in zones:
        entities.append(TadoWindowOpenTimeout(coordinator, zone, base_url))
        entities.append(TadoWindowRestTimeout(coordinator, zone, base_url))

    async_add_entities(entities)


class TadoWindowOpenTimeout(CoordinatorEntity, TextEntity):
    """Representation of the value of Window open timeout."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:timer-refresh"
    _attr_translation_key = "window_open_timeout"
    # Issue #10 Fix: Allow min length 0 to avoid Home Assistant validation crash on empty/0, max length 5
    _attr_native_min = 0
    _attr_native_max = 5

    def __init__(self, coordinator, zone_data, base_url):
        super().__init__(coordinator)
        self._zone_id = zone_data.get("zone_id") or zone_data.get("id")
        self._zone_name = zone_data.get("name") or f"Zone {self._zone_id}"
        self._attr_unique_id = f"tado_local_window_open_{self._zone_id}"
        self._attr_suggested_object_id = f"{slugify(self._zone_name)}_window_open_timeout"
        self._tado_zone_id = zone_data.get("tado_zone_id", "")
        self._base_url = base_url

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "zone", self._zone_id)},
            "name": self._zone_name,
            "manufacturer": MANUFACTURER,
            "model": format_model("zone_control"),
        }

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the text."""
        zones = self.coordinator.data.get("zones", []) if self.coordinator.data else []
        for zone in zones:
            zid = zone.get("zone_id") or zone.get("id")
            if zid == self._zone_id:
                val = zone.get("window_open_time", 0)
                return str(val if val is not None else 0)
        return "0"

    async def async_set_value(self, value: str) -> None:
        """Change the value."""
        if not value.isdigit() and value != "-1":
            raise ValueError(f"Invalid number '{value}'")
        int_val = int(value)
        if int_val < -1 or int_val > 480:
            raise ValueError(f"Invalid value '{value}', not between -1 and 480")
        _LOGGER.debug("Set window open timeout to %s", value)
        url = f"{self._base_url}/zones/{self._zone_id}/windowtimeouts"
        params = {"window_open_time": str(value)}
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    _LOGGER.error("Errore update Tado: %s", await response.text())
                else:
                    await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Errore connessione update: %s", err)


class TadoWindowRestTimeout(CoordinatorEntity, TextEntity):
    """Representation of the value of Window rest timeout."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:timer-pause"
    _attr_translation_key = "window_rest_timeout"
    # Issue #10 Fix: Allow min length 0 to avoid Home Assistant validation crash on empty/0, max length 5
    _attr_native_min = 0
    _attr_native_max = 5

    def __init__(self, coordinator, zone_data, base_url):
        super().__init__(coordinator)
        self._zone_id = zone_data.get("zone_id") or zone_data.get("id")
        self._zone_name = zone_data.get("name") or f"Zone {self._zone_id}"
        self._attr_unique_id = f"tado_local_window_rest_{self._zone_id}"
        self._attr_suggested_object_id = f"{slugify(self._zone_name)}_window_rest_timeout"
        self._tado_zone_id = zone_data.get("tado_zone_id", "")
        self._base_url = base_url

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "zone", self._zone_id)},
            "name": self._zone_name,
            "manufacturer": MANUFACTURER,
            "model": format_model("zone_control"),
        }

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the text."""
        zones = self.coordinator.data.get("zones", []) if self.coordinator.data else []
        for zone in zones:
            zid = zone.get("zone_id") or zone.get("id")
            if zid == self._zone_id:
                val = zone.get("window_rest_time", 0)
                return str(val if val is not None else 0)
        return "0"

    async def async_set_value(self, value: str) -> None:
        """Change the value."""
        if not value.isdigit() and value != "-1":
            raise ValueError(f"Invalid number '{value}'")
        int_val = int(value)
        if int_val < -1 or int_val > 480:
            raise ValueError(f"Invalid value '{value}', not between -1 and 480")
        _LOGGER.debug("Set window rest timeout to %s", value)
        url = f"{self._base_url}/zones/{self._zone_id}/windowtimeouts"
        params = {"window_rest_time": str(value)}
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    _LOGGER.error("Errore update Tado: %s", await response.text())
                else:
                    await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Errore connessione update: %s", err)
