from datetime import timedelta
import logging
import asyncio
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
        try:
            connections = await self.api.get_connections()
            connections = connections[0]["aansluitingen"]
            connections = connections["elektra"] + connections["gas"]

            data = []
            for connection in connections:
                ean = connection["ean"]
                data.append({
                    "type": connection["type"],
                    "ean": ean,
                    "status": connection["status"],
                    "meter_reading": None,
                })

            self.hass.async_create_task(self._fetch_meter_readings(data))

            return data
        except Exception as err:
            _LOGGER.error("Error has been thrown while updating Liander coordinator: %s", err)
            raise UpdateFailed(err)

    async def _fetch_meter_readings(self, data):
        for item in data:
            ean = item["ean"]
            try:
                request_id = await self.api.get_meter_reading_request_id(ean)

                for _ in range(20):
                    await asyncio.sleep(15)

                    result = await self.api.get_meter_reading(ean, request_id)
                    _LOGGER.warning("Received meter reading response: %s", result)
                    if result.get("laatstOntvangenOpDatum"):
                        type = item["type"]
                        if type == "Gasaansluiting":
                            item["meter_reading"] = result.get("gasVolume")
                        elif type == "ElektraAansluiting":
                            wattage = (result.get("elektraImportT1", 0) + result.get("elektraImportT2", 0))
                            item["meter_reading"] = wattage / 1000
                        else:
                            raise Exception(f"Unknown connection type: {type}")

                        self.async_set_updated_data(cloned_data)

                        break
                else:
                    _LOGGER.warning("Unable to receive meter reading for EAN %s with request id %s within 5 minutes", ean, request_id)

            except Exception as e:
                _LOGGER.error("Error with receiving meter readings for EAN %s: %s", ean, e)