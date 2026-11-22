import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import EntityCategory
from .const import DOMAIN, MASTER_DEVICE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tado Local buttons."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    base_url = data["base_url"]

    entities = []
    devices = coordinator.data.get("devices", []) if coordinator.data else []
    for device in devices:
        dev_type = device.get("device_type")
        if dev_type == MASTER_DEVICE:
            entities.append(TadoCloudSyncButton(coordinator, device, base_url))
        elif dev_type == "thermostat":
            entities.append(TadoIdentifyButton(coordinator, device, base_url))

    async_add_entities(entities)


class TadoCloudSyncButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger cloud refresh (e.g. for battery status)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:cloud-sync"
    _attr_translation_key = "refresh_cloud"

    def __init__(self, coordinator, device_data, base_url):
        super().__init__(coordinator)
        self._device_id = device_data.get("device_id") or device_data.get("id")
        self._base_url = base_url
        self._attr_unique_id = f"tado_local_cloud_sync_{self._device_id}"
        self._device_info_data = {
            "identifiers": {(DOMAIN, "device", self._device_id)}
        }

    @property
    def device_info(self):
        return self._device_info_data

    async def async_press(self) -> None:
        """Handle the button press."""
        url = f"{self._base_url}/refresh/cloud"
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url) as response:
                if response.status == 200:
                    _LOGGER.info("Tado cloud battery sync completed successfully")
                    await self.coordinator.async_request_refresh()
                else:
                    _LOGGER.error("Failed to refresh Tado cloud: %s", await response.text())
        except Exception as err:
            _LOGGER.error("Error connecting to TadoLocal server during cloud sync: %s", err)


class TadoIdentifyButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger physical thermostat display blinking / identify."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:flash-outline"
    _attr_translation_key = "identify"

    def __init__(self, coordinator, device_data, base_url):
        super().__init__(coordinator)
        self._device_id = device_data.get("device_id") or device_data.get("id")
        self._base_url = base_url
        self._attr_unique_id = f"tado_local_identify_{self._device_id}"
        self._device_info_data = {
            "identifiers": {(DOMAIN, "device", self._device_id)}
        }

    @property
    def device_info(self):
        return self._device_info_data

    async def async_press(self) -> None:
        """Handle the button press."""
        url = f"{self._base_url}/devices/{self._device_id}/identify"
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(url) as response:
                if response.status == 200:
                    _LOGGER.info("Tado identify triggered for device %s", self._device_id)
                else:
                    _LOGGER.warning("Failed to trigger identify on device %s: %s", self._device_id, await response.text())
        except Exception as err:
            _LOGGER.error("Error triggering identify for device %s: %s", self._device_id, err)
