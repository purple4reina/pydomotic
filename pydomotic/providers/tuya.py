import gosundpy
import logging

from .base import Provider, Device

logger = logging.getLogger(__name__)

class TuyaProvider(Provider):

    def __init__(self, username, password, access_id, access_key,
            status_cache_seconds=None, timeout=None):
        self.tuya = gosundpy.Gosund(username, password, access_id, access_key,
                status_cache_seconds=status_cache_seconds, timeout=timeout)

    def get_device(self, device_id, device_name, device_description):
        device = self.tuya.get_device(device_id)
        return TuyaDevice(device, device_name, device_description)

class TuyaDevice(Device):

    def turn_on(self):
        self.device.turn_on()
        logger.debug('device "%s" turned on', self.name)

    def turn_off(self):
        self.device.turn_off()
        logger.debug('device "%s" turned off', self.name)

    def switch(self):
        self.device.switch()
        logger.debug('device "%s" switched', self.name)

    def current_temperature(self):
        return self.device.get_temperature()
