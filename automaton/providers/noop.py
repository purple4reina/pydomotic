import logging

from .base import Provider, Device

logger = logging.getLogger(__name__)

class NoopProvider(Provider):

    def get_device(self, device_id, device_name):
        return NoopDevice(device_id, device_name)

class NoopDevice(Device):

    def turn_on(self):
        logger.debug('device "%s" turned on', self.name)

    def turn_off(self):
        logger.debug('device "%s" turned off', self.name)

    def switch(self):
        logger.debug('device "%s" switched', self.name)
