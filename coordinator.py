from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

class LianderCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )
        self.hass = hass
        self.api = api

    async def _async_update_data(self):
        connections = await self.api.get_connections()
        connections = connections[0]["aansluitingen"]
        connections = connections["elektra"] + connections["gas"]

        data = []
        for connection in connections:
            ean = connection["ean"]
            try:
                meter_reading = await self.api.request_meter_reading(ean)
                _LOGGER.warning("Meter reading response for %s: %s", ean, meter_reading)
            except Exception as err:
                _LOGGER.warning("Meterstand aanvraag mislukt voor %s: %s", ean, err)
                meter_reading = None

            data.append({
                "type": connection["type"],
                "ean": ean,
                "status": connection["status"],
                "meter_reading": meter_reading,
            })

        return data