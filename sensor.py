from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfVolume
)
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="status",
        name="Status",
        translation_key="status"
    ),
    SensorEntityDescription(
        key="meter_reading",
        name="Meter reading",
        translation_key="meter_reading",
        icon="mdi:counter",
    ),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for connection in coordinator.data:
        entities.extend([
            LianderSensor(coordinator, connection, description, entry)
            for description in SENSOR_DESCRIPTIONS
        ])

    async_add_entities(entities)

class LianderSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, connection, description, entry):
        super().__init__(coordinator)
        self._connection = connection
        self._description = description
        self._entry = entry

        if description.key == "meter_reading":
            type = connection.get("type")
            if type == "Gasaansluiting":
                self._attr_device_class = SensorDeviceClass.GAS
                self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
            elif type == "ElektraAansluiting":
                self._attr_device_class = SensorDeviceClass.ENERGY
                self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def name(self):
        return self._description.name

    @property
    def unique_id(self):
        ean = self._connection.get("ean")

        return f"{ean}_{self.device_name()}_{self._description.key}"

    @property
    def translation_key(self):
        return self._description.translation_key or None

    @property
    def device_info(self):
        ean = self._connection.get("ean")

        return DeviceInfo(
            identifiers={(DOMAIN, ean)},
            name=self.device_name(),
            manufacturer="Liander",
            model=f"{self._connection.get("type")} ({ean[-4:]})",
            configuration_url="https://mijn-liander.web.liander.nl",
            serial_number=ean
        )

    def device_name(self):
        type = self._connection.get("type")
        if type == "Gasaansluiting":
            return "Gas meter"
        if type == "ElektraAansluiting":
            return "Electric meter"
        raise Exception(f"Unknown connection type: {type}")

    @property
    def icon(self):
        return self._description.icon or None

    @property
    def native_value(self):
        match self._description.key:
            case "ean":
                return self._connection.get("ean")
            case "status":
                return self._connection.get("status")
            case "meter_reading":
                return self._connection.get("meter_reading", 0)