"""Binary sensor platform for dahua."""
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from custom_components.dahua import DahuaDataUpdateCoordinator

from .const import (
    BELL_ICON, DOMAIN, DOOR_DEVICE_CLASS
)
from .entity import DahuaBaseEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup invite_sensor platform."""
    coordinator: DahuaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[DahuaSensor] = []

    if coordinator.is_doorbell():
        sensors.append(DahuaSensor(coordinator, entry, "Invite"))

    if sensors:
        async_add_devices(sensors)


class DahuaSensor(DahuaBaseEntity, SensorEntity):
    """
    dahua invite_sensor class to record events.
    """

    def __init__(self, coordinator: DahuaDataUpdateCoordinator, config_entry, event_name: str):
        DahuaBaseEntity.__init__(self, coordinator, config_entry)
        SensorEntity.__init__(self)

        # event_name is the event name, example: Invite
        self._event_name = event_name

        self._coordinator = coordinator
        self._device_name = coordinator.get_device_name()
        self._device_class = DOOR_DEVICE_CLASS

        self._name = re.sub(r"(?<![A-Z])(?<!^)([A-Z])", r" \1", event_name)

        # Build the unique ID. This will convert the name to lower underscores. For example, "Smart Motion Vehicle" will
        # become "smart_motion_vehicle" and will be added as a suffix to the device serial number
        self._unique_id = coordinator.get_serial_number() + "_" + self._name.lower().replace(" ", "_")

    @property
    def unique_id(self):
        """Return the entity unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the binary_sensor. Example: Cam14 Motion Alarm"""
        return f"{self._device_name} {self._name}"

    @property
    def device_class(self):
        """Return the class of this binary_sensor, Example: motion"""
        return self._device_class

    @property
    def icon(self) -> str:
        return BELL_ICON

    @property
    def native_value(self) -> int:
        return self._coordinator.get_event_data(self._event_name).get('UserID')

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self._coordinator.add_dahua_event_listener(self._event_name, self.schedule_update_ha_state)

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.  False if entity pushes its state to HA"""
        return False
