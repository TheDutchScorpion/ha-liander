from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for connetion in coordinator.data:
        type = connetion["type"]
        ean = connetion["ean"]
        status = connetion.get("status", "unknown")

        entities.extend([
            EANSensor(type, ean),
            StatusSensor(type, ean, status),
            MeterReadingSensor(type, ean, coordinator),
        ])

    async_add_entities(entities)

class BaseSensor(SensorEntity):
    def __init__(self, type: str, ean: str):
        self._type = type
        self._ean = ean

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._ean)},
            name=f"Aansluiting {self._ean[-4:]}",
            manufacturer="Liander",
            model=self._type,
            configuration_url="https://mijn.liander.nl",
        )

class EANSensor(BaseSensor):
    @property
    def name(self):
        return "EAN"

    @property
    def unique_id(self):
        return f"{self._ean}_ean"

    @property
    def state(self):
        return self._ean

class StatusSensor(BaseSensor):
    def __init__(self, type, ean, status):
        super().__init__(type, ean)
        self._status = status

    @property
    def name(self):
        return "Status"

    @property
    def unique_id(self):
        return f"{self._ean}_status"

    @property
    def state(self):
        return self._status

class MeterReadingSensor(BaseSensor):
    def __init__(self, type, ean, coordinator):
        super().__init__(type, ean)
        self.coordinator = coordinator

    @property
    def name(self):
        return "Meter reading"

    @property
    def unique_id(self):
        return f"{self._ean}_meter_reading"

    @property
    def state(self):
        return self.coordinator.data.get(self._ean)