import logging

from .base import Provider, Device

logger = logging.getLogger(__name__)

class NoopProvider(Provider):

    def get_device(self, device_id):
        return NoopDevice(device_id)

class NoopDevice(Device):

    def __init__(self, device_id):
        self.device_id = device_id

    def turn_on(self):
        logger.debug('device "%s" turned on', self.device_id)

    def turn_off(self):
        logger.debug('device "%s" turned off', self.device_id)

    def switch(self):
        logger.debug('device "%s" switched', self.device_id)
