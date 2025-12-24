from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

class LianderCoordinator(DataUpdateCoordinator):
    """Coordinator voor dagelijkse Liander API updates."""

    def __init__(self, hass, api):
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )
        self.hass = hass
        self.api = api
        self.aansluitingen = []

    async def _async_update_data(self):
        profile = await self.api.get_profile()
        self.aansluitingen = profile.get("aansluitingKoppelingen", [])

        for aansluiting in self.aansluitingen:
            ean = aansluiting["ean"]
            try:
                await self.api.request_meter_reading(ean)
            except Exception as err:
                _LOGGER.warning("Meterstand aanvraag mislukt voor %s: %s", ean, err)

        return self.aansluitingen